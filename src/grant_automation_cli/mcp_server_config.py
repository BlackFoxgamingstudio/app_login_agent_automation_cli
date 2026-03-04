"""
MCP Server Configuration and Connection
Provides utilities to configure and connect to MCP servers for browser automation.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class MCPServerConfig:
    """Manages MCP server configuration for browser tools."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize MCP server configuration.

        Args:
            config_path: Path to MCP server configuration file
        """
        self.config_path = Path(config_path or "~/.mcp_servers.json").expanduser()
        self.config: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self):
        """Load MCP server configuration from file."""
        if self.config_path.exists():
            try:
                with open(self.config_path, "r") as f:
                    self.config = json.load(f)
                logger.info(f"Loaded MCP server config from {self.config_path}")
            except Exception as e:
                logger.warning(f"Error loading MCP config: {e}")
                self.config = {}
        else:
            self.config = {"servers": {}, "default_server": None, "browser_tools": {}}

    def _save_config(self):
        """Save MCP server configuration to file."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, "w") as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"Saved MCP server config to {self.config_path}")
        except Exception as e:
            logger.error(f"Error saving MCP config: {e}")

    def add_server(self, name: str, server_type: str, config: Dict[str, Any]):
        """
        Add an MCP server configuration.

        Args:
            name: Server name/identifier
            server_type: Type of server (e.g., 'browserbase', 'cursor-ide-browser')
            config: Server configuration dictionary
        """
        if "servers" not in self.config:
            self.config["servers"] = {}

        self.config["servers"][name] = {"type": server_type, "config": config, "enabled": True}
        self._save_config()
        logger.info(f"Added MCP server: {name}")

    def get_server_config(self, name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get MCP server configuration.

        Args:
            name: Server name (uses default if not provided)

        Returns:
            Server configuration or None
        """
        server_name = name or self.config.get("default_server")
        if not server_name:
            return None

        return self.config.get("servers", {}).get(server_name)

    def list_servers(self) -> List[str]:
        """List all configured MCP servers."""
        return list(self.config.get("servers", {}).keys())

    def connect_to_server(self, name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Connect to MCP server and get available tools.

        Args:
            name: Server name (uses default if not provided)

        Returns:
            Dictionary of available tools or None
        """
        server_config = self.get_server_config(name)
        if not server_config:
            logger.warning("No MCP server configured")
            return None

        server_type = server_config.get("type")
        config = server_config.get("config", {})

        if server_type == "browserbase":
            return self._connect_browserbase(config)
        elif server_type == "playwright":
            return self._connect_playwright(config)
        elif server_type == "cursor-ide-browser":
            return self._connect_cursor_ide_browser(config)
        else:
            logger.warning(f"Unknown server type: {server_type}")
            return None

    def _connect_browserbase(self, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Connect to Browserbase MCP server."""
        # Browserbase tools would be available via MCP protocol
        # This is a placeholder for actual MCP server connection
        logger.info("Connecting to Browserbase MCP server...")

        # In a real implementation, this would:
        # 1. Connect to MCP server via stdio or HTTP
        # 2. List available tools
        # 3. Return tool functions

        return None

    def _connect_playwright(self, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Connect to Playwright MCP server or use Playwright directly."""
        logger.info("Connecting to Playwright MCP server...")

        # Try to get tools from running MCP server first
        # If that fails, use Playwright Python library directly as fallback
        try:
            # Check if Playwright Python library is available
            try:
                from playwright.sync_api import Browser, Page, sync_playwright  # noqa: F401

                logger.info("Playwright Python library found - using direct Playwright integration")

                # Create Playwright tool wrappers
                playwright_tools = self._create_playwright_tools()
                if playwright_tools:
                    logger.info(f"Created {len(playwright_tools)} Playwright tools")
                    return playwright_tools
            except ImportError:
                logger.warning(
                    "Playwright Python library not installed. Install with: pip install playwright && playwright install"
                )
                logger.info("Attempting to use MCP server connection...")

                # Try to connect to MCP server via stdio
                # This would require implementing MCP JSON-RPC client
                # For now, return None and let the user know they need Playwright installed
                return None

        except Exception as e:
            logger.error(f"Error connecting to Playwright: {e}")
            return None

    def _create_playwright_tools(self) -> Optional[Dict[str, Any]]:
        """Create Playwright tool wrappers using Playwright Python library."""
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
                                "location": "mcp_server_config.py:_create_playwright_tools:entry",
                                "message": "Creating Playwright tools",
                                "data": {},
                                "timestamp": int(__import__("time").time() * 1000),
                            }
                        )
                        + "\n"
                    )
            except Exception:
                pass
            # #endregion

            import threading

            from playwright.sync_api import Browser, Page, sync_playwright  # noqa: F401

            # #region agent log
            try:
                with open("/tmp/grant_automation_debug.log", "a") as f:
                    f.write(
                        json.dumps(
                            {
                                "sessionId": "debug-session",
                                "runId": "post-fix-v2",
                                "hypothesisId": "H2",
                                "location": "mcp_server_config.py:_create_playwright_tools:import_success",
                                "message": "Playwright imported successfully",
                                "data": {},
                                "timestamp": int(__import__("time").time() * 1000),
                            }
                        )
                        + "\n"
                    )
            except Exception:
                pass
            # #endregion

            # Global Playwright context
            _playwright_context = {
                "playwright": None,
                "browser": None,
                "page": None,
                "lock": threading.Lock(),
            }

            def init_playwright():
                """Initialize Playwright browser."""
                with _playwright_context["lock"]:
                    if _playwright_context["playwright"] is None:
                        try:
                            _playwright_context["playwright"] = sync_playwright().start()
                            _playwright_context["browser"] = _playwright_context[
                                "playwright"
                            ].chromium.launch(headless=False)
                            _playwright_context["page"] = _playwright_context["browser"].new_page()
                            logger.info("Playwright browser initialized")
                        except Exception as e:
                            logger.error(f"Failed to initialize Playwright: {e}")
                            logger.error(
                                "Make sure Playwright is installed: pip install playwright && playwright install"
                            )
                            raise

            def playwright_navigate(url: str) -> bool:
                """Navigate to URL."""
                try:
                    init_playwright()
                    _playwright_context["page"].goto(url)
                    logger.info(f"Navigated to {url}")
                    return True
                except Exception as e:
                    logger.error(f"Navigation error: {e}")
                    return False

            def playwright_click(selector_or_description: str) -> bool:
                """Click element by selector or description."""
                import re

                try:
                    init_playwright()
                    page = _playwright_context["page"]

                    # Check if it looks like a CSS selector
                    is_likely_selector = (
                        selector_or_description.startswith("#")
                        or selector_or_description.startswith(".")
                        or selector_or_description.startswith("[")
                        or (
                            len(selector_or_description.split()) == 1
                            and not any(
                                word in selector_or_description.lower()
                                for word in ["button", "link", "login", "sign", "submit", "click"]
                            )
                        )
                    )

                    # Try as selector first only if it looks like a selector
                    if is_likely_selector:
                        try:
                            page.click(selector_or_description, timeout=2000)
                            logger.info(f"Clicked: {selector_or_description} (as selector)")
                            return True
                        except:
                            pass  # Fall through to description-based approaches

                    # Description-based approaches (for text descriptions like "login button")
                    desc_lower = selector_or_description.lower()

                    # Extract key words from description
                    keywords = [
                        word
                        for word in desc_lower.split()
                        if word not in ["the", "a", "an", "or", "and", "button", "link", "element"]
                    ]
                    if not keywords:
                        keywords = desc_lower.split()

                    # Strategy 1: For login/submit buttons, try form submission FIRST (most reliable)
                    if "login" in desc_lower or "sign" in desc_lower or "submit" in desc_lower:
                        # Try form submission methods first
                        form_submit_approaches = [
                            # Method 1: Submit form directly via JavaScript (most reliable)
                            lambda: page.evaluate("""() => {
                                const form = document.querySelector('form');
                                if (form) {
                                    form.submit();
                                    return true;
                                }
                                return false;
                            }"""),
                            # Method 2: Find form and submit via evaluate
                            lambda: page.locator("form").first.evaluate("form => form.submit()"),
                            # Method 3: Press Enter on password field (common form submission)
                            lambda: page.locator('input[type="password"]').first.press("Enter"),
                        ]

                        for i, approach in enumerate(form_submit_approaches, 1):
                            try:
                                result = approach()
                                if result or i > 1:  # First approach returns bool, others don't
                                    logger.info(
                                        f"Submitted form using method {i}: {selector_or_description}"
                                    )
                                    return True
                            except Exception as e:
                                logger.debug(f"Form submit method {i} failed: {e}")
                                continue

                    # Strategy 2: Try by role (button, link) - only if form submission didn't work
                    if (
                        "button" in desc_lower
                        or "login" in desc_lower
                        or "sign" in desc_lower
                        or "submit" in desc_lower
                    ):
                        approaches = [
                            # Try submit button first (most common for forms)
                            lambda: page.locator('button[type="submit"]').first.click(timeout=3000),
                            lambda: page.locator('input[type="submit"]').first.click(timeout=3000),
                            # Try exact button text matches
                            lambda: page.get_by_role("button", name="login", exact=False).click(
                                timeout=3000
                            ),
                            lambda: page.get_by_role("button", name="sign in", exact=False).click(
                                timeout=3000
                            ),
                            lambda: page.get_by_role("button", name="Sign In", exact=False).click(
                                timeout=3000
                            ),
                            lambda: page.get_by_role("button", name="Log In", exact=False).click(
                                timeout=3000
                            ),
                            lambda: page.get_by_role("button", name="submit", exact=False).click(
                                timeout=3000
                            ),
                            # Try by text content in button (case insensitive)
                            lambda: (
                                page.locator("button")
                                .filter(has_text=re.compile(r"login|sign.*in", re.I))
                                .first.click(timeout=3000)
                            ),
                            # Try with keywords
                            lambda: page.get_by_role(
                                "button",
                                name=lambda name: (
                                    name
                                    and any(kw in name.lower() for kw in keywords if len(kw) > 2)
                                ),
                                exact=False,
                            ).first.click(timeout=3000),
                            # Try any button in form
                            lambda: page.locator("form button").first.click(timeout=3000),
                            # Try any button
                            lambda: page.get_by_role("button").first.click(timeout=3000),
                            lambda: page.locator("button").first.click(timeout=3000),
                        ]
                        for i, approach in enumerate(approaches):
                            try:
                                approach()
                                logger.info(f"Clicked button: {selector_or_description}")
                                return True
                            except Exception as e:
                                logger.debug(f"Click approach failed: {e}")
                                continue

                    # Strategy 3: Try by text content (for links or any clickable element)
                    approaches = [
                        lambda: page.get_by_text(
                            keywords[0] if keywords else selector_or_description, exact=False
                        ).first.click(timeout=2000),
                        lambda: page.get_by_text(selector_or_description, exact=False).first.click(
                            timeout=2000
                        ),
                        lambda: page.locator(
                            f"text={keywords[0] if keywords else selector_or_description}"
                        ).first.click(timeout=2000),
                    ]
                    for approach in approaches:
                        try:
                            approach()
                            logger.info(f"Clicked by text: {selector_or_description}")
                            return True
                        except:
                            continue

                    # Strategy 4: Try by link role
                    if "link" in desc_lower:
                        try:
                            page.get_by_role(
                                "link",
                                name=lambda name: (
                                    name
                                    and any(kw in name.lower() for kw in keywords if len(kw) > 2)
                                ),
                                exact=False,
                            ).first.click(timeout=2000)
                            logger.info(f"Clicked link: {selector_or_description}")
                            return True
                        except:
                            pass

                    logger.warning(f"Could not click: {selector_or_description}")
                    return False
                except Exception as e:
                    logger.error(f"Click error: {e}")
                    import traceback

                    logger.debug(traceback.format_exc())
                    return False

            def playwright_fill(selector_or_description: str, text: str) -> bool:
                """Fill input field by selector or description."""
                try:
                    init_playwright()
                    page = _playwright_context["page"]

                    # Check if it looks like a CSS selector (starts with #, ., [, or is a simple tag)
                    is_likely_selector = (
                        selector_or_description.startswith("#")
                        or selector_or_description.startswith(".")
                        or selector_or_description.startswith("[")
                        or selector_or_description.startswith("input")
                        or selector_or_description.startswith("button")
                        or len(selector_or_description.split()) == 1
                        and not any(
                            word in selector_or_description.lower()
                            for word in [
                                "field",
                                "input",
                                "button",
                                "username",
                                "password",
                                "email",
                            ]
                        )
                    )

                    # Try as selector first only if it looks like a selector
                    if is_likely_selector:
                        try:
                            page.fill(selector_or_description, text, timeout=2000)
                            logger.info(f"Filled {selector_or_description} with text (as selector)")
                            return True
                        except:
                            pass  # Fall through to description-based approaches

                    # Description-based approaches (for text descriptions like "username input field")
                    desc_lower = selector_or_description.lower()

                    if "username" in desc_lower or "email" in desc_lower:
                        # Try multiple approaches for username/email
                        approaches = [
                            lambda: page.get_by_label("username", exact=False).fill(text),
                            lambda: page.get_by_label("email", exact=False).fill(text),
                            lambda: page.get_by_placeholder("username", exact=False).fill(text),
                            lambda: page.get_by_placeholder("email", exact=False).fill(text),
                            lambda: page.get_by_placeholder("Email", exact=False).fill(text),
                            lambda: page.locator('input[type="email"]').first.fill(text),
                            lambda: page.locator('input[type="text"]').first.fill(text),
                            lambda: page.locator(
                                'input[name*="user" i], input[name*="email" i]'
                            ).first.fill(text),
                            lambda: page.locator(
                                'input[id*="user" i], input[id*="email" i]'
                            ).first.fill(text),
                        ]
                        for approach in approaches:
                            try:
                                approach()
                                logger.info(
                                    f"Filled username/email field using {approach.__name__}"
                                )
                                return True
                            except:
                                continue

                    if "password" in desc_lower:
                        # Try multiple approaches for password
                        approaches = [
                            lambda: page.get_by_label("password", exact=False).fill(text),
                            lambda: page.get_by_placeholder("password", exact=False).fill(text),
                            lambda: page.get_by_placeholder("Password", exact=False).fill(text),
                            lambda: page.locator('input[type="password"]').fill(text),
                            lambda: page.locator('input[name*="pass" i]').first.fill(text),
                            lambda: page.locator('input[id*="pass" i]').first.fill(text),
                        ]
                        for approach in approaches:
                            try:
                                approach()
                                logger.info(f"Filled password field using {approach.__name__}")
                                return True
                            except:
                                continue

                    # Generic fallback - try first input field
                    try:
                        page.locator("input").first.fill(text)
                        logger.info(f"Filled first input field: {selector_or_description}")
                        return True
                    except:
                        pass

                    logger.warning(f"Could not fill: {selector_or_description}")
                    return False
                except Exception as e:
                    logger.error(f"Fill error: {e}")
                    import traceback

                    logger.debug(traceback.format_exc())
                    return False

            def playwright_snapshot() -> Dict[str, Any]:
                """Get page snapshot."""
                try:
                    init_playwright()
                    content = _playwright_context["page"].content()
                    return {"content": content, "url": _playwright_context["page"].url}
                except Exception as e:
                    logger.error(f"Snapshot error: {e}")
                    return {}

            def playwright_screenshot(name: str = "screenshot") -> str:
                """Take screenshot."""
                try:
                    init_playwright()
                    screenshot_path = f"agents/grant_scraper/screenshots/{name}.png"
                    Path(screenshot_path).parent.mkdir(parents=True, exist_ok=True)
                    _playwright_context["page"].screenshot(path=screenshot_path)
                    logger.info(f"Screenshot saved: {screenshot_path}")
                    return screenshot_path
                except Exception as e:
                    logger.error(f"Screenshot error: {e}")
                    return ""

            def playwright_get_url() -> str:
                """Get current URL."""
                try:
                    init_playwright()
                    return _playwright_context["page"].url
                except Exception as e:
                    logger.error(f"Get URL error: {e}")
                    return ""

            def playwright_wait(time_seconds: float = 1.0):
                """Wait for specified time."""
                import time

                time.sleep(time_seconds)

            def playwright_close():
                """Close browser."""
                try:
                    with _playwright_context["lock"]:
                        if _playwright_context["browser"]:
                            _playwright_context["browser"].close()
                        if _playwright_context["playwright"]:
                            _playwright_context["playwright"].stop()
                        _playwright_context["browser"] = None
                        _playwright_context["page"] = None
                        _playwright_context["playwright"] = None
                        logger.info("Playwright browser closed")
                except Exception as e:
                    logger.error(f"Close error: {e}")

            # Wrapper function for browser_type to convert keyword args to positional for playwright_fill
            def browser_type_wrapper(desc=None, txt=None, elem_ref=None, **kwargs):
                """Wrapper to convert browser_type signature to playwright_fill signature."""
                # Extract description and text from various possible parameter names
                description = desc or kwargs.get("description") or kwargs.get("desc") or ""
                text = txt or kwargs.get("text") or ""

                if not description or not text:
                    return False

                # Call playwright_fill with positional arguments only
                return playwright_fill(str(description), str(text))

            # Return tool dictionary matching expected MCP tool names
            tools = {
                "playwright_navigate": playwright_navigate,
                "playwright_click": playwright_click,
                "playwright_fill": playwright_fill,
                "playwright_snapshot": playwright_snapshot,
                "playwright_screenshot": playwright_screenshot,
                "playwright_get_url": playwright_get_url,
                "playwright_wait": playwright_wait,
                "playwright_close": playwright_close,
                # Also add aliases for compatibility
                "browser_navigate": playwright_navigate,
                "browser_click": playwright_click,
                "browser_type": browser_type_wrapper,
                "browser_take_snapshot": playwright_snapshot,
                "browser_take_screenshot": playwright_screenshot,
                "browser_get_url": playwright_get_url,
                "browser_wait": playwright_wait,
                "browser_close": playwright_close,
            }

            # #region agent log
            try:
                with open("/tmp/grant_automation_debug.log", "a") as f:
                    f.write(
                        json.dumps(
                            {
                                "sessionId": "debug-session",
                                "runId": "post-fix-v2",
                                "hypothesisId": "H2",
                                "location": "mcp_server_config.py:_create_playwright_tools:success",
                                "message": "Playwright tools created",
                                "data": {"tool_count": len(tools), "tool_keys": list(tools.keys())},
                                "timestamp": int(__import__("time").time() * 1000),
                            }
                        )
                        + "\n"
                    )
            except Exception:
                pass
            # #endregion

            return tools

        except ImportError:
            logger.error(
                "Playwright not installed. Install with: pip install playwright && playwright install"
            )
            return None
        except Exception as e:
            logger.error(f"Error creating Playwright tools: {e}")
            return None

    def _connect_cursor_ide_browser(self, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Connect to Cursor IDE browser MCP server."""
        logger.info("Connecting to Cursor IDE browser MCP server...")

        # Cursor IDE browser tools are available via tool calling interface
        # Try to get them from the environment

        from .mcp_tools_helper import get_mcp_tools_from_environment

        tools = get_mcp_tools_from_environment()

        if tools:
            logger.info(f"Found {len(tools)} Cursor IDE browser tools from environment")
            return tools

        # If not found, return expected tool structure
        # These will be injected when tools are actually available
        expected_tools = {
            "mcp_cursor-ide-browser_browser_navigate": "cursor_ide_browser_navigate",
            "mcp_cursor-ide-browser_browser_snapshot": "cursor_ide_browser_snapshot",
            "mcp_cursor-ide-browser_browser_click": "cursor_ide_browser_click",
            "mcp_cursor-ide-browser_browser_type": "cursor_ide_browser_type",
            "mcp_cursor-ide-browser_browser_select_option": "cursor_ide_browser_select_option",
            "mcp_cursor-ide-browser_browser_wait_for": "cursor_ide_browser_wait_for",
            "mcp_cursor-ide-browser_browser_take_screenshot": "cursor_ide_browser_take_screenshot",
        }

        logger.info(f"Expected {len(expected_tools)} Cursor IDE browser tools")
        # Return None since tools aren't actually available yet
        return None

    def setup_default_config(self):
        """Set up default MCP server configuration."""
        if not self.config.get("servers"):
            # Add Cursor IDE browser as default
            self.add_server(
                name="cursor-ide-browser",
                server_type="cursor-ide-browser",
                config={"description": "Cursor IDE built-in browser tools", "auto_detect": True},
            )
            self.config["default_server"] = "cursor-ide-browser"
            self._save_config()
            logger.info("Set up default MCP server configuration")


def configure_mcp_server_interactive():
    """
    Interactive MCP server configuration.
    Guides user through setting up MCP server.
    """
    print("=" * 60)
    print("MCP Server Configuration")
    print("=" * 60)

    config = MCPServerConfig()

    print("\n1. Server Type Selection:")
    print("   a) Cursor IDE Browser (built-in, recommended for Cursor IDE)")
    print("   b) Playwright MCP (local browser automation, recommended)")
    print("   c) Browserbase/Stagehand (requires API key)")
    print("   d) Custom MCP Server")

    choice = input("\nSelect option (a/b/c/d): ").strip().lower()

    if choice == "a":
        server_name = "cursor-ide-browser"
        server_type = "cursor-ide-browser"
        server_config = {"description": "Cursor IDE built-in browser tools", "auto_detect": True}
        config.add_server(server_name, server_type, server_config)
        config.config["default_server"] = server_name
        config._save_config()
        print(f"\n✅ Configured {server_name} as default MCP server")

    elif choice == "b":
        server_name = input("Server name (default: playwright): ").strip() or "playwright"

        server_config = {
            "package": "@playwright/mcp@latest",
            "command": "npx",
            "description": "Playwright MCP browser automation (local)",
        }
        config.add_server(server_name, "playwright", server_config)
        config.config["default_server"] = server_name
        config._save_config()
        print(f"\n✅ Configured {server_name} as default MCP server")
        print("   Playwright MCP will be started with: npx @playwright/mcp@latest")

    elif choice == "c":
        server_name = input("Server name (default: browserbase): ").strip() or "browserbase"
        api_key = input("Browserbase API key (optional): ").strip()

        server_config = {
            "api_key": api_key if api_key else None,
            "description": "Browserbase/Stagehand browser automation",
        }
        config.add_server(server_name, "browserbase", server_config)
        config.config["default_server"] = server_name
        config._save_config()
        print(f"\n✅ Configured {server_name} as default MCP server")

    elif choice == "d":
        server_name = input("Server name: ").strip()
        server_type = input("Server type: ").strip()
        server_url = input("Server URL or command: ").strip()

        server_config = {"url": server_url, "description": "Custom MCP server"}
        config.add_server(server_name, server_type, server_config)
        config.config["default_server"] = server_name
        config._save_config()
        print(f"\n✅ Configured {server_name} as default MCP server")

    print("\nConfiguration saved!")
    print(f"Config file: {config.config_path}")


def get_mcp_tools_from_server(server_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Get MCP tools from configured server.

    Args:
        server_name: Server name (uses default if not provided)

    Returns:
        Dictionary of MCP tool functions or None
    """
    config = MCPServerConfig()

    # Setup default if no config exists
    if not config.config.get("servers"):
        config.setup_default_config()

    tools = config.connect_to_server(server_name)

    if tools:
        # Inject tools into the helper
        from .inject_mcp_tools import inject_available_mcp_tools

        inject_available_mcp_tools(tools)
        logger.info(f"Loaded {len(tools)} tools from MCP server")
        return tools

    return None
