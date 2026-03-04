"""
MCP Browser Integration for Grant Application Automation
Integrates with MCP browser tools (Browserbase/Stagehand) for actual browser automation.
"""

import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class MCPBrowserIntegration:
    """Integration layer for MCP browser automation tools."""

    def __init__(self, use_multi_session: bool = False):
        """
        Initialize MCP browser integration.

        Args:
            use_multi_session: Whether to use multi-session browser tools
        """
        self.use_multi_session = use_multi_session
        self.session_id: Optional[str] = None
        self.current_url: Optional[str] = None
        self.screenshots_dir = Path("agents/grant_scraper/screenshots")
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)

    def _get_mcp_tools(self):
        """Get MCP browser tools - this will be injected by the workflow."""
        # These will be passed from the workflow that has access to MCP tools
        return None

    def initialize_browser(self, mcp_tools: Dict[str, Any]) -> bool:
        """
        Initialize browser session using MCP tools.

        Args:
            mcp_tools: Dictionary of MCP tool functions

        Returns:
            True if successful, False otherwise
        """
        try:
            # #region agent log
            import json

            try:
                with open("/tmp/grant_automation_debug.log", "a") as f:
                    f.write(
                        json.dumps(
                            {
                                "sessionId": "debug-session",
                                "runId": "post-fix-v2",
                                "hypothesisId": "H2",
                                "location": "mcp_browser_integration.py:initialize_browser:entry",
                                "message": "initialize_browser called",
                                "data": {
                                    "mcp_tools_keys": list(mcp_tools.keys()) if mcp_tools else None
                                },
                                "timestamp": int(__import__("time").time() * 1000),
                            }
                        )
                        + "\n"
                    )
            except Exception:
                pass
            # #endregion

            self.mcp_tools = mcp_tools

            # Check for Playwright tools - they don't need session creation
            playwright_tools = [
                "playwright_navigate",
                "playwright_fill",
                "playwright_click",
                "browser_navigate",
                "browser_type",
                "browser_click",
            ]
            has_playwright = any(mcp_tools.get(tool) for tool in playwright_tools)

            if has_playwright:
                # #region agent log
                try:
                    with open("/tmp/grant_automation_debug.log", "a") as f:
                        f.write(
                            json.dumps(
                                {
                                    "sessionId": "debug-session",
                                    "runId": "post-fix-v2",
                                    "hypothesisId": "H2",
                                    "location": "mcp_browser_integration.py:initialize_browser:playwright",
                                    "message": "Playwright tools detected, no session needed",
                                    "data": {},
                                    "timestamp": int(__import__("time").time() * 1000),
                                }
                            )
                            + "\n"
                        )
                except Exception:
                    pass
                # #endregion
                logger.info("Playwright browser tools initialized (no session needed)")
                return True

            if self.use_multi_session:
                # Use multi-session tools
                create_session = mcp_tools.get("multi_browserbase_stagehand_session_create")
                if create_session:
                    result = create_session(name="grant-application-automation")
                    self.session_id = result.get("sessionId")
                    logger.info(f"Multi-session browser initialized: {self.session_id}")
                    return True
            else:
                # Use single session tools
                create_session = mcp_tools.get("browserbase_session_create")
                if create_session:
                    create_session()
                    logger.info("Single-session browser initialized")
                    return True

            # #region agent log
            try:
                with open("/tmp/grant_automation_debug.log", "a") as f:
                    f.write(
                        json.dumps(
                            {
                                "sessionId": "debug-session",
                                "runId": "post-fix-v2",
                                "hypothesisId": "H2",
                                "location": "mcp_browser_integration.py:initialize_browser:no_tools",
                                "message": "No MCP browser tools available",
                                "data": {},
                                "timestamp": int(__import__("time").time() * 1000),
                            }
                        )
                        + "\n"
                    )
            except Exception:
                pass
            # #endregion
            logger.warning("No MCP browser tools available")
            return False

        except Exception as e:
            # #region agent log
            try:
                with open("/tmp/grant_automation_debug.log", "a") as f:
                    f.write(
                        json.dumps(
                            {
                                "sessionId": "debug-session",
                                "runId": "post-fix-v2",
                                "hypothesisId": "H2",
                                "location": "mcp_browser_integration.py:initialize_browser:error",
                                "message": "Error initializing browser",
                                "data": {"error": str(e)},
                                "timestamp": int(__import__("time").time() * 1000),
                            }
                        )
                        + "\n"
                    )
            except Exception as e:
                pass
            # #endregion
            logger.error(f"Error initializing browser: {e}")
            return False

    def navigate(self, url: str) -> bool:
        """
        Navigate to a URL.

        Args:
            url: URL to navigate to

        Returns:
            True if successful, False otherwise
        """
        try:
            # #region agent log
            import json

            with open("/tmp/grant_automation_debug.log", "a") as f:
                f.write(
                    json.dumps(
                        {
                            "sessionId": "debug-session",
                            "runId": "initial",
                            "hypothesisId": "H3",
                            "location": "mcp_browser_integration.py:navigate:entry",
                            "message": "Navigate called",
                            "data": {
                                "url": url,
                                "mcp_tools_keys": list(self.mcp_tools.keys())
                                if self.mcp_tools
                                else None,
                            },
                            "timestamp": int(__import__("time").time() * 1000),
                        }
                    )
                    + "\n"
                )
            # #endregion

            navigate_tool = None

            # Try Playwright tools first (direct integration)
            playwright_navigate = (
                self.mcp_tools.get("playwright_navigate") or self.mcp_tools.get("browser_navigate")
                if self.mcp_tools
                else None
            )
            if playwright_navigate:
                try:
                    # #region agent log
                    with open("/tmp/grant_automation_debug.log", "a") as f:
                        f.write(
                            json.dumps(
                                {
                                    "sessionId": "debug-session",
                                    "runId": "initial",
                                    "hypothesisId": "H3",
                                    "location": "mcp_browser_integration.py:navigate:playwright",
                                    "message": "Using Playwright navigate",
                                    "data": {"url": url},
                                    "timestamp": int(__import__("time").time() * 1000),
                                }
                            )
                            + "\n"
                        )
                    # #endregion
                    result = playwright_navigate(url)
                    if result:
                        self.current_url = url
                        time.sleep(2)  # Wait for page load
                        # #region agent log
                        playwright_get_url = (
                            self.mcp_tools.get("playwright_get_url")
                            or self.mcp_tools.get("browser_get_url")
                            if self.mcp_tools
                            else None
                        )
                        actual_url = playwright_get_url() if playwright_get_url else url
                        with open("/tmp/grant_automation_debug.log", "a") as f:
                            f.write(
                                json.dumps(
                                    {
                                        "sessionId": "debug-session",
                                        "runId": "initial",
                                        "hypothesisId": "H3",
                                        "location": "mcp_browser_integration.py:navigate:playwright_success",
                                        "message": "Playwright navigate succeeded",
                                        "data": {"url": url, "actual_url": actual_url},
                                        "timestamp": int(__import__("time").time() * 1000),
                                    }
                                )
                                + "\n"
                            )
                        # #endregion
                        logger.info(f"Navigated to: {url} (using Playwright)")
                        return True
                except Exception as e:
                    # #region agent log
                    with open("/tmp/grant_automation_debug.log", "a") as f:
                        f.write(
                            json.dumps(
                                {
                                    "sessionId": "debug-session",
                                    "runId": "initial",
                                    "hypothesisId": "H3",
                                    "location": "mcp_browser_integration.py:navigate:playwright_error",
                                    "message": "Playwright navigate failed",
                                    "data": {"error": str(e)},
                                    "timestamp": int(__import__("time").time() * 1000),
                                }
                            )
                            + "\n"
                        )
                    # #endregion
                    logger.warning(f"Playwright navigate failed: {e}, trying alternatives")

            # Try Cursor IDE browser tools
            cursor_navigate = self.mcp_tools.get("cursor_ide_browser_navigate")
            if cursor_navigate:
                try:
                    cursor_navigate(url=url)
                    self.current_url = url
                    time.sleep(2)  # Wait for page load
                    logger.info(f"Navigated to: {url} (using Cursor IDE browser)")
                    return True
                except Exception as e:
                    logger.warning(f"Cursor IDE navigate failed: {e}, trying alternatives")

            # Try Browserbase/Stagehand tools
            if self.use_multi_session and self.session_id:
                navigate_tool = self.mcp_tools.get("multi_browserbase_stagehand_navigate_session")
                if navigate_tool:
                    navigate_tool(sessionId=self.session_id, url=url)
            else:
                navigate_tool = self.mcp_tools.get("browserbase_stagehand_navigate")
                if navigate_tool:
                    navigate_tool(url=url)

            if navigate_tool:
                self.current_url = url
                time.sleep(2)  # Wait for page load
                logger.info(f"Navigated to: {url}")
                return True
            else:
                logger.warning("Navigate tool not available")
                return False

        except Exception as e:
            logger.error(f"Error navigating to {url}: {e}")
            return False

    def take_snapshot(self) -> Optional[Dict[str, Any]]:
        """
        Take a snapshot of the current page.

        Returns:
            Snapshot data or None if error
        """
        try:
            # Try Playwright snapshot first
            playwright_snapshot = self.mcp_tools.get("playwright_snapshot") or self.mcp_tools.get(
                "browser_take_snapshot"
            )
            if playwright_snapshot:
                try:
                    result = playwright_snapshot()
                    if result:
                        logger.info("Snapshot taken (using Playwright)")
                        return result
                except Exception as e:
                    logger.warning(f"Playwright snapshot failed: {e}, trying alternatives")

            # Try Cursor IDE browser snapshot
            cursor_snapshot = self.mcp_tools.get("cursor_ide_browser_snapshot")
            if cursor_snapshot:
                try:
                    result = cursor_snapshot()
                    logger.info("Snapshot taken (using Cursor IDE browser)")
                    return result
                except Exception as e:
                    logger.warning(f"Cursor IDE snapshot failed: {e}, trying alternatives")

            # Try Browserbase/Stagehand observe tool
            observe_tool = None
            if self.use_multi_session and self.session_id:
                observe_tool = self.mcp_tools.get("multi_browserbase_stagehand_observe_session")
            else:
                observe_tool = self.mcp_tools.get("browserbase_stagehand_observe")

            if observe_tool:
                if self.use_multi_session and self.session_id:
                    result = observe_tool(
                        sessionId=self.session_id,
                        instruction="Observe the entire page structure including all form fields, buttons, and interactive elements",
                    )
                else:
                    result = observe_tool(
                        instruction="Observe the entire page structure including all form fields, buttons, and interactive elements"
                    )
                return result
            else:
                logger.warning("Observe tool not available")
                return None

        except Exception as e:
            logger.error(f"Error taking snapshot: {e}")
            return None

    def find_element(
        self, description: str, return_action: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Find an element on the page by description.

        Args:
            description: Description of the element to find
            return_action: Whether to return action information

        Returns:
            Element information or None if not found
        """
        try:
            # #region agent log
            import json

            with open("/tmp/grant_automation_debug.log", "a") as f:
                f.write(
                    json.dumps(
                        {
                            "sessionId": "debug-session",
                            "runId": "initial",
                            "hypothesisId": "H1,H2,H4",
                            "location": "mcp_browser_integration.py:find_element:entry",
                            "message": "find_element called",
                            "data": {
                                "description": description,
                                "mcp_tools_keys": list(self.mcp_tools.keys())
                                if self.mcp_tools
                                else None,
                                "has_playwright": bool(
                                    self.mcp_tools.get("playwright_navigate")
                                    if self.mcp_tools
                                    else False
                                ),
                            },
                            "timestamp": int(__import__("time").time() * 1000),
                        }
                    )
                    + "\n"
                )
            # #endregion

            # Try Playwright first - check if any Playwright tools are available
            has_playwright = False
            if self.mcp_tools:
                playwright_tools = [
                    "playwright_navigate",
                    "playwright_fill",
                    "playwright_click",
                    "browser_navigate",
                    "browser_type",
                    "browser_click",
                ]
                has_playwright = any(self.mcp_tools.get(tool) for tool in playwright_tools)

            if has_playwright:
                # #region agent log
                with open("/tmp/grant_automation_debug.log", "a") as f:
                    f.write(
                        json.dumps(
                            {
                                "sessionId": "debug-session",
                                "runId": "initial",
                                "hypothesisId": "H1",
                                "location": "mcp_browser_integration.py:find_element:playwright",
                                "message": "Playwright tools available, returning placeholder",
                                "data": {"description": description},
                                "timestamp": int(__import__("time").time() * 1000),
                            }
                        )
                        + "\n"
                    )
                # #endregion
                # For Playwright, we can't directly find by description, but we can return a dict
                # that indicates the element should be found by the description
                # The actual finding will happen in type_text/click methods using Playwright's locator API
                return {
                    "description": description,
                    "found": True,
                    "method": "playwright",
                    "selector": description,
                }

            observe_tool = None
            if self.use_multi_session and self.session_id:
                observe_tool = (
                    self.mcp_tools.get("multi_browserbase_stagehand_observe_session")
                    if self.mcp_tools
                    else None
                )
            else:
                observe_tool = (
                    self.mcp_tools.get("browserbase_stagehand_observe") if self.mcp_tools else None
                )

            # #region agent log
            with open("/tmp/grant_automation_debug.log", "a") as f:
                f.write(
                    json.dumps(
                        {
                            "sessionId": "debug-session",
                            "runId": "initial",
                            "hypothesisId": "H2",
                            "location": "mcp_browser_integration.py:find_element:observe_check",
                            "message": "Checking observe tool",
                            "data": {"has_observe_tool": bool(observe_tool)},
                            "timestamp": int(__import__("time").time() * 1000),
                        }
                    )
                    + "\n"
                )
            # #endregion

            if observe_tool:
                if self.use_multi_session and self.session_id:
                    result = observe_tool(
                        sessionId=self.session_id,
                        instruction=description,
                        returnAction=return_action,
                    )
                else:
                    result = observe_tool(instruction=description, returnAction=return_action)
                # #region agent log
                with open("/tmp/grant_automation_debug.log", "a") as f:
                    f.write(
                        json.dumps(
                            {
                                "sessionId": "debug-session",
                                "runId": "initial",
                                "hypothesisId": "H2",
                                "location": "mcp_browser_integration.py:find_element:observe_result",
                                "message": "Observe tool result",
                                "data": {"has_result": bool(result)},
                                "timestamp": int(__import__("time").time() * 1000),
                            }
                        )
                        + "\n"
                    )
                # #endregion
                return result
            else:
                # #region agent log
                with open("/tmp/grant_automation_debug.log", "a") as f:
                    f.write(
                        json.dumps(
                            {
                                "sessionId": "debug-session",
                                "runId": "initial",
                                "hypothesisId": "H1,H2",
                                "location": "mcp_browser_integration.py:find_element:no_tool",
                                "message": "No observe tool available",
                                "data": {"description": description},
                                "timestamp": int(__import__("time").time() * 1000),
                            }
                        )
                        + "\n"
                    )
                # #endregion
                logger.warning("Observe tool not available")
                return None

        except Exception as e:
            # #region agent log
            with open("/tmp/grant_automation_debug.log", "a") as f:
                f.write(
                    json.dumps(
                        {
                            "sessionId": "debug-session",
                            "runId": "initial",
                            "hypothesisId": "H1,H2,H4",
                            "location": "mcp_browser_integration.py:find_element:error",
                            "message": "Error finding element",
                            "data": {"error": str(e)},
                            "timestamp": int(__import__("time").time() * 1000),
                        }
                    )
                    + "\n"
                )
            # #endregion
            logger.error(f"Error finding element: {e}")
            return None

    def click(self, element_description: str, element_ref: Optional[str] = None) -> bool:
        """
        Click an element on the page.

        Args:
            element_description: Description of element to click
            element_ref: Optional element reference from snapshot

        Returns:
            True if successful, False otherwise
        """
        try:
            # Try Playwright click first
            playwright_click = self.mcp_tools.get("playwright_click") or self.mcp_tools.get(
                "browser_click"
            )
            if playwright_click:
                try:
                    # For Playwright, try to use description as selector or find element first
                    if not element_ref:
                        element_info = self.find_element(element_description)
                        if element_info and isinstance(element_info, dict):
                            element_ref = element_info.get("ref") or element_info.get("selector")

                    # Try clicking with selector/ref
                    selector = element_ref or element_description
                    result = playwright_click(selector)
                    if result:
                        time.sleep(1)
                        logger.info(f"Clicked: {element_description} (using Playwright)")
                        return True
                except Exception as e:
                    logger.warning(f"Playwright click failed: {e}, trying alternatives")

            # First, find the element if ref not provided
            if not element_ref:
                element_info = self.find_element(element_description)
                if element_info and isinstance(element_info, dict):
                    # Extract ref from element info
                    element_ref = element_info.get("ref") or element_info.get("element_ref")

            if not element_ref:
                # Try using act tool which can find elements by description
                act_tool = None
                if self.use_multi_session and self.session_id:
                    act_tool = self.mcp_tools.get("multi_browserbase_stagehand_act_session")
                else:
                    act_tool = self.mcp_tools.get("browserbase_stagehand_act")

                if act_tool:
                    action = f"Click the {element_description}"
                    if self.use_multi_session and self.session_id:
                        act_tool(sessionId=self.session_id, action=action)
                    else:
                        act_tool(action=action)
                    time.sleep(1)
                    logger.info(f"Clicked: {element_description}")
                    return True
            else:
                # Use cursor-ide-browser tools if available (more precise)
                click_tool = self.mcp_tools.get("cursor_ide_browser_click")
                if click_tool:
                    click_tool(element=element_description, ref=element_ref)
                    time.sleep(1)
                    logger.info(f"Clicked: {element_description}")
                    return True

            logger.warning(f"Could not click element: {element_description}")
            return False

        except Exception as e:
            logger.error(f"Error clicking element '{element_description}': {e}")
            return False

    def type_text(
        self,
        element_description: str,
        text: str,
        element_ref: Optional[str] = None,
        submit: bool = False,
    ) -> bool:
        """
        Type text into an input field.

        Args:
            element_description: Description of input field
            text: Text to type
            element_ref: Optional element reference from snapshot

        Returns:
            True if successful, False otherwise
        """
        try:
            # #region agent log
            import json
            import time as time_module

            try:
                mcp_keys = None
                if hasattr(self, "mcp_tools") and self.mcp_tools:
                    try:
                        mcp_keys = list(self.mcp_tools.keys())
                    except:
                        mcp_keys = "error_getting_keys"
                with open("/tmp/grant_automation_debug.log", "a") as f:
                    f.write(
                        json.dumps(
                            {
                                "sessionId": "debug-session",
                                "runId": "post-fix-v3",
                                "hypothesisId": "H5",
                                "location": "mcp_browser_integration.py:type_text:entry",
                                "message": "type_text called",
                                "data": {
                                    "element_description": element_description,
                                    "has_element_ref": bool(element_ref),
                                    "has_mcp_tools_attr": hasattr(self, "mcp_tools"),
                                    "mcp_tools_keys": mcp_keys,
                                },
                                "timestamp": int(time_module.time() * 1000),
                            }
                        )
                        + "\n"
                    )
            except Exception as log_err:
                logger.error(f"Log write error in type_text entry: {log_err}")
            # #endregion

            # Try Playwright fill first
            playwright_fill = self.mcp_tools.get("playwright_fill") if self.mcp_tools else None
            playwright_type = self.mcp_tools.get("browser_type") if self.mcp_tools else None

            # #region agent log
            try:
                with open("/tmp/grant_automation_debug.log", "a") as f:
                    f.write(
                        json.dumps(
                            {
                                "sessionId": "debug-session",
                                "runId": "post-fix-v2",
                                "hypothesisId": "H5",
                                "location": "mcp_browser_integration.py:type_text:playwright_check",
                                "message": "Checking Playwright tools",
                                "data": {
                                    "has_mcp_tools": bool(self.mcp_tools),
                                    "mcp_tools_keys": list(self.mcp_tools.keys())
                                    if self.mcp_tools
                                    else None,
                                    "has_playwright_fill": bool(playwright_fill),
                                    "has_playwright_type": bool(playwright_type),
                                },
                                "timestamp": int(__import__("time").time() * 1000),
                            }
                        )
                        + "\n"
                    )
            except Exception as log_err:
                logger.error(f"Log write error: {log_err}")
            # #endregion

            if playwright_fill or playwright_type:
                try:
                    # #region agent log
                    try:
                        with open("/tmp/grant_automation_debug.log", "a") as f:
                            f.write(
                                json.dumps(
                                    {
                                        "sessionId": "debug-session",
                                        "runId": "post-fix-v2",
                                        "hypothesisId": "H5",
                                        "location": "mcp_browser_integration.py:type_text:playwright",
                                        "message": "Using Playwright fill",
                                        "data": {
                                            "element_description": element_description,
                                            "has_fill": bool(playwright_fill),
                                            "has_type": bool(playwright_type),
                                        },
                                        "timestamp": int(__import__("time").time() * 1000),
                                    }
                                )
                                + "\n"
                            )
                    except Exception:
                        pass
                    # #endregion
                    # For Playwright, use description directly - no need to find element first
                    # Playwright's fill method can handle descriptions
                    # Prefer browser_type (wrapper) over playwright_fill if both exist
                    if playwright_type:
                        # browser_type_wrapper accepts (desc, txt, elem_ref, **kwargs)
                        # It will convert to positional args for playwright_fill
                        result = playwright_type(
                            desc=element_description, txt=text, elem_ref=element_ref
                        )
                    elif playwright_fill:
                        # playwright_fill expects (selector_or_description, text) as positional args
                        result = playwright_fill(element_description, text)
                    else:
                        result = False

                    if result:
                        # #region agent log
                        try:
                            with open("/tmp/grant_automation_debug.log", "a") as f:
                                f.write(
                                    json.dumps(
                                        {
                                            "sessionId": "debug-session",
                                            "runId": "post-fix-v2",
                                            "hypothesisId": "H5",
                                            "location": "mcp_browser_integration.py:type_text:playwright_success",
                                            "message": "Playwright fill succeeded",
                                            "data": {"element_description": element_description},
                                            "timestamp": int(__import__("time").time() * 1000),
                                        }
                                    )
                                    + "\n"
                                )
                        except Exception:
                            pass
                        # #endregion
                        logger.info(f"Typed text into {element_description} (using Playwright)")
                        return True
                    else:
                        # #region agent log
                        try:
                            with open("/tmp/grant_automation_debug.log", "a") as f:
                                f.write(
                                    json.dumps(
                                        {
                                            "sessionId": "debug-session",
                                            "runId": "post-fix-v2",
                                            "hypothesisId": "H5",
                                            "location": "mcp_browser_integration.py:type_text:playwright_failed",
                                            "message": "Playwright fill returned False",
                                            "data": {"element_description": element_description},
                                            "timestamp": int(__import__("time").time() * 1000),
                                        }
                                    )
                                    + "\n"
                                )
                        except Exception:
                            pass
                        # #endregion
                except Exception as e:
                    # #region agent log
                    try:
                        with open("/tmp/grant_automation_debug.log", "a") as f:
                            f.write(
                                json.dumps(
                                    {
                                        "sessionId": "debug-session",
                                        "runId": "post-fix-v2",
                                        "hypothesisId": "H5",
                                        "location": "mcp_browser_integration.py:type_text:playwright_error",
                                        "message": "Playwright type failed with exception",
                                        "data": {"error": str(e), "error_type": type(e).__name__},
                                        "timestamp": int(__import__("time").time() * 1000),
                                    }
                                )
                                + "\n"
                            )
                    except Exception:
                        pass
                    # #endregion
                    logger.warning(f"Playwright type failed: {e}, trying alternatives")
                    import traceback

                    logger.debug(traceback.format_exc())

            # First, find the element if ref not provided
            if not element_ref:
                element_info = self.find_element(element_description)
                if element_info and isinstance(element_info, dict):
                    element_ref = element_info.get("ref") or element_info.get("element_ref")

            if not element_ref:
                # Use act tool which can find elements by description
                act_tool = None
                if self.use_multi_session and self.session_id:
                    act_tool = self.mcp_tools.get("multi_browserbase_stagehand_act_session")
                else:
                    act_tool = self.mcp_tools.get("browserbase_stagehand_act")

                if act_tool:
                    action = f"Type '{text}' into the {element_description}"
                    if submit:
                        action += " and press Enter"
                    if self.use_multi_session and self.session_id:
                        act_tool(sessionId=self.session_id, action=action)
                    else:
                        act_tool(action=action)
                    time.sleep(0.5)
                    logger.info(f"Typed text into: {element_description}")
                    return True
            else:
                # Use cursor-ide-browser tools if available (more precise)
                type_tool = self.mcp_tools.get("cursor_ide_browser_type")
                if type_tool:
                    type_tool(
                        element=element_description, ref=element_ref, text=text, submit=submit
                    )
                    time.sleep(0.5)
                    logger.info(f"Typed text into: {element_description}")
                    return True

            logger.warning(f"Could not type into element: {element_description}")
            return False

        except Exception as e:
            logger.error(f"Error typing into element '{element_description}': {e}")
            return False

    def select_option(
        self, element_description: str, values: List[str], element_ref: Optional[str] = None
    ) -> bool:
        """
        Select option(s) in a dropdown.

        Args:
            element_description: Description of dropdown element
            values: List of values to select
            element_ref: Optional element reference

        Returns:
            True if successful, False otherwise
        """
        try:
            # First, find the element if ref not provided
            if not element_ref:
                element_info = self.find_element(element_description)
                if element_info and isinstance(element_info, dict):
                    element_ref = element_info.get("ref") or element_info.get("element_ref")

            if element_ref:
                select_tool = self.mcp_tools.get("cursor_ide_browser_select_option")
                if select_tool:
                    select_tool(element=element_description, ref=element_ref, values=values)
                    time.sleep(0.5)
                    logger.info(f"Selected {values} in: {element_description}")
                    return True

            # Fallback to act tool
            act_tool = None
            if self.use_multi_session and self.session_id:
                act_tool = self.mcp_tools.get("multi_browserbase_stagehand_act_session")
            else:
                act_tool = self.mcp_tools.get("browserbase_stagehand_act")

            if act_tool:
                action = f"Select '{values[0]}' in the {element_description}"
                if self.use_multi_session and self.session_id:
                    act_tool(sessionId=self.session_id, action=action)
                else:
                    act_tool(action=action)
                time.sleep(0.5)
                logger.info(f"Selected option in: {element_description}")
                return True

            logger.warning(f"Could not select option in: {element_description}")
            return False

        except Exception as e:
            logger.error(f"Error selecting option in '{element_description}': {e}")
            return False

    def take_screenshot(self, name: str) -> Optional[str]:
        """
        Take a screenshot of the current page.

        Args:
            name: Name for the screenshot

        Returns:
            Path to screenshot file or None if error
        """
        try:
            # Try Playwright screenshot first
            playwright_screenshot = self.mcp_tools.get(
                "playwright_screenshot"
            ) or self.mcp_tools.get("browser_take_screenshot")
            if playwright_screenshot:
                try:
                    result = playwright_screenshot(name)
                    if result:
                        logger.info(f"Screenshot saved: {result} (using Playwright)")
                        return result
                except Exception as e:
                    logger.warning(f"Playwright screenshot failed: {e}, trying alternatives")

            # Try Cursor IDE browser screenshot
            cursor_screenshot = self.mcp_tools.get("cursor_ide_browser_take_screenshot")
            if cursor_screenshot:
                try:
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    filename = f"{name}_{timestamp}.png"
                    filepath = str(self.screenshots_dir / filename)
                    cursor_screenshot(filename=filename)
                    logger.info(f"Screenshot saved: {filepath} (using Cursor IDE browser)")
                    return filepath
                except Exception as e:
                    logger.warning(f"Cursor IDE screenshot failed: {e}, trying alternatives")

            screenshot_tool = None
            if self.use_multi_session and self.session_id:
                # Multi-session doesn't have direct screenshot, use single session
                screenshot_tool = self.mcp_tools.get("browserbase_screenshot")
            else:
                screenshot_tool = self.mcp_tools.get("browserbase_screenshot")

            if screenshot_tool:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"{name}_{timestamp}.png"
                filepath = str(self.screenshots_dir / filename)

                screenshot_tool(name=filename)
                logger.info(f"Screenshot saved: {filepath}")
                return filepath
            else:
                logger.warning("Screenshot tool not available")
                return None

        except Exception as e:
            logger.error(f"Error taking screenshot: {e}")
            return None

    def get_current_url(self) -> Optional[str]:
        """
        Get the current page URL.

        Returns:
            Current URL or None if error
        """
        try:
            # Try Playwright get_url first
            playwright_get_url = self.mcp_tools.get("playwright_get_url") or self.mcp_tools.get(
                "browser_get_url"
            )
            if playwright_get_url:
                try:
                    result = playwright_get_url()
                    if result:
                        self.current_url = result
                        logger.info(f"Got URL: {result} (using Playwright)")
                        return result
                except Exception as e:
                    logger.warning(f"Playwright get_url failed: {e}, trying alternatives")

            # Try Cursor IDE browser get_url
            cursor_get_url = self.mcp_tools.get("cursor_ide_browser_get_url")
            if cursor_get_url:
                try:
                    result = cursor_get_url()
                    if isinstance(result, dict):
                        return result.get("url") or result.get("current_url")
                    elif isinstance(result, str):
                        return result
                    return str(result) if result else None
                except Exception as e:
                    logger.warning(f"Cursor IDE get_url failed: {e}, trying alternatives")

            # Try Browserbase/Stagehand get_url
            get_url_tool = None
            if self.use_multi_session and self.session_id:
                get_url_tool = self.mcp_tools.get("multi_browserbase_stagehand_get_url_session")
                if get_url_tool:
                    result = get_url_tool(sessionId=self.session_id)
                    if isinstance(result, dict):
                        return result.get("url")
                    return str(result) if result else None
            else:
                get_url_tool = self.mcp_tools.get("browserbase_stagehand_get_url")
                if get_url_tool:
                    result = get_url_tool()
                    if isinstance(result, dict):
                        return result.get("url")
                    return str(result) if result else None

            # Fallback to stored URL
            if self.current_url:
                return self.current_url

            logger.warning("Get URL tool not available")
            return None

        except Exception as e:
            logger.error(f"Error getting current URL: {e}")
            return None

    def wait_for(
        self,
        text: Optional[str] = None,
        text_gone: Optional[str] = None,
        time_seconds: Optional[float] = None,
    ) -> bool:
        """
        Wait for text to appear/disappear or for a specified time.

        Args:
            text: Text to wait for
            text_gone: Text to wait for to disappear
            time_seconds: Time in seconds to wait

        Returns:
            True if successful, False otherwise
        """
        try:
            # Try Playwright wait first
            playwright_wait = self.mcp_tools.get("playwright_wait") or self.mcp_tools.get(
                "browser_wait"
            )
            if playwright_wait:
                try:
                    if time_seconds:
                        playwright_wait(time_seconds)
                    else:
                        playwright_wait(2.0)
                    return True
                except Exception as e:
                    logger.warning(f"Playwright wait failed: {e}, trying alternatives")

            wait_tool = self.mcp_tools.get("cursor_ide_browser_wait_for")
            if wait_tool:
                if time_seconds:
                    wait_tool(time=time_seconds)
                elif text:
                    wait_tool(text=text)
                elif text_gone:
                    wait_tool(textGone=text_gone)
                return True
            else:
                # Fallback to time.sleep
                if time_seconds:
                    time.sleep(time_seconds)
                else:
                    time.sleep(2)
                return True

        except Exception as e:
            logger.warning(f"Error in wait_for: {e}, using fallback")
            if time_seconds:
                time.sleep(time_seconds)
            else:
                time.sleep(2)
            return True

    def close_browser(self):
        """Close the browser session."""
        try:
            # Try Playwright close first
            playwright_close = self.mcp_tools.get("playwright_close") or self.mcp_tools.get(
                "browser_close"
            )
            if playwright_close:
                try:
                    playwright_close()
                    logger.info("Browser closed (using Playwright)")
                    return
                except Exception as e:
                    logger.warning(f"Playwright close failed: {e}, trying alternatives")

            if self.use_multi_session and self.session_id:
                close_tool = self.mcp_tools.get("multi_browserbase_stagehand_session_close")
                if close_tool:
                    close_tool(sessionId=self.session_id)
                    logger.info("Multi-session browser closed")
            else:
                close_tool = self.mcp_tools.get("browserbase_session_close")
                if close_tool:
                    close_tool()
                    logger.info("Browser session closed")
        except Exception as e:
            logger.warning(f"Error closing browser: {e}")
