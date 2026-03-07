"""
Document Parser for Grant Applications

DEVELOPER GUIDELINE: Resilient Markdown Parsing
Parses markdown files and extracts structured grant data. 
Markdown structure is often informal. Do not rely strictly on exact line numbers 
or rigid spacing. Use lenient Regular Expressions and fallback gracefully when 
sections are missing.
"""

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class DocumentParser:
    """Parser for extracting structured data from grant application documents."""

    def __init__(self, docs_folder: str):
        """
        Initialize the document parser.

        Args:
            docs_folder: Path to the docs folder containing markdown files
        """
        self.docs_folder = Path(docs_folder)
        if not self.docs_folder.exists():
            raise ValueError(f"Docs folder not found: {docs_folder}")

    def parse_markdown_file(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a markdown file and extract structured data.

        DEVELOPER GUIDELINE: Graceful Degradation
        If a specific field cannot be parsed, log a warning but do not halt
        the entire document parsing process unless it's a critical identifier.

        Args:
            file_path: Path to the markdown file

        Returns:
            Dictionary containing extracted structured data
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract frontmatter if present
        frontmatter = self._extract_frontmatter(content)

        # Extract main content
        main_content = self._remove_frontmatter(content)

        # Parse structured sections
        parsed_data = {
            "file_path": str(file_path),
            "frontmatter": frontmatter,
            "organization": self._extract_organization_info(main_content),
            "project": self._extract_project_info(main_content),
            "budget": self._extract_budget_info(main_content),
            "contact": self._extract_contact_info(main_content),
            "timeline": self._extract_timeline_info(main_content),
            "technical": self._extract_technical_info(main_content),
            "raw_content": main_content,
        }

        return parsed_data

    def _extract_frontmatter(self, content: str) -> Dict[str, Any]:
        """Extract YAML frontmatter from markdown."""
        frontmatter = {}
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                try:
                    import yaml

                    frontmatter = yaml.safe_load(parts[1]) or {}
                except ImportError:
                    logger.warning("PyYAML not available, skipping frontmatter parsing")
                except (IOError, yaml.YAMLError) as e:
                    logger.warning(f"Error parsing frontmatter: {e}")
        return frontmatter

    def _remove_frontmatter(self, content: str) -> str:
        """Remove frontmatter from content."""
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                return parts[2].strip()
        return content

    def _extract_organization_info(self, content: str) -> Dict[str, Any]:
        """Extract organization information."""
        org_info = {
            "name": self._extract_section_value(content, r"#\s+([^#\n]+)", "Organization Profile"),
            "mission": self._extract_subsection(content, "Mission and Vision"),
            "structure": self._extract_subsection(content, "Organizational Structure"),
            "history": self._extract_subsection(content, "Program History and Impact"),
            "budget": self._extract_budget_amount(content),
            "staff_size": self._extract_number(
                content, r"(\d+)\s*(?:staff|employees|team members)"
            ),
            "founded": self._extract_year(content, r"founded in (\d{4})"),
            "tax_status": self._extract_tax_status(content),
        }

        # Extract organization name from title or first heading
        if not org_info["name"]:
            title_match = re.search(r"^#\s+([^#\n]+)", content, re.MULTILINE)
            if title_match:
                org_info["name"] = title_match.group(1).strip()

        return org_info

    def _extract_project_info(self, content: str) -> Dict[str, Any]:
        """Extract project information."""
        project_info = {
            "title": self._extract_section_value(content, r"##\s+([^#\n]+)", "Overview"),
            "description": self._extract_subsection(content, "Overview"),
            "goals": self._extract_list_items(
                content, r"(?:goal|objective|purpose)[s]?:", case_insensitive=True
            ),
            "impact": self._extract_subsection(content, "Impact"),
            "target_audience": self._extract_target_audience(content),
            "activities": self._extract_activities(content),
            "outcomes": self._extract_outcomes(content),
        }

        return project_info

    def _extract_budget_info(self, content: str) -> Dict[str, Any]:
        """Extract budget information."""
        budget_info = {
            "total_requested": self._extract_budget_amount(content),
            "line_items": self._extract_budget_line_items(content),
            "matching_funds": self._extract_matching_funds(content),
            "breakdown": self._extract_budget_breakdown(content),
        }

        return budget_info

    def _extract_contact_info(self, content: str) -> Dict[str, Any]:
        """Extract contact information."""
        contact_info = {
            "name": self._extract_contact_name(content),
            "email": self._extract_email(content),
            "phone": self._extract_phone(content),
            "address": self._extract_address(content),
            "website": self._extract_website(content),
        }

        return contact_info

    def _extract_timeline_info(self, content: str) -> Dict[str, Any]:
        """Extract timeline and milestone information."""
        timeline_info = {
            "start_date": self._extract_date(
                content, r"start(?:ing|s)?\s*(?:date|on)?\s*:?\s*([A-Za-z]+\s+\d{1,2},?\s+\d{4})"
            ),
            "end_date": self._extract_date(
                content, r"end(?:ing|s)?\s*(?:date|on)?\s*:?\s*([A-Za-z]+\s+\d{1,2},?\s+\d{4})"
            ),
            "deadline": self._extract_date(
                content, r"deadline\s*:?\s*([A-Za-z]+\s+\d{1,2},?\s+\d{4})"
            ),
            "milestones": self._extract_milestones(content),
            "duration": self._extract_duration(content),
        }

        return timeline_info

    def _extract_technical_info(self, content: str) -> Dict[str, Any]:
        """Extract technical requirements and specifications."""
        technical_info = {
            "specifications": self._extract_subsection(content, "Technical Project Specifications"),
            "equipment": self._extract_equipment_list(content),
            "infrastructure": self._extract_subsection(content, "Infrastructure"),
            "requirements": self._extract_requirements(content),
        }

        return technical_info

    # Helper methods for extraction

    def _extract_section_value(
        self, content: str, pattern: str, section_name: str
    ) -> Optional[str]:
        """Extract value from a specific section."""
        section_match = re.search(
            rf"##\s+{re.escape(section_name)}.*?(?=##|$)", content, re.DOTALL | re.IGNORECASE
        )
        if section_match:
            section_content = section_match.group(0)
            match = re.search(pattern, section_content, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _extract_subsection(self, content: str, subsection_name: str) -> Optional[str]:
        """Extract content from a subsection."""
        pattern = rf"###\s+{re.escape(subsection_name)}.*?(?=###|##|$)"
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            text = match.group(0)
            # Remove the heading
            text = re.sub(rf"###\s+{re.escape(subsection_name)}", "", text, flags=re.IGNORECASE)
            return text.strip()
        return None

    def _extract_budget_amount(self, content: str) -> Optional[float]:
        """Extract budget amount from content."""
        # Look for patterns like "$75,000", "$75,000.00", "75,000 dollars"
        patterns = [
            r"\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)",
            r"(\d{1,3}(?:,\d{3})*)\s*(?:dollars?|USD)",
        ]
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                # Get the largest amount (likely the total)
                amounts = []
                for match in matches:
                    try:
                        amount = float(match.replace(",", ""))
                        amounts.append(amount)
                    except ValueError:
                        continue
                if amounts:
                    return max(amounts)
        return None

    def _extract_budget_line_items(self, content: str) -> List[Dict[str, Any]]:
        """Extract budget line items."""
        line_items = []

        # Look for patterns like "Item ($amount)" or "Item: $amount"
        pattern = r"([A-Za-z][^$]+?)\s*\(?\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\)?"
        matches = re.findall(pattern, content)

        for match in matches:
            item_name = match[0].strip()
            try:
                amount = float(match[1].replace(",", ""))
                line_items.append({"item": item_name, "amount": amount})
            except ValueError:
                continue

        return line_items

    def _extract_matching_funds(self, content: str) -> Optional[Dict[str, Any]]:
        """Extract matching funds information."""
        pattern = r"matching\s+funds?[:\s]+(\d+)%"
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return {"percentage": int(match.group(1))}
        return None

    def _extract_budget_breakdown(self, content: str) -> Dict[str, float]:
        """Extract budget breakdown by category."""
        breakdown = {}

        # Look for patterns like "Category ($amount)"
        pattern = r"([A-Za-z\s]+)\s*\(?\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\)?"
        matches = re.findall(pattern, content)

        for match in matches:
            category = match[0].strip()
            try:
                amount = float(match[1].replace(",", ""))
                breakdown[category] = amount
            except ValueError:
                continue

        return breakdown

    def _extract_contact_name(self, content: str) -> Optional[str]:
        """Extract contact person name."""
        patterns = [
            r"contact\s+person[:\s]+([A-Z][a-z]+\s+[A-Z][a-z]+)",
            r"primary\s+contact[:\s]+([A-Z][a-z]+\s+[A-Z][a-z]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _extract_email(self, content: str) -> Optional[str]:
        """Extract email address."""
        pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        match = re.search(pattern, content)
        if match:
            return match.group(0)
        return None

    def _extract_phone(self, content: str) -> Optional[str]:
        """Extract phone number."""
        patterns = [
            r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
            r"\+\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}",
        ]
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(0)
        return None

    def _extract_address(self, content: str) -> Optional[str]:
        """Extract address."""
        pattern = r"\d+\s+[A-Za-z0-9\s,]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Way|Circle|Cir)[^,\n]*(?:,\s*[A-Za-z\s]+,\s*[A-Z]{2}\s+\d{5})?"
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return match.group(0).strip()
        return None

    def _extract_website(self, content: str) -> Optional[str]:
        """Extract website URL."""
        pattern = r"https?://[^\s\)]+"
        match = re.search(pattern, content)
        if match:
            return match.group(0)
        return None

    def _extract_date(self, content: str, pattern: str) -> Optional[str]:
        """Extract date from content."""
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None

    def _extract_milestones(self, content: str) -> List[Dict[str, Any]]:
        """Extract project milestones."""
        milestones = []
        # Look for milestone patterns
        pattern = r"(?:milestone|phase|stage)\s+\d+[:\s]+([^.\n]+)"
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            milestones.append({"description": match.strip()})
        return milestones

    def _extract_duration(self, content: str) -> Optional[str]:
        """Extract project duration."""
        pattern = r"(\d+)\s*(?:month|year|week|day)s?"
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return match.group(0)
        return None

    def _extract_list_items(
        self, content: str, pattern: str, case_insensitive: bool = False
    ) -> List[str]:
        """Extract list items following a pattern."""
        items = []
        flags = re.IGNORECASE if case_insensitive else 0
        match = re.search(pattern, content, flags)
        if match:
            # Get the section after the match
            section_start = match.end()
            section = content[section_start : section_start + 500]
            # Extract bullet points
            bullet_pattern = r"[-*]\s+([^\n]+)"
            bullets = re.findall(bullet_pattern, section)
            items.extend([b.strip() for b in bullets])
        return items

    def _extract_target_audience(self, content: str) -> Optional[str]:
        """Extract target audience information."""
        pattern = r"target\s+audience[:\s]+([^.\n]+)"
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None

    def _extract_activities(self, content: str) -> List[str]:
        """Extract project activities."""
        activities = []
        # Look for activities section
        section = self._extract_subsection(content, "Activities")
        if section:
            bullet_pattern = r"[-*]\s+([^\n]+)"
            bullets = re.findall(bullet_pattern, section)
            activities.extend([b.strip() for b in bullets])
        return activities

    def _extract_outcomes(self, content: str) -> List[str]:
        """Extract expected outcomes."""
        outcomes = []
        # Look for outcomes section
        section = self._extract_subsection(content, "Outcomes")
        if not section:
            section = self._extract_subsection(content, "Expected Outcomes")
        if section:
            bullet_pattern = r"[-*]\s+([^\n]+)"
            bullets = re.findall(bullet_pattern, section)
            outcomes.extend([b.strip() for b in bullets])
        return outcomes

    def _extract_equipment_list(self, content: str) -> List[str]:
        """Extract equipment list."""
        equipment = []
        # Look for equipment section
        section = self._extract_subsection(content, "Equipment")
        if not section:
            section = self._extract_subsection(content, "Equipment Inventory")
        if section:
            bullet_pattern = r"[-*]\s+([^\n]+)"
            bullets = re.findall(bullet_pattern, section)
            equipment.extend([b.strip() for b in bullets])
        return equipment

    def _extract_requirements(self, content: str) -> List[str]:
        """Extract technical requirements."""
        requirements = []
        section = self._extract_subsection(content, "Requirements")
        if section:
            bullet_pattern = r"[-*]\s+([^\n]+)"
            bullets = re.findall(bullet_pattern, section)
            requirements.extend([b.strip() for b in bullets])
        return requirements

    def _extract_number(self, content: str, pattern: str) -> Optional[int]:
        """Extract a number from content."""
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            try:
                return int(match.group(1))
            except (ValueError, IndexError):
                pass
        return None

    def _extract_year(self, content: str, pattern: str) -> Optional[int]:
        """Extract a year from content."""
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            try:
                return int(match.group(1))
            except (ValueError, IndexError):
                pass
        return None

    def _extract_tax_status(self, content: str) -> Optional[str]:
        """Extract tax status (e.g., 501(c)(3))."""
        pattern = r"501\(c\)\s*\(\s*(\d+)\s*\)"
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return f"501(c)({match.group(1)})"
        return None
