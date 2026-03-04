"""
CLI Interface for 4Culture Grant Application Automation
Command-line interface that uses browser MCP tools for automation.
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from .automation_workflow import AutomationWorkflow
from .data_extractor import DataExtractor
from .form_mapper import FormMapper

# Import dashboard if available
try:
    from .grant_dashboard import GrantDashboard
except ImportError:
    GrantDashboard = None

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class GrantApplicationCLI:
    """CLI for grant application automation."""

    def __init__(self):
        """Initialize the CLI."""
        self.workflow: Optional[AutomationWorkflow] = None
        self.browser_connected = False

    def _get_mcp_browser_tools(self) -> Optional[Dict[str, Any]]:
        """
        Collect available MCP browser tools.
        This method attempts to access MCP browser tools if they're available.

        Returns:
            Dictionary of MCP tool functions or None if not available
        """
        try:
            import sys

            from .mcp_tools_helper import create_mcp_tools_dict_from_globals

            # Get the calling frame's globals (where MCP tools would be available)
            frame = sys._getframe(1)
            caller_globals = frame.f_globals

            # Try to collect tools from globals
            mcp_tools = create_mcp_tools_dict_from_globals(caller_globals)

            if mcp_tools:
                logger.info(f"Found {len(mcp_tools)} MCP browser tools")
                return mcp_tools
            else:
                logger.warning("MCP browser tools not found in environment")
                return None

        except Exception as e:
            logger.warning(f"Could not access MCP browser tools: {e}")
            return None

    def run(self, args):
        """Run the CLI with parsed arguments."""
        try:
            if args.command == "extract":
                self._run_extract(args)
            elif args.command == "automate":
                self._run_automate(args)
            elif args.command == "validate":
                self._run_validate(args)
            elif args.command == "dashboard":
                self._run_dashboard(args)
            else:
                logger.error(f"Unknown command: {args.command}")
                sys.exit(1)
        except Exception as e:
            logger.error(f"Error running CLI: {e}", exc_info=True)
            sys.exit(1)

    def _run_extract(self, args):
        """Run data extraction only."""
        logger.info("Running data extraction...")

        docs_folder = args.docs_folder or "docs"
        grant_name = args.grant_name

        extractor = DataExtractor(docs_folder)

        document_paths = None
        if args.doc:
            document_paths = [args.doc]

        grant_data = extractor.extract_grant_data(grant_name, document_paths)
        validation = extractor.validate_extracted_data(grant_data)

        print("\n=== Data Extraction Results ===")
        print(f"Grant: {grant_name}")
        print(f"Organization: {grant_data.get('organization', {}).get('name', 'N/A')}")
        print(f"Project: {grant_data.get('project', {}).get('title', 'N/A')}")
        print(f"Budget: ${grant_data.get('budget', {}).get('total_requested', 0):,.2f}")
        print(f"\nValidation: {'✅ Valid' if validation['valid'] else '❌ Invalid'}")

        if validation.get("missing_required"):
            print("\nMissing Required Fields:")
            for field in validation["missing_required"]:
                print(f"  - {field}")

        if validation.get("warnings"):
            print("\nWarnings:")
            for warning in validation["warnings"]:
                print(f"  - {warning}")

        if args.output:
            with open(args.output, "w") as f:
                json.dump(grant_data, f, indent=2)
            print(f"\nData saved to: {args.output}")

    def _run_validate(self, args):
        """Validate extracted data."""
        logger.info("Validating data...")

        docs_folder = args.docs_folder or "docs"
        grant_name = args.grant_name

        extractor = DataExtractor(docs_folder)
        grant_data = extractor.extract_grant_data(grant_name, args.doc and [args.doc] or None)
        validation = extractor.validate_extracted_data(grant_data)

        standardized = extractor.get_standardized_data(grant_data)
        mapper = FormMapper(args.config)
        mapped_fields = mapper.map_data_to_fields(standardized)
        field_validation = mapper.validate_mapped_fields(mapped_fields)

        print("\n=== Validation Results ===")
        print(f"Data Validation: {'✅ Valid' if validation['valid'] else '❌ Invalid'}")
        print(f"Field Validation: {'✅ Valid' if field_validation['valid'] else '❌ Invalid'}")

        if not validation["valid"] or not field_validation["valid"]:
            sys.exit(1)

    def _run_automate(self, args):
        """Run full automation workflow."""
        logger.info("Starting automation workflow...")

        # Initialize workflow
        docs_folder = args.docs_folder or "docs"
        config_path = args.config or "grant_config.yaml"

        # Collect MCP browser tools if available
        mcp_tools = self._get_mcp_browser_tools()

        workflow = AutomationWorkflow(
            username=args.username or os.getenv("4CULTURE_USERNAME", ""),
            password=args.password or os.getenv("4CULTURE_PASSWORD", ""),
            docs_folder=docs_folder,
            config_path=config_path,
            use_narratives=args.use_narratives,
            openai_api_key=args.openai_api_key,
            narrative_model=args.narrative_model,
            mcp_tools=mcp_tools,
        )

        if args.use_narratives:
            logger.info(
                "Narrative generation enabled - will convert bullet points to complete prose"
            )

            # Check if API key is provided
            api_key = args.openai_api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                logger.error(
                    "\n❌ ERROR: OpenAI API key required for narrative generation!\n"
                    "Please provide your API key using one of these methods:\n"
                    "  1. Environment variable: export OPENAI_API_KEY='your-api-key'\n"
                    "  2. CLI argument: --openai-api-key 'your-api-key'\n"
                    "\nGet your API key from: https://platform.openai.com/api-keys\n"
                )
                sys.exit(1)

        self.workflow = workflow

        # Extract and map data
        logger.info("Extracting and mapping data...")

        document_paths = None
        if args.doc:
            document_paths = [args.doc]

        result = workflow.run_automation(
            grant_name=args.grant_name, document_paths=document_paths, dry_run=args.dry_run
        )

        if args.dry_run:
            print("\n=== Dry Run Results ===")
            print("Data extracted and mapped, but form not filled.")
            print(f"\nFields mapped: {len(result.get('fields_mapped', []))}")
            for field in result.get("fields_mapped", [])[:10]:  # Show first 10
                print(f"  - {field.get('field_name')}: {str(field.get('value', ''))[:50]}...")
            return

        # Generate report
        report_path = (
            args.report or f"grant_application_report_{args.grant_name.replace(' ', '_')}.md"
        )
        report = workflow.generate_report(result, report_path)
        print("\n=== Automation Report ===")
        print(report)

        if not result.get("success"):
            logger.error("Automation failed. Check report for details.")
            sys.exit(1)

        print("\n✅ Automation completed successfully!")
        print(f"Report saved to: {report_path}")

        if mcp_tools:
            print("\n✅ Browser automation completed using MCP tools")
            if result.get("draft_saved"):
                print(f"Draft URL: {result.get('draft_url', 'N/A')}")
        else:
            print("\n⚠️  MCP browser tools not available - browser automation was skipped")
            print("The workflow has prepared all data and field mappings.")
            print("Use the field instructions in the report to fill the form manually.")

        # Cleanup: close browser if MCP tools were used
        if mcp_tools and workflow.automator:
            try:
                workflow.automator.close()
            except Exception as e:
                logger.warning(f"Error closing browser: {e}")

        # Close database connection
        if workflow.db:
            try:
                workflow.db.close()
            except Exception as e:
                logger.warning(f"Error closing database: {e}")

    def _run_dashboard(self, args):
        """Generate HTML dashboard."""
        if not GrantDashboard:
            logger.error("GrantDashboard not available")
            sys.exit(1)

        logger.info("Generating grant planning dashboard...")

        dashboard = GrantDashboard()
        output_path = dashboard.generate_dashboard()

        print("\n✅ Dashboard generated successfully!")
        print(f"   Location: {output_path}")
        print(f"   Open in browser: file://{Path(output_path).absolute()}")
        print("\n   The dashboard shows:")
        print("   - All planned grant applications")
        print("   - Applications in progress with completion status")
        print("   - Submitted and completed applications")
        print("   - Grants organized by deadline month")
        print("   - Priority-based view for strategic planning")


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="4Culture Grant Application Automation CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract data only
  python3 -m grant_automation_cli.cli extract --grant "Moving Stories" --doc docs/02-green-stem-expo-technical.md
  
  # Validate extracted data
  python3 -m grant_automation_cli.cli validate --grant "Moving Stories"
  
  # Run automation (dry run)
  python3 -m grant_automation_cli.cli automate --grant "Moving Stories" --dry-run
  
  # Run full automation
  python3 -m grant_automation_cli.cli automate --grant "Moving Stories" --username YOUR_USERNAME --password "YOUR_PASSWORD"

Note: For developers needing fine-grained control over individual steps, use the SDK CLI:
  python3 -m grant_automation_cli.sdk_cli --help
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Extract command
    extract_parser = subparsers.add_parser("extract", help="Extract data from documents")
    extract_parser.add_argument("--grant-name", required=True, help="Name of the grant")
    extract_parser.add_argument("--doc", help="Specific document path to use")
    extract_parser.add_argument("--docs-folder", default="docs", help="Path to docs folder")
    extract_parser.add_argument("--output", help="Output file for extracted data (JSON)")

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate extracted data")
    validate_parser.add_argument("--grant-name", required=True, help="Name of the grant")
    validate_parser.add_argument("--doc", help="Specific document path to use")
    validate_parser.add_argument("--docs-folder", default="docs", help="Path to docs folder")
    validate_parser.add_argument("--config", help="Path to grant configuration file")

    # Automate command
    automate_parser = subparsers.add_parser("automate", help="Run full automation workflow")
    automate_parser.add_argument("--grant-name", required=True, help="Name of the grant")
    automate_parser.add_argument("--doc", help="Specific document path to use")
    automate_parser.add_argument("--docs-folder", default="docs", help="Path to docs folder")
    automate_parser.add_argument("--config", help="Path to grant configuration file")
    automate_parser.add_argument(
        "--username", help="4Culture username (optional; set 4CULTURE_USERNAME env)"
    )
    automate_parser.add_argument("--password", help="4Culture password")
    automate_parser.add_argument(
        "--dry-run", action="store_true", help="Extract data but don't fill form"
    )
    automate_parser.add_argument("--report", help="Path to save completion report")
    automate_parser.add_argument(
        "--use-narratives",
        action="store_true",
        help="Use OpenAI to generate complete narratives (no bullet points)",
    )
    automate_parser.add_argument("--openai-api-key", help="OpenAI API key for narrative generation")
    automate_parser.add_argument(
        "--narrative-model", help="OpenAI model to use for narratives (default: gpt-4)"
    )

    # Dashboard command
    dashboard_parser = subparsers.add_parser(
        "dashboard", help="Generate HTML grant planning dashboard"
    )
    dashboard_parser.add_argument("--db", default="grants.db", help="Path to grant database")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    cli = GrantApplicationCLI()
    cli.run(args)


if __name__ == "__main__":
    main()
