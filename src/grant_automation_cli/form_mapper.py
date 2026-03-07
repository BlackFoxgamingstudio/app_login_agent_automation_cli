"""
Form Field Mapper for Grant Applications

DEVELOPER GUIDELINE: Loose Coupling
Maps extracted data to 4Culture form fields.
This acts as an Anti-Corruption Layer between our internal data model 
and the target website's specific HTML form names. Do not hardcode form field 
names here; load them from configuration files when possible.
"""

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
except ImportError:
    yaml = None

logger = logging.getLogger(__name__)

# Import narrative generator if available
try:
    from .narrative_generator import NarrativeGenerator
except ImportError:
    NarrativeGenerator = None


class FormMapper:
    """Maps extracted grant data to form fields."""

    def __init__(
        self,
        config_path: Optional[str] = None,
        narrative_generator: Optional[Any] = None,
        use_narratives: bool = False,
        narrative_config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the form mapper.

        Args:
            config_path: Path to field mapping configuration file
            narrative_generator: Optional NarrativeGenerator instance
            use_narratives: Whether to use narrative generation
            narrative_config: Configuration for narrative generation
        """
        self.config_path = config_path
        self.field_mappings: Dict[str, Any] = {}
        self.narrative_generator = narrative_generator
        self.use_narratives = use_narratives and narrative_generator is not None
        self.narrative_config = narrative_config or {}
        self.narrative_cache: Dict[str, str] = {}  # Cache generated narratives

        if config_path and Path(config_path).exists():
            self.load_mappings(config_path)
        else:
            # Default mappings
            self.field_mappings = self._get_default_mappings()

        # Load narrative config from mappings if available
        if yaml and config_path and Path(config_path).exists():
            try:
                with open(config_path, "r") as f:
                    config = yaml.safe_load(f)
                    narrative_config_from_file = config.get("narrative_generation", {})
                    if narrative_config_from_file:
                        self.narrative_config = {
                            **self.narrative_config,
                            **narrative_config_from_file,
                        }
                        if not self.use_narratives:
                            self.use_narratives = narrative_config_from_file.get("enabled", False)
            except (IOError, yaml.YAMLError) as e:
                logger.warning(f"Error loading narrative config: {e}")

    def load_mappings(self, config_path: str):
        """Load field mappings from configuration file."""
        if yaml is None:
            logger.warning("PyYAML not available, using default mappings")
            self.field_mappings = self._get_default_mappings()
            return

        try:
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
                self.field_mappings = config.get("field_mappings", {})
        except (IOError, yaml.YAMLError) as e:
            logger.error(f"Error loading mappings from {config_path}: {e}")
            self.field_mappings = self._get_default_mappings()

    def _get_default_mappings(self) -> Dict[str, Any]:
        """Get default field mappings."""
        return {
            "organization_name": {
                "field_type": "text",
                "field_name": "organization_name",
                "required": True,
            },
            "organization_mission": {
                "field_type": "textarea",
                "field_name": "mission_statement",
                "required": True,
            },
            "organization_tax_status": {
                "field_type": "select",
                "field_name": "tax_status",
                "required": True,
                "options": ["501(c)(3)", "501(c)(4)", "Other"],
            },
            "project_title": {
                "field_type": "text",
                "field_name": "project_title",
                "required": True,
            },
            "project_description": {
                "field_type": "textarea",
                "field_name": "project_description",
                "required": True,
            },
            "project_goals": {
                "field_type": "textarea",
                "field_name": "project_goals",
                "required": False,
            },
            "project_impact": {
                "field_type": "textarea",
                "field_name": "project_impact",
                "required": False,
            },
            "budget_total": {
                "field_type": "number",
                "field_name": "budget_total",
                "required": True,
            },
            "contact_name": {"field_type": "text", "field_name": "contact_name", "required": True},
            "contact_email": {
                "field_type": "email",
                "field_name": "contact_email",
                "required": True,
            },
            "contact_phone": {
                "field_type": "tel",
                "field_name": "contact_phone",
                "required": False,
            },
            "contact_address": {
                "field_type": "textarea",
                "field_name": "contact_address",
                "required": False,
            },
        }

    def map_data_to_fields(
        self,
        standardized_data: Dict[str, Any],
        grant_name: Optional[str] = None,
        grant_data: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Map standardized data to form fields.

        Args:
            standardized_data: Standardized data dictionary
            grant_name: Optional grant name for narrative generation
            grant_data: Optional full grant data for narrative generation

        Returns:
            List of field mapping dictionaries ready for form filling
        """
        mapped_fields = []

        for data_key, data_value in standardized_data.items():
            if data_key in self.field_mappings:
                mapping = self.field_mappings[data_key].copy()
                field_name = mapping.get("field_name")

                # Check if narrative generation should be used for this field
                # Pass both field_name and data_key to help with mapping lookup
                should_narrate = self.use_narratives and self._should_use_narrative(
                    field_name, data_value, data_key
                )
                if should_narrate:
                    # Try to generate narrative
                    narrative = self._generate_narrative_for_field(
                        field_name, data_key, grant_name, grant_data, standardized_data
                    )
                    if narrative:
                        mapping["value"] = narrative
                        mapping["narrative_generated"] = True
                        logger.info(f"Generated narrative for field: {field_name}")
                    else:
                        # Fallback to original value
                        mapping["value"] = self._format_value(data_value, mapping.get("field_type"))
                        mapping["narrative_generated"] = False
                        logger.warning(
                            f"Narrative generation failed for {field_name}, using original value"
                        )
                else:
                    mapping["value"] = self._format_value(data_value, mapping.get("field_type"))
                    mapping["narrative_generated"] = False

                mapped_fields.append(mapping)

        return mapped_fields

    def _should_use_narrative(
        self, field_name: str, data_value: Any, data_key: Optional[str] = None
    ) -> bool:
        """
        Check if narrative generation should be used for this field.

        Args:
            field_name: Form field name
            data_value: Data value to check
            data_key: Optional data key for finding mapping
        """
        if not self.use_narratives or not self.narrative_generator:
            return False

        # Check field-specific configuration
        fields_config = self.narrative_config.get("fields_to_narrate", {})
        if isinstance(fields_config, dict):
            field_config = fields_config.get(field_name, {})
            if isinstance(field_config, dict):
                if not field_config.get("enabled", True):
                    return False
        elif isinstance(fields_config, list):
            if field_name not in fields_config:
                return False

        # Find the mapping - try by field_name first, then by data_key
        mapping = None
        if data_key and data_key in self.field_mappings:
            mapping = self.field_mappings[data_key]
        else:
            # Find by field_name
            for key, map_config in self.field_mappings.items():
                if map_config.get("field_name") == field_name:
                    mapping = map_config
                    break

        if not mapping:
            return False

        field_type = mapping.get("field_type", "")
        if field_type not in ["textarea", "text"]:
            return False

        # Check if value contains bullet points or is structured (list-like)
        if isinstance(data_value, list):
            return True
        if isinstance(data_value, str):
            # Check for bullet points, numbered lists, or very short text
            if any(marker in data_value for marker in ["- ", "* ", "• ", "\n-", "\n*", "\n•"]):
                return True
            if re.match(r"^\d+\.\s+", data_value, re.MULTILINE):
                return True
            # If text is very short, might benefit from narrative expansion
            if len(data_value) < 200:
                return True

        return False

    def _generate_narrative_for_field(
        self,
        field_name: str,
        data_key: str,
        grant_name: Optional[str],
        grant_data: Optional[Dict[str, Any]],
        standardized_data: Dict[str, Any],
    ) -> Optional[str]:
        """Generate narrative for a specific field."""
        # Check cache first
        cache_key = f"{field_name}:{data_key}"
        if cache_key in self.narrative_cache:
            return self.narrative_cache[cache_key]

        if not self.narrative_generator or not grant_name or not grant_data:
            return None

        try:
            # Map field names to narrative generator types
            field_to_narrative_type = {
                "project_description": "project_description",
                "mission_statement": "project_description",  # Can use project description template
                "project_goals": "goals",
                "project_impact": "impact",
                "expected_outcomes": "impact",  # Can use impact template
                "project_activities": "activities",
                "target_audience": "project_description",  # Can use project description template
                "budget_breakdown": "budget",
                "technical_requirements": "technical",
                "equipment_needed": "technical",  # Can use technical template
            }

            narrative_type = field_to_narrative_type.get(field_name)
            if narrative_type:
                narrative = self.narrative_generator.generate_narrative(
                    narrative_type, grant_name, grant_data
                )
                if narrative:
                    self.narrative_cache[cache_key] = narrative
                    return narrative
        except RuntimeError as e:
            logger.error(f"Error generating narrative for {field_name}: {e}")

        return None

    def _format_value(self, value: Any, field_type: str) -> str:
        """Format value based on field type."""
        if value is None:
            return ""

        if field_type == "number":
            if isinstance(value, (int, float)):
                return str(value)
            return str(value) if value else "0"

        if field_type == "textarea":
            if isinstance(value, list):
                return "\n".join(str(v) for v in value)
            return str(value)

        if field_type == "select":
            return str(value)

        # Default: convert to string
        return str(value) if value else ""

    def get_field_by_name(
        self, field_name: str, mapped_fields: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Get a mapped field by its field name."""
        for field in mapped_fields:
            if field.get("field_name") == field_name:
                return field
        return None

    def validate_mapped_fields(self, mapped_fields: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate mapped fields before form filling.

        Args:
            mapped_fields: List of mapped field dictionaries

        Returns:
            Validation result
        """
        validation_result = {
            "valid": True,
            "missing_required": [],
            "invalid_fields": [],
            "warnings": [],
        }

        # Check required fields
        for field in mapped_fields:
            if field.get("required", False):
                value = field.get("value", "")
                if not value or value.strip() == "":
                    validation_result["missing_required"].append(field.get("field_name"))
                    validation_result["valid"] = False

        # Validate field types
        for field in mapped_fields:
            field_type = field.get("field_type")
            value = field.get("value", "")

            if field_type == "email" and value:
                if "@" not in value:
                    validation_result["invalid_fields"].append(
                        f"{field.get('field_name')}: invalid email"
                    )
                    validation_result["valid"] = False

            if field_type == "number" and value:
                try:
                    float(value)
                except ValueError:
                    validation_result["invalid_fields"].append(
                        f"{field.get('field_name')}: invalid number"
                    )
                    validation_result["valid"] = False

        return validation_result

    def handle_conditional_fields(
        self, mapped_fields: List[Dict[str, Any]], form_state: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Handle conditional fields that appear based on other field values.

        Args:
            mapped_fields: List of mapped fields
            form_state: Current form state (field values)

        Returns:
            Updated list of mapped fields including conditional fields
        """
        # This would be extended based on actual form structure
        # For now, return fields as-is
        return mapped_fields

    def create_field_filling_instructions(
        self, mapped_fields: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Create instructions for filling each field.

        Args:
            mapped_fields: List of mapped fields

        Returns:
            List of field filling instructions
        """
        instructions = []

        for field in mapped_fields:
            instruction = {
                "action": self._get_action_for_field_type(field.get("field_type")),
                "field_name": field.get("field_name"),
                "value": field.get("value"),
                "field_type": field.get("field_type"),
                "required": field.get("required", False),
            }
            instructions.append(instruction)

        return instructions

    def _get_action_for_field_type(self, field_type: str) -> str:
        """Get the action type for a field type."""
        action_map = {
            "text": "type",
            "textarea": "type",
            "email": "type",
            "tel": "type",
            "number": "type",
            "select": "select",
            "checkbox": "click",
            "radio": "click",
            "file": "upload",
        }
        return action_map.get(field_type, "type")
