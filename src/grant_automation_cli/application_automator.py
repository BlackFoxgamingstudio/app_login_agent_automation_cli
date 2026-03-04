"""
Application Automator for 4Culture Grant Applications
Extends GrantScraper with form automation capabilities using browser automation.
"""

import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .mcp_browser_integration import MCPBrowserIntegration
from .scraper import GrantScraper

logger = logging.getLogger(__name__)


class ApplicationAutomator(GrantScraper):
    """Extended scraper with form automation capabilities."""

    def __init__(self, username: str, password: str, mcp_tools: Optional[Dict[str, Any]] = None):
        """
        Initialize the application automator.

        Args:
            username: 4Culture login username
            password: 4Culture login password
            mcp_tools: Optional dictionary of MCP browser tool functions
        """
        super().__init__(username, password)
        self.username = username
        self.password = password
        self.current_url: Optional[str] = None
        self.screenshots_dir = Path("agents/grant_scraper/screenshots")
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)

        # Initialize MCP browser integration
        self.browser = MCPBrowserIntegration(use_multi_session=False)
        if mcp_tools:
            # #region agent log
            import json
            import time as time_module

            try:
                with open("/tmp/grant_automation_debug.log", "a") as f:
                    f.write(
                        json.dumps(
                            {
                                "sessionId": "debug-session",
                                "runId": "post-fix-v3",
                                "hypothesisId": "H2",
                                "location": "application_automator.py:__init__:before_init",
                                "message": "Before initializing browser",
                                "data": {
                                    "mcp_tools_keys": list(mcp_tools.keys()) if mcp_tools else None,
                                    "has_playwright_navigate": bool(
                                        mcp_tools.get("playwright_navigate") if mcp_tools else False
                                    ),
                                    "has_playwright_fill": bool(
                                        mcp_tools.get("playwright_fill") if mcp_tools else False
                                    ),
                                },
                                "timestamp": int(time_module.time() * 1000),
                            }
                        )
                        + "\n"
                    )
            except Exception as e:
                logger.error(f"Log error: {e}")
            # #endregion
            result = self.browser.initialize_browser(mcp_tools)
            # #region agent log
            try:
                browser_keys = None
                if hasattr(self.browser, "mcp_tools") and self.browser.mcp_tools:
                    try:
                        browser_keys = list(self.browser.mcp_tools.keys())
                    except:
                        browser_keys = "error"
                with open("/tmp/grant_automation_debug.log", "a") as f:
                    f.write(
                        json.dumps(
                            {
                                "sessionId": "debug-session",
                                "runId": "post-fix-v3",
                                "hypothesisId": "H2",
                                "location": "application_automator.py:__init__:after_init",
                                "message": "After initializing browser",
                                "data": {
                                    "init_success": bool(result),
                                    "has_mcp_tools_attr": hasattr(self.browser, "mcp_tools"),
                                    "browser_mcp_tools_keys": browser_keys,
                                },
                                "timestamp": int(time_module.time() * 1000),
                            }
                        )
                        + "\n"
                    )
            except Exception as e:
                logger.error(f"Log error: {e}")
            # #endregion
        else:
            # #region agent log
            import json
            import time as time_module

            try:
                with open("/tmp/grant_automation_debug.log", "a") as f:
                    f.write(
                        json.dumps(
                            {
                                "sessionId": "debug-session",
                                "runId": "post-fix-v3",
                                "hypothesisId": "H2",
                                "location": "application_automator.py:__init__:no_tools",
                                "message": "No mcp_tools provided",
                                "data": {},
                                "timestamp": int(time_module.time() * 1000),
                            }
                        )
                        + "\n"
                    )
            except Exception as e:
                logger.error(f"Log error: {e}")
            # #endregion

    def start_new_application(self, grant_name: str) -> bool:
        """
        Navigate to and start a new grant application.

        Args:
            grant_name: Name of the grant to apply for

        Returns:
            True if successful, False otherwise
        """
        try:
            # Navigate to draft applications page
            self._navigate_to_draft_applications()

            # Find and click the grant application link
            grant_found = self._click_grant_application_link(grant_name)

            if grant_found:
                self._take_screenshot("grant_application_started")
                return True
            else:
                logger.error(f"Grant application '{grant_name}' not found")
                return False

        except Exception as e:
            logger.error(f"Error starting new application: {e}")
            self._take_screenshot("error_starting_application")
            return False

    def _navigate_to_draft_applications(self):
        """Navigate to the draft applications page."""
        try:
            url = "https://apply.4culture.org/draft-applications"
            success = self.browser.navigate(url)
            if success:
                self.browser.wait_for(time_seconds=2)
                self.browser.take_screenshot("draft_applications_page")
                return True
            return False
        except Exception as e:
            logger.error(f"Error navigating to draft applications: {e}")
            return False

    def _click_grant_application_link(self, grant_name: str) -> bool:
        """Click the link to start a new application for the specified grant."""
        try:
            # Take snapshot to find the grant link
            snapshot = self.browser.take_snapshot()

            # Look for the grant link - try multiple descriptions
            link_descriptions = [
                f"Start New Application link for {grant_name}",
                f"link or button to start application for {grant_name}",
                f"Start New Application button for grant containing '{grant_name.split(':')[0]}'",
                "Start New Application button",
            ]

            for description in link_descriptions:
                element = self.browser.find_element(description)
                if element:
                    success = self.browser.click(description)
                    if success:
                        self.browser.wait_for(time_seconds=3)
                        self.browser.take_screenshot(
                            f"grant_application_{grant_name.replace(' ', '_')}"
                        )
                        return True

            logger.warning(f"Could not find grant application link for: {grant_name}")
            return False

        except Exception as e:
            logger.error(f"Error clicking grant application link: {e}")
            return False

    def extract_form_structure(self) -> Dict[str, Any]:
        """
        Extract the structure of the current form page.

        Returns:
            Dictionary containing form structure information
        """
        try:
            snapshot = self.browser.take_snapshot()

            # Parse snapshot to extract form fields
            # The snapshot should contain information about form elements
            form_structure = {"fields": [], "pages": [], "current_page": 1, "snapshot": snapshot}

            # Try to extract page navigation elements
            page_elements = self.browser.find_element("page navigation buttons or tabs")
            if page_elements:
                form_structure["pages"] = [1]  # Default to page 1

            return form_structure

        except Exception as e:
            logger.error(f"Error extracting form structure: {e}")
            return {"fields": [], "pages": [], "current_page": 1}

    def fill_form_field(self, field_name: str, value: str, field_type: str = "text") -> bool:
        """
        Fill a single form field.

        Args:
            field_name: Name or identifier of the field
            value: Value to fill
            field_type: Type of field (text, textarea, select, etc.)

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Filling field '{field_name}' with value: {value[:50]}...")

            # Create description for finding the field
            field_description = f"{field_name} input field or textarea"

            if field_type == "select":
                # For dropdowns, use select_option
                if isinstance(value, list):
                    success = self.browser.select_option(field_description, value)
                else:
                    success = self.browser.select_option(field_description, [value])
            else:
                # For text inputs and textareas, use type_text
                success = self.browser.type_text(field_description, str(value))

            if success:
                time.sleep(0.3)  # Small delay after filling
                return True
            else:
                logger.warning(f"Failed to fill field: {field_name}")
                return False

        except Exception as e:
            logger.error(f"Error filling field '{field_name}': {e}")
            return False

    def fill_form_fields(self, field_instructions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Fill multiple form fields based on instructions.

        Args:
            field_instructions: List of field filling instructions

        Returns:
            Result dictionary with success status and filled fields
        """
        result = {"success": True, "filled_fields": [], "failed_fields": [], "errors": []}

        for instruction in field_instructions:
            field_name = instruction.get("field_name")
            value = instruction.get("value")
            field_type = instruction.get("field_type", "text")
            action = instruction.get("action", "type")

            try:
                success = self._execute_field_action(field_name, value, action, field_type)

                if success:
                    result["filled_fields"].append(field_name)
                    logger.info(f"Successfully filled field: {field_name}")
                else:
                    result["failed_fields"].append(field_name)
                    result["success"] = False
                    logger.warning(f"Failed to fill field: {field_name}")

                # Small delay between fields
                time.sleep(0.5)

            except Exception as e:
                result["failed_fields"].append(field_name)
                result["errors"].append(f"{field_name}: {str(e)}")
                result["success"] = False
                logger.error(f"Error filling field '{field_name}': {e}")

        return result

    def _execute_field_action(
        self, field_name: str, value: str, action: str, field_type: str
    ) -> bool:
        """Execute the appropriate action for a field."""
        try:
            if action == "type":
                return self.fill_form_field(field_name, value, field_type)
            elif action == "select":
                return self.fill_form_field(field_name, value, "select")
            elif action == "click":
                return self.browser.click(f"{field_name} button or checkbox")
            else:
                logger.warning(f"Unknown action type: {action}")
                return False
        except Exception as e:
            logger.error(f"Error executing field action: {e}")
            return False

    def navigate_form_page(self, page_number: int) -> bool:
        """
        Navigate to a specific page in a multi-page form.

        Args:
            page_number: Page number to navigate to

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Navigating to form page {page_number}")

            # Try to find and click the page navigation button
            page_descriptions = [
                f"page {page_number} button or tab",
                "next page button",
                "continue button",
                f"page navigation button for page {page_number}",
            ]

            for description in page_descriptions:
                element = self.browser.find_element(description)
                if element:
                    success = self.browser.click(description)
                    if success:
                        self.browser.wait_for(time_seconds=2)
                        self.browser.take_screenshot(f"form_page_{page_number}")
                        return True

            # If no navigation found, try "Next" or "Continue" button
            next_button = self.browser.find_element("Next button or Continue button")
            if next_button:
                return self.browser.click("Next button or Continue button")

            logger.warning(f"Could not find navigation to page {page_number}")
            return False

        except Exception as e:
            logger.error(f"Error navigating to page {page_number}: {e}")
            return False

    def save_draft(self) -> Dict[str, Any]:
        """
        Save the current draft application.

        Returns:
            Result dictionary with save status and draft URL
        """
        result = {"success": False, "draft_url": None, "message": ""}

        try:
            logger.info("Saving draft application...")

            # Find and click the save button
            save_descriptions = [
                "Save Draft button",
                "Save button",
                "Save Application button",
                "button to save the draft",
            ]

            for description in save_descriptions:
                element = self.browser.find_element(description)
                if element:
                    success = self.browser.click(description)
                    if success:
                        # Wait for save to complete
                        self.browser.wait_for(time_seconds=3)

                        # Get current URL after save
                        draft_url = self.browser.get_current_url()
                        result["draft_url"] = draft_url
                        result["success"] = True
                        result["message"] = "Draft saved successfully"

                        # Take screenshot after save
                        self.browser.take_screenshot("draft_saved")
                        return result

            logger.warning("Could not find save button")
            result["message"] = "Save button not found"

        except Exception as e:
            logger.error(f"Error saving draft: {e}")
            result["message"] = str(e)
            self.browser.take_screenshot("error_saving_draft")

        return result

    def handle_form_validation_errors(self) -> List[str]:
        """
        Check for and return any form validation errors.

        Returns:
            List of error messages
        """
        errors = []

        try:
            # Take snapshot and look for error messages
            snapshot = self.browser.take_snapshot()

            # Look for common error indicators
            error_descriptions = [
                "error message",
                "validation error",
                "required field error",
                "form error",
                "alert message indicating error",
            ]

            for description in error_descriptions:
                element = self.browser.find_element(description)
                if element:
                    # Try to extract error text
                    if isinstance(element, dict):
                        error_text = element.get("text") or element.get("content")
                        if error_text:
                            errors.append(str(error_text))
                    elif isinstance(element, str):
                        errors.append(element)

        except Exception as e:
            logger.error(f"Error checking validation: {e}")

        return errors

    def _take_screenshot(self, name: str):
        """Take a screenshot for debugging."""
        try:
            screenshot_path = self.browser.take_screenshot(name)
            if screenshot_path:
                logger.info(f"Screenshot saved: {screenshot_path}")
        except Exception as e:
            logger.warning(f"Error taking screenshot: {e}")

    def get_current_page_url(self) -> Optional[str]:
        """Get the current page URL."""
        url = self.browser.get_current_url()
        if url:
            self.current_url = url
        return self.current_url

    def wait_for_page_load(self, timeout: int = 10):
        """Wait for page to load."""
        self.browser.wait_for(time_seconds=2)

    def login(self) -> bool:
        """
        Log in to the 4Culture portal.

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Logging in to 4Culture portal...")

            # Navigate to login page
            login_url = "https://apply.4culture.org/login"
            if not self.browser.navigate(login_url):
                return False

            self.browser.wait_for(time_seconds=2)

            # Find and fill username field
            username_field = self.browser.find_element("username input field or email input field")
            if not username_field:
                # Try alternative descriptions
                username_field = self.browser.find_element("login username field")

            if username_field:
                self.browser.type_text("username input field", self.username)
            else:
                logger.warning("Could not find username field")
                return False

            time.sleep(0.5)

            # Find and fill password field
            password_field = self.browser.find_element("password input field")
            if password_field:
                self.browser.type_text("password input field", self.password)
            else:
                logger.warning("Could not find password field")
                return False

            time.sleep(0.5)

            # Find and click login button
            login_button = self.browser.find_element("login button or sign in button")
            if login_button:
                self.browser.click("login button or sign in button")
                self.browser.wait_for(time_seconds=3)

                # Verify login by checking URL or page content
                current_url = self.browser.get_current_url()
                if "login" not in current_url.lower():
                    self.browser.take_screenshot("login_successful")
                    logger.info("Login successful")
                    return True
                else:
                    logger.warning("Login may have failed - still on login page")
                    self.browser.take_screenshot("login_failed")
                    return False
            else:
                logger.warning("Could not find login button")
                return False

        except Exception as e:
            logger.error(f"Error during login: {e}")
            self.browser.take_screenshot("login_error")
            return False

    def close(self):
        """Close the browser session."""
        try:
            self.browser.close_browser()
        except Exception as e:
            logger.warning(f"Error closing browser: {e}")

    def take_verification_snapshot(self) -> Dict[str, Any]:
        """Take snapshot and screenshot for verification."""
        try:
            snapshot = self.browser.take_snapshot()
            screenshot_path = self.browser.take_screenshot("login_verified")
            current_url = self.browser.get_current_url()

            return {
                "snapshot": snapshot if isinstance(snapshot, dict) else str(snapshot),
                "screenshot_path": screenshot_path,
                "current_url": current_url,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error taking verification snapshot: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    def get_grants_list_after_login(self) -> List[Dict]:
        """Navigate to grants list and extract available grants."""
        try:
            # Navigate to draft applications
            if not self._navigate_to_draft_applications():
                logger.warning("Could not navigate to draft applications")
                return []

            # Take snapshot to find grants
            snapshot = self.browser.take_snapshot()

            # Try to extract grant information from the page
            # This is a simplified extraction - in a real scenario, you'd parse the HTML/snapshot
            grants = []

            # Look for grant links or buttons
            grant_descriptions = [
                "Start New Application",
                "grant application link",
                "apply for grant",
            ]

            # Try to find grant elements by looking at the snapshot
            # The snapshot should contain information about available grants
            if isinstance(snapshot, dict):
                # Try to extract grant information from snapshot structure
                # This is a simplified approach - actual implementation would parse the full page
                logger.debug("Attempting to extract grants from snapshot")

            # For now, return empty list - actual grant extraction would parse the page HTML/snapshot
            # In a real implementation, you'd:
            # 1. Parse the snapshot/HTML to find grant links
            # 2. Extract grant names, deadlines, and other details
            # 3. Return structured grant data

            logger.info(
                "Grant extraction placeholder - would parse page structure in full implementation"
            )

            return grants

        except Exception as e:
            logger.error(f"Error getting grants list: {e}")
            return []
