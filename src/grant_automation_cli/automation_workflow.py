"""
Automation Workflow for 4Culture Grant Applications

DEVELOPER GUIDELINE: Orchestration Layer
This module orchestrates the entire automation pipeline. It should not contain
low-level scraping or parsing logic itself. It must act strictly as a Director,
coordinating the DataExtractor, Automator, and Dashboard generation.
"""

import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .application_automator import ApplicationAutomator
from .data_extractor import DataExtractor
from .form_mapper import FormMapper

# Import narrative generator if available
try:
    from .narrative_generator import NarrativeGenerator
except ImportError:
    NarrativeGenerator = None

# Import database if available
try:
    from .grant_database import GrantDatabase
except ImportError:
    GrantDatabase = None

logger = logging.getLogger(__name__)


class AutomationWorkflow:
    """Orchestrates the complete grant application automation workflow."""

    def __init__(
        self,
        username: str,
        password: str,
        docs_folder: str,
        config_path: Optional[str] = None,
        use_narratives: bool = False,
        openai_api_key: Optional[str] = None,
        narrative_model: Optional[str] = None,
        mcp_tools: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the automation workflow.

        Args:
            username: 4Culture login username
            password: 4Culture login password
            docs_folder: Path to docs folder containing grant documents
            config_path: Optional path to grant configuration file
            use_narratives: Whether to use narrative generation
            openai_api_key: Optional OpenAI API key
            narrative_model: Optional model name for narrative generation
        """
        self.username = username
        self.password = password
        self.docs_folder = docs_folder
        self.config_path = config_path
        self.use_narratives = use_narratives

        # Load narrative config from file if available
        narrative_config = {}
        if config_path and Path(config_path).exists():
            try:
                import yaml

                with open(config_path, "r") as f:
                    config = yaml.safe_load(f)
                    narrative_config = config.get("narrative_generation", {})
                    if narrative_config and not use_narratives:
                        use_narratives = narrative_config.get("enabled", False)
            except (IOError, yaml.YAMLError) as e:
                logger.warning(f"Error loading narrative config: {e}")

        # Initialize narrative generator if enabled
        self.narrative_generator = None
        if use_narratives and NarrativeGenerator:
            try:
                # Get API key from multiple sources (priority order)
                api_key = (
                    openai_api_key  # CLI argument (highest priority)
                    or narrative_config.get("openai_api_key")  # Config file
                    or os.getenv("OPENAI_API_KEY")  # Environment variable
                )

                if not api_key or api_key == "null" or api_key == "":
                    raise ValueError(
                        "OpenAI API key is required for narrative generation. "
                        "Please provide it via:\n"
                        "  1. Environment variable: export OPENAI_API_KEY='your-key'\n"
                        "  2. CLI argument: --openai-api-key 'your-key'\n"
                        "  3. Or disable narrative generation: remove --use-narratives flag"
                    )

                model = narrative_model or narrative_config.get("model", "gpt-4")
                temperature = narrative_config.get("temperature", 0.7)
                max_tokens = narrative_config.get("max_tokens", 2000)

                self.narrative_generator = NarrativeGenerator(
                    api_key=api_key, model=model, temperature=temperature, max_tokens=max_tokens
                )
                logger.info(f"Narrative generator initialized with model: {model}")
            except ValueError as e:
                logger.error(str(e))
                raise  # Re-raise ValueError so user knows they need to provide API key
            except (RuntimeError, IOError) as e:
                logger.warning(
                    f"Failed to initialize narrative generator: {e}. Continuing without narratives."
                )
                self.use_narratives = False

        # Initialize components
        self.data_extractor = DataExtractor(docs_folder)
        self.form_mapper = FormMapper(
            config_path=config_path,
            narrative_generator=self.narrative_generator,
            use_narratives=self.use_narratives,
            narrative_config=narrative_config,
        )
        self.automator = ApplicationAutomator(username, password, mcp_tools=mcp_tools)
        self.mcp_tools = mcp_tools

        # Initialize database for tracking
        self.db = None
        if GrantDatabase:
            try:
                self.db = GrantDatabase()
                logger.info("Grant database initialized for tracking")
            except (RuntimeError, IOError) as e:
                logger.warning(f"Could not initialize grant database: {e}")

        # Workflow state
        self.workflow_state: Dict[str, Any] = {
            "current_step": None,
            "errors": [],
            "warnings": [],
            "screenshots": [],
            "narratives_generated": 0,
        }

    def run_automation(
        self, grant_name: str, document_paths: Optional[List[str]] = None, dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Run the complete automation workflow.

        DEVELOPER GUIDELINE: Error Boundaries
        The workflow must catch and record all sub-component exceptions to generate 
        a meaningful final report, ensuring the CLI doesn't exit abruptly without 
        saving the state of successful partial steps.

        Args:
            grant_name: Name of the grant to apply for
            document_paths: Optional list of specific document paths to use
            dry_run: If True, extract data but don't fill form

        Returns:
            Result dictionary with automation status and details
        """
        result = {
            "success": False,
            "grant_name": grant_name,
            "steps_completed": [],
            "steps_failed": [],
            "data_extracted": None,
            "fields_mapped": None,
            "fields_filled": [],
            "fields_failed": [],
            "draft_saved": False,
            "draft_url": None,
            "errors": [],
            "warnings": [],
            "screenshots": [],
        }

        try:
            # Step 1: Extract data from documents
            logger.info(f"Step 1: Extracting data for grant: {grant_name}")
            self.workflow_state["current_step"] = "data_extraction"

            grant_data = self.data_extractor.extract_grant_data(grant_name, document_paths)
            validation = self.data_extractor.validate_extracted_data(grant_data)

            result["data_extracted"] = grant_data
            result["warnings"].extend(validation.get("warnings", []))

            if not validation["valid"]:
                result["errors"].extend(
                    [f"Missing required field: {f}" for f in validation["missing_required"]]
                )
                if not dry_run:
                    logger.error("Required fields missing, cannot proceed")
                    return result

            result["steps_completed"].append("data_extraction")

            # Step 2: Standardize and map data
            logger.info("Step 2: Standardizing and mapping data to form fields")
            self.workflow_state["current_step"] = "data_mapping"

            standardized_data = self.data_extractor.get_standardized_data(grant_data)

            # Map data to fields (with narrative generation if enabled)
            mapped_fields = self.form_mapper.map_data_to_fields(
                standardized_data, grant_name=grant_name, grant_data=grant_data
            )

            # Count narratives generated
            narratives_generated = sum(
                1 for f in mapped_fields if f.get("narrative_generated", False)
            )
            self.workflow_state["narratives_generated"] = narratives_generated
            if narratives_generated > 0:
                logger.info(f"Generated {narratives_generated} narratives for form fields")

            field_validation = self.form_mapper.validate_mapped_fields(mapped_fields)

            result["fields_mapped"] = mapped_fields

            if not field_validation["valid"]:
                result["errors"].extend(
                    [f"Invalid field: {f}" for f in field_validation["invalid_fields"]]
                )
                result["warnings"].extend(
                    [
                        f"Missing optional field: {f}"
                        for f in field_validation.get("missing_required", [])
                    ]
                )

            result["steps_completed"].append("data_mapping")

            # Update database with grant information
            if self.db:
                try:
                    self._update_database(grant_name, grant_data, mapped_fields, result)
                except (RuntimeError, IOError) as e:
                    logger.warning(f"Error updating database: {e}")

            if dry_run:
                logger.info("Dry run mode: Data extracted and mapped, but not filling form")
                result["success"] = True
                return result

            # Step 3: Browser automation - Login
            logger.info("Step 3: Logging in to 4Culture portal")
            self.workflow_state["current_step"] = "login"

            if self.mcp_tools:
                login_success = self.automator.login()
                if login_success:
                    result["steps_completed"].append("login")
                else:
                    result["errors"].append("Failed to log in to 4Culture portal")
                    result["steps_failed"].append("login")
                    logger.error("Login failed, cannot proceed")
                    return result
            else:
                logger.warning("No MCP tools available, skipping browser automation")
                result["warnings"].append("MCP tools not available - browser automation skipped")
                result["steps_completed"].append("login")

            # Step 4: Navigate to grant application
            logger.info(f"Step 4: Navigating to grant application: {grant_name}")
            self.workflow_state["current_step"] = "navigation"

            if self.mcp_tools:
                # Navigation is handled in start_new_application
                result["steps_completed"].append("navigation")
            else:
                result["steps_completed"].append("navigation")

            # Step 5: Start new application
            logger.info("Step 5: Starting new application")
            self.workflow_state["current_step"] = "start_application"

            if self.mcp_tools:
                app_started = self.automator.start_new_application(grant_name)
                if app_started:
                    result["steps_completed"].append("start_application")
                else:
                    result["errors"].append(f"Failed to start application for {grant_name}")
                    result["steps_failed"].append("start_application")
                    logger.error("Failed to start application")
                    return result
            else:
                result["steps_completed"].append("start_application")

            # Step 6: Fill form fields
            logger.info("Step 6: Filling form fields")
            self.workflow_state["current_step"] = "fill_form"

            field_instructions = self.form_mapper.create_field_filling_instructions(mapped_fields)

            if self.mcp_tools:
                # Extract form structure first
                form_structure = self.automator.extract_form_structure()
                logger.info(
                    f"Form structure extracted: {len(form_structure.get('fields', []))} fields found"
                )

                # Fill all fields
                fill_result = self.automator.fill_form_fields(field_instructions)

                result["fields_filled"] = fill_result.get("filled_fields", [])
                result["fields_failed"] = fill_result.get("failed_fields", [])

                if fill_result.get("errors"):
                    result["errors"].extend(fill_result["errors"])

                # Check for validation errors
                validation_errors = self.automator.handle_form_validation_errors()
                if validation_errors:
                    result["errors"].extend([f"Validation error: {e}" for e in validation_errors])
                    logger.warning(f"Form validation errors found: {validation_errors}")

                if fill_result.get("success"):
                    result["steps_completed"].append("fill_form")
                else:
                    result["steps_failed"].append("fill_form")
                    logger.warning("Some fields failed to fill")
            else:
                result["fields_mapped"] = field_instructions
                result["steps_completed"].append("fill_form")

            # Step 7: Save draft
            logger.info("Step 7: Saving draft application")
            self.workflow_state["current_step"] = "save_draft"

            if self.mcp_tools:
                save_result = self.automator.save_draft()
                if save_result.get("success"):
                    result["draft_saved"] = True
                    result["draft_url"] = save_result.get("draft_url")
                    result["steps_completed"].append("save_draft")
                else:
                    result["errors"].append(f"Failed to save draft: {save_result.get('message')}")
                    result["steps_failed"].append("save_draft")
            else:
                result["steps_completed"].append("save_draft")
                result["draft_saved"] = True

            result["success"] = True
            logger.info("Automation workflow completed successfully")

            # Final database update
            if self.db:
                try:
                    self._update_database_final(grant_name, result)
                except (RuntimeError, IOError) as e:
                    logger.warning(f"Error in final database update: {e}")

        except RuntimeError as e:
            logger.error(f"Error in automation workflow: {e}", exc_info=True)
            result["errors"].append(str(e))
            result["steps_failed"].append(self.workflow_state.get("current_step", "unknown"))

        return result

    def _update_database(
        self,
        grant_name: str,
        grant_data: Dict[str, Any],
        mapped_fields: List[Dict[str, Any]],
        result: Dict[str, Any],
    ):
        """Update database with grant information."""
        if not self.db:
            return

        # Check if grant exists
        grants = self.db.get_grants_by_status()
        existing_grant = next((g for g in grants if g.get("name") == grant_name), None)

        if existing_grant:
            grant_id = existing_grant["id"]
        else:
            # Add new grant
            grant_data_db = {
                "name": grant_name,
                "identifier": grant_name.lower().replace(" ", "-").replace(":", "")[:50],
                "deadline": grant_data.get("timeline", {}).get("deadline", "Not specified"),
                "status": "in_progress",
                "amount_requested": grant_data.get("budget", {}).get("total_requested"),
                "organization_name": grant_data.get("organization", {}).get("name"),
                "project_title": grant_data.get("project", {}).get("title"),
                "description": grant_data.get("project", {}).get("description", "")[:500],
                "priority": 5,
            }
            grant_id = self.db.add_grant(grant_data_db)

        # Update status
        progress = 0
        if result.get("steps_completed"):
            completed_steps = len(result["steps_completed"])
            total_steps = 7  # Approximate total steps
            progress = int((completed_steps / total_steps) * 100)

        current_step = self.workflow_state.get("current_step", "data_extraction")

        self.db.update_grant_status(
            grant_id,
            "in_progress",
            progress_percentage=progress,
            current_step=current_step,
            data_extracted=True,
            narrative_generated=self.workflow_state.get("narratives_generated", 0) > 0,
            form_filled=len(result.get("fields_filled", [])) > 0,
            draft_saved=result.get("draft_saved", False),
            draft_url=result.get("draft_url"),
            report_path=result.get("report_path"),
            errors=result.get("errors", []),
            warnings=result.get("warnings", []),
        )

    def _update_database_final(self, grant_name: str, result: Dict[str, Any]):
        """Final database update after workflow completion."""
        if not self.db:
            return

        grants = self.db.get_grants_by_status()
        existing_grant = next((g for g in grants if g.get("name") == grant_name), None)

        if existing_grant:
            status = "submitted" if result.get("draft_saved") else "in_progress"
            self.db.update_grant_status(
                existing_grant["id"],
                status,
                progress_percentage=100 if result.get("success") else 50,
                submitted=result.get("draft_saved", False),
                submitted_date=time.strftime("%Y-%m-%d") if result.get("draft_saved") else None,
            )

    def generate_report(self, result: Dict[str, Any], output_path: Optional[str] = None) -> str:
        """
        Generate a completion report.

        Args:
            result: Automation result dictionary
            output_path: Optional path to save report

        Returns:
            Report text
        """
        report_lines = [
            "# 4Culture Grant Application Automation Report",
            "",
            f"**Grant:** {result.get('grant_name', 'Unknown')}",
            f"**Status:** {'✅ Success' if result.get('success') else '❌ Failed'}",
            "",
            "## Steps Completed",
        ]

        for step in result.get("steps_completed", []):
            report_lines.append(f"- ✅ {step}")

        for step in result.get("steps_failed", []):
            report_lines.append(f"- ❌ {step}")

        report_lines.extend(
            [
                "",
                "## Data Extraction",
            ]
        )

        if result.get("data_extracted"):
            data = result["data_extracted"]
            org = data.get("organization", {})
            report_lines.extend(
                [
                    f"- Organization: {org.get('name', 'N/A')}",
                    f"- Project: {data.get('project', {}).get('title', 'N/A')}",
                    f"- Budget: ${data.get('budget', {}).get('total_requested', 0):,.2f}",
                ]
            )

        report_lines.extend(
            [
                "",
                "## Fields Mapped",
                f"Total fields: {len(result.get('fields_mapped', []))}",
            ]
        )

        # Add narrative generation info if used
        narratives_generated = self.workflow_state.get("narratives_generated", 0)
        if narratives_generated > 0:
            report_lines.extend(
                [
                    "",
                    f"**Narratives Generated:** {narratives_generated} fields converted to complete prose",
                ]
            )
            narrative_fields = [
                f for f in result.get("fields_mapped", []) if f.get("narrative_generated", False)
            ]
            if narrative_fields:
                report_lines.append("")
                report_lines.append("Fields with generated narratives:")
                for field in narrative_fields:
                    report_lines.append(f"  - ✅ {field.get('field_name')} (narrative generated)")

        if result.get("fields_filled"):
            report_lines.extend(
                [
                    "",
                    "## Fields Filled Successfully",
                ]
            )
            for field in result["fields_filled"]:
                report_lines.append(f"- ✅ {field}")

        if result.get("fields_failed"):
            report_lines.extend(
                [
                    "",
                    "## Fields Failed",
                ]
            )
            for field in result["fields_failed"]:
                report_lines.append(f"- ❌ {field}")

        if result.get("warnings"):
            report_lines.extend(
                [
                    "",
                    "## Warnings",
                ]
            )
            for warning in result["warnings"]:
                report_lines.append(f"- ⚠️ {warning}")

        if result.get("errors"):
            report_lines.extend(
                [
                    "",
                    "## Errors",
                ]
            )
            for error in result["errors"]:
                report_lines.append(f"- ❌ {error}")

        if result.get("draft_saved"):
            report_lines.extend(
                [
                    "",
                    "## Draft Application",
                    "- Status: Saved",
                    f"- URL: {result.get('draft_url', 'N/A')}",
                ]
            )

        report_text = "\n".join(report_lines)

        if output_path:
            with open(output_path, "w") as f:
                f.write(report_text)
            logger.info(f"Report saved to: {output_path}")

        return report_text

    def save_workflow_state(self, output_path: str):
        """Save workflow state to file."""
        state = {
            "workflow_state": self.workflow_state,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        with open(output_path, "w") as f:
            json.dump(state, f, indent=2)

        logger.info(f"Workflow state saved to: {output_path}")
