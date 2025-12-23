"""
Complete SDK CLI for 4Culture Grant Application Automation
Provides individual step commands and workflow orchestration.
"""

import argparse
import sys
import logging
import json
import os
from pathlib import Path
from typing import Optional, List, Dict, Any

try:
    import yaml
except ImportError:
    yaml = None

from .automation_workflow import AutomationWorkflow
from .data_extractor import DataExtractor
from .form_mapper import FormMapper
from .application_automator import ApplicationAutomator
from .grant_database import GrantDatabase
from .grant_dashboard import GrantDashboard
from .workflow_state import WorkflowState

# Import narrative generator if available
try:
    from .narrative_generator import NarrativeGenerator
except ImportError:
    NarrativeGenerator = None

# Import MCP browser integration
try:
    from .mcp_browser_integration import MCPBrowserIntegration
except ImportError:
    MCPBrowserIntegration = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GrantSDKCLI:
    """Complete SDK CLI for grant application automation."""
    
    def __init__(self):
        """Initialize the SDK CLI."""
        self.workflow_state: Optional[WorkflowState] = None
        self.mcp_tools: Optional[Dict[str, Any]] = None
        self.output_format = 'human'  # human, json, yaml
    
    def _get_mcp_browser_tools(self) -> Optional[Dict[str, Any]]:
        """Collect available MCP browser tools from multiple sources."""
        try:
            from .mcp_tools_helper import (
                collect_mcp_browser_tools,
                get_mcp_tools_from_environment,
                inject_mcp_tools
            )
            
            # Try comprehensive collection first
            mcp_tools = collect_mcp_browser_tools()
            
            if not mcp_tools:
                # Try environment-based collection
                mcp_tools = get_mcp_tools_from_environment()
            
            # If still no tools, try MCP server configuration
            if not mcp_tools:
                try:
                    from .inject_mcp_tools import inject_tools_from_mcp_server, setup_mcp_tools_auto
                    # Try automatic setup
                    if setup_mcp_tools_auto():
                        # Retry collection after injection
                        mcp_tools = collect_mcp_browser_tools()
                except Exception as e:
                    logger.debug(f"Could not set up MCP server: {e}")
            
            # If still no tools, try to create from Cursor IDE environment
            if not mcp_tools:
                try:
                    from .inject_mcp_tools import create_mcp_tools_from_cursor_functions
                    mcp_tools = create_mcp_tools_from_cursor_functions()
                except Exception as e:
                    logger.debug(f"Could not create Cursor tools: {e}")
            
            if mcp_tools:
                logger.info(f"Found {len(mcp_tools)} MCP browser tools")
                return mcp_tools
            
            # If still no tools, provide helpful message with setup instructions
            logger.warning("MCP browser tools not found in Python namespace")
            logger.info("")
            logger.info("To enable MCP tools, use one of these methods:")
            logger.info("")
            logger.info("Method 1: Configure MCP Server")
            logger.info("  python3 -m agents.grant_scraper.mcp_server_config")
            logger.info("")
            logger.info("Method 2: Inject Tools Manually")
            logger.info("  from agents.grant_scraper.inject_mcp_tools import inject_tools_from_dict")
            logger.info("  inject_tools_from_dict({'cursor_ide_browser_navigate': your_function, ...})")
            logger.info("")
            logger.info("Method 3: Use in Cursor IDE (automatic)")
            logger.info("  MCP tools are automatically available in Cursor IDE")
            logger.info("")
            
            return None
        except Exception as e:
            logger.warning(f"Could not access MCP browser tools: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return None
    
    def _output(self, data: Any, title: Optional[str] = None):
        """Output data in the configured format."""
        if self.output_format == 'json':
            print(json.dumps(data, indent=2, default=str))
        elif self.output_format == 'yaml':
            if yaml:
                try:
                    print(yaml.dump(data, default_flow_style=False))
                except:
                    print(json.dumps(data, indent=2, default=str))
            else:
                print(json.dumps(data, indent=2, default=str))
        else:  # human
            if title:
                print(f"\n=== {title} ===")
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, (dict, list)):
                        print(f"{key}:")
                        print(json.dumps(value, indent=2, default=str))
                    else:
                        print(f"{key}: {value}")
            elif isinstance(data, list):
                for item in data:
                    print(json.dumps(item, indent=2, default=str))
            else:
                print(data)
    
    def _error(self, message: str, code: int = 1):
        """Output error and exit."""
        if self.output_format == 'json':
            print(json.dumps({'error': message, 'code': code}))
        else:
            print(f"❌ Error: {message}", file=sys.stderr)
        sys.exit(code)
    
    def _prompt_yes_no(self, message: str, default: Optional[bool] = None) -> bool:
        """Prompt user for yes/no confirmation."""
        if self.output_format != 'human':
            # In non-human mode, use default or True
            return default if default is not None else True
        
        while True:
            prompt = f"{message} [y/n]"
            if default is not None:
                prompt += f" (default: {'y' if default else 'n'})"
            prompt += ": "
            
            try:
                response = input(prompt).strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\n❌ Operation cancelled by user")
                sys.exit(130)
            
            if not response and default is not None:
                return default
            
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print("Please enter 'y' or 'n'")
    
    def _prompt_choice(self, message: str, choices: List[str], 
                       default: Optional[str] = None) -> str:
        """Prompt user to select from choices."""
        if self.output_format != 'human':
            # In non-human mode, use default or first choice
            return default if default else choices[0]
        
        while True:
            print(f"\n{message}")
            for i, choice in enumerate(choices, 1):
                marker = " (default)" if choice == default else ""
                print(f"  {i}) {choice}{marker}")
            
            if default:
                default_idx = choices.index(default) + 1
                prompt = f"Enter choice [1-{len(choices)}] (default: {default_idx}): "
            else:
                prompt = f"Enter choice [1-{len(choices)}]: "
            
            try:
                response = input(prompt).strip()
            except (EOFError, KeyboardInterrupt):
                print("\n❌ Operation cancelled by user")
                sys.exit(130)
            
            if not response and default:
                return default
            
            try:
                idx = int(response) - 1
                if 0 <= idx < len(choices):
                    return choices[idx]
            except ValueError:
                pass
            
            print(f"Please enter a number between 1 and {len(choices)}")
    
    def _print_step_header(self, step_num: int, step_name: str, description: str = ""):
        """Print formatted step header."""
        if self.output_format == 'human':
            print(f"\n{'='*60}")
            print(f"Step {step_num}: {step_name}")
            print(f"{'-'*60}")
            if description:
                print(f"{description}\n")
    
    def _interactive_mcp_setup(self, non_interactive: bool = False) -> Optional[Dict[str, Any]]:
        """Interactively set up MCP tools with user confirmation."""
        # Step 1: Check for existing tools
        print("Checking for MCP browser tools...")
        mcp_tools = self._get_mcp_browser_tools()
        
        if mcp_tools:
            print("✅ MCP browser tools already available")
            if non_interactive or self._prompt_yes_no("Use existing tools?", default=True):
                return mcp_tools
        
        # Step 2: Check for configured servers
        try:
            from .mcp_server_config import MCPServerConfig
            config = MCPServerConfig()
            servers = config.list_servers()
            
            if not servers:
                print("❌ No MCP servers configured")
                if non_interactive:
                    return None
                
                if self._prompt_yes_no("Would you like to configure a server now?"):
                    try:
                        from .mcp_server_config import configure_mcp_server_interactive
                        configure_mcp_server_interactive()
                        servers = config.list_servers()
                    except Exception as e:
                        logger.error(f"Error configuring server: {e}")
                        return None
                else:
                    return None
            
            # Step 3: Select server
            print("\nAvailable MCP servers:")
            server_names = []
            for i, server_name in enumerate(servers, 1):
                server_config = config.get_server_config(server_name)
                server_type = server_config.get('type', 'unknown') if server_config else 'unknown'
                server_names.append(server_name)
                if server_type == 'cursor-ide-browser':
                    status = "built-in (Cursor IDE only)"
                elif server_type == 'playwright':
                    status = "local browser (recommended)"
                else:
                    status = "external"
                print(f"  {i}. {server_name} ({server_type}, {status})")
            
            if non_interactive:
                selected_server = server_names[0] if server_names else None
            else:
                selected_choice = self._prompt_choice(
                    "Select a server to use:",
                    server_names,
                    default=server_names[0] if server_names else None
                )
                selected_server = selected_choice
            
            if not selected_server:
                return None
            
            # Step 4: Start server if needed
            from .mcp_server_runner import MCPServerRunner
            runner = MCPServerRunner()
            
            # Check if server is running
            running_servers = runner.list_running_servers()
            server_running = any(s['name'] == selected_server for s in running_servers)
            
            server_config = config.get_server_config(selected_server)
            server_type = server_config.get('type') if server_config else None
            
            if server_type == 'playwright':
                # Playwright MCP needs to be started
                if not server_running:
                    print(f"⚠️  Playwright MCP server is not running")
                    if non_interactive or self._prompt_yes_no(f"Start Playwright MCP server now?", default=True):
                        success = runner.start_server(server_name=selected_server)
                        if not success:
                            print(f"❌ Failed to start Playwright MCP server")
                            print("   Make sure npx is installed: npm install -g npx")
                            return None
                        print(f"✅ Playwright MCP server started")
                        # Wait a moment for server to initialize
                        import time
                        time.sleep(2)
                
                # Inject tools - Playwright uses direct Python library, not MCP server
                if non_interactive or self._prompt_yes_no("Initialize Playwright browser tools?", default=True):
                    try:
                        from .mcp_server_config import get_mcp_tools_from_server
                        print("Attempting to get Playwright tools...")
                        tools = get_mcp_tools_from_server(selected_server)
                        if tools:
                            # Tools are already injected by get_mcp_tools_from_server
                            # Retry collection
                            mcp_tools = self._get_mcp_browser_tools()
                            if mcp_tools:
                                print(f"✅ Successfully initialized {len(mcp_tools)} Playwright browser tools")
                                return mcp_tools
                            else:
                                print("⚠️  Tools were created but could not be collected.")
                                print("   This may indicate Playwright is not installed.")
                                print("   Install with: pip install playwright && playwright install")
                                if not non_interactive:
                                    if self._prompt_yes_no("Continue anyway? (login will fail without tools)", default=False):
                                        return None
                        else:
                            print("⚠️  Could not initialize Playwright browser tools.")
                            print("   Make sure Playwright is installed: pip install playwright && playwright install")
                            if not non_interactive:
                                if self._prompt_yes_no("Continue anyway? (login will fail without tools)", default=False):
                                    return None
                    except Exception as e:
                        logger.error(f"Error initializing Playwright tools: {e}")
                        print(f"❌ Error during Playwright initialization: {e}")
                        print("   Install Playwright with: pip install playwright && playwright install")
                        if not non_interactive:
                            if self._prompt_yes_no("Continue anyway? (login will fail without tools)", default=False):
                                return None
                else:
                    print("⚠️  Playwright initialization skipped. MCP tools are required for browser automation.")
                    if not non_interactive:
                        if self._prompt_yes_no("Continue anyway? (login will fail without tools)", default=False):
                            return None
            
            elif server_type == 'cursor-ide-browser':
                print(f"✅ {selected_server} is available (built-in)")
                if non_interactive or self._prompt_yes_no("Inject tools from this server?", default=True):
                    try:
                        from .inject_mcp_tools import inject_tools_from_mcp_server
                        print("Attempting to inject tools...")
                        if inject_tools_from_mcp_server(selected_server):
                            # Retry collection
                            mcp_tools = self._get_mcp_browser_tools()
                            if mcp_tools:
                                print(f"✅ Successfully injected {len(mcp_tools)} MCP browser tools")
                                return mcp_tools
                            else:
                                print("⚠️  Tools were injected but could not be collected.")
                                print("   This usually means you're not running in Cursor IDE.")
                                print("   Cursor IDE browser tools are only available when running inside Cursor IDE.")
                                if not non_interactive:
                                    if self._prompt_yes_no("Continue anyway? (login will fail without tools)", default=False):
                                        return None
                        else:
                            print("⚠️  Could not inject tools from server.")
                            print("   Cursor IDE browser tools are only available when running inside Cursor IDE.")
                            if not non_interactive:
                                if self._prompt_yes_no("Continue anyway? (login will fail without tools)", default=False):
                                    return None
                    except Exception as e:
                        logger.error(f"Error injecting tools: {e}")
                        print(f"❌ Error during tool injection: {e}")
                        if not non_interactive:
                            if self._prompt_yes_no("Continue anyway? (login will fail without tools)", default=False):
                                return None
                else:
                    print("⚠️  Tool injection skipped. MCP tools are required for browser automation.")
                    if not non_interactive:
                        if self._prompt_yes_no("Continue anyway? (login will fail without tools)", default=False):
                            return None
            else:
                if not server_running:
                    print(f"⚠️  Server '{selected_server}' is not running")
                    if non_interactive or self._prompt_yes_no(f"Start server '{selected_server}' now?", default=True):
                        success = runner.start_server(server_name=selected_server)
                        if not success:
                            print(f"❌ Failed to start server '{selected_server}'")
                            return None
                        print(f"✅ Server '{selected_server}' started")
                
                # Inject tools
                if non_interactive or self._prompt_yes_no("Inject tools from server?", default=True):
                    try:
                        from .inject_mcp_tools import inject_tools_from_mcp_server
                        print("Attempting to inject tools...")
                        if inject_tools_from_mcp_server(selected_server):
                            # Retry collection
                            mcp_tools = self._get_mcp_browser_tools()
                            if mcp_tools:
                                print(f"✅ Successfully injected {len(mcp_tools)} MCP browser tools")
                                return mcp_tools
                            else:
                                print("⚠️  Tools were injected but could not be collected.")
                                print("   Please check server connection and try again.")
                                if not non_interactive:
                                    if self._prompt_yes_no("Continue anyway? (login will fail without tools)", default=False):
                                        return None
                        else:
                            print("⚠️  Could not inject tools from server.")
                            print("   Please check server connection and configuration.")
                            if not non_interactive:
                                if self._prompt_yes_no("Continue anyway? (login will fail without tools)", default=False):
                                    return None
                    except Exception as e:
                        logger.error(f"Error injecting tools: {e}")
                        print(f"❌ Error during tool injection: {e}")
                        if not non_interactive:
                            if self._prompt_yes_no("Continue anyway? (login will fail without tools)", default=False):
                                return None
                else:
                    print("⚠️  Tool injection skipped. MCP tools are required for browser automation.")
                    if not non_interactive:
                        if self._prompt_yes_no("Continue anyway? (login will fail without tools)", default=False):
                            return None
            
            return None
            
        except Exception as e:
            logger.error(f"Error during MCP setup: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return None
    
    # ==================== AUTH COMMANDS ====================
    
    def cmd_auth_login(self, args):
        """Interactive login to 4Culture portal."""
        non_interactive = getattr(args, 'non_interactive', False)
        skip_mcp_setup = getattr(args, 'skip_mcp_setup', False)
        skip_verification = getattr(args, 'skip_verification', False)
        
        if self.output_format == 'human':
            print("\n" + "="*60)
            print("4Culture Grant Application - Interactive Login Setup")
            print("="*60)
        
        # Step 1: MCP Tools Check
        self._print_step_header(1, "MCP Tools Check", 
                               "Checking for MCP browser tools...")
        
        if skip_mcp_setup:
            mcp_tools = self._get_mcp_browser_tools()
            if not mcp_tools:
                self._error("MCP browser tools not available. Use interactive mode to set them up.", 3)
        else:
            mcp_tools = self._interactive_mcp_setup(non_interactive=non_interactive)
        
        if not mcp_tools:
            error_msg = (
                "MCP tools are required for browser automation.\n\n"
                "To set up MCP tools manually, run:\n"
                "  python3 -m agents.grant_scraper.mcp_setup_cli configure\n\n"
                "Or run this command in Cursor IDE where tools are automatically available."
            )
            self._error(error_msg, 3)
        
        # Step 2: Browser Initialization
        self._print_step_header(2, "Browser Initialization",
                               "Ready to initialize browser.")
        
        if not non_interactive:
            if not self._prompt_yes_no("Initialize browser now?", default=True):
                self._error("Browser initialization required", 3)
        
        username = args.username or os.getenv('4CULTURE_USERNAME', 'Keyisaccess')
        password = args.password or os.getenv('4CULTURE_PASSWORD', 'Outlaw22!!')
        
        automator = ApplicationAutomator(username, password, mcp_tools=mcp_tools)
        print("✅ Browser initialized successfully")
        
        # Step 3: Credentials Confirmation
        self._print_step_header(3, "Login Credentials")
        print(f"Using credentials:")
        print(f"  Username: {username}")
        print(f"  Password: {'*' * len(password)}")
        
        if not non_interactive:
            cred_choices = [
                "Use these credentials",
                "Enter different credentials",
                "Use environment variables"
            ]
            cred_choice = self._prompt_choice(
                "Would you like to:",
                cred_choices,
                default=cred_choices[0]
            )
            
            if cred_choice == cred_choices[1]:
                username = input("Enter username: ").strip()
                import getpass
                password = getpass.getpass("Enter password: ")
            elif cred_choice == cred_choices[2]:
                username = os.getenv('4CULTURE_USERNAME', username)
                password = os.getenv('4CULTURE_PASSWORD', password)
        
        # Update automator with potentially new credentials
        automator.username = username
        automator.password = password
        
        # Step 4: Navigate to Login Page
        self._print_step_header(4, "Navigate to Login Page")
        print(f"Ready to navigate to: https://apply.4culture.org/login")
        
        if not non_interactive:
            if not self._prompt_yes_no("Continue?", default=True):
                self._error("Navigation required", 3)
        
        print("Navigating...")
        if not automator.browser.navigate("https://apply.4culture.org/login"):
            self._error("Failed to navigate to login page", 4)
        automator.browser.wait_for(time_seconds=2)
        print("✅ Successfully navigated to login page")
        
        # Step 5: Fill Login Form
        self._print_step_header(5, "Fill Login Form")
        print("Ready to fill login form with credentials.")
        
        if not non_interactive:
            if not self._prompt_yes_no("Continue?", default=True):
                self._error("Form filling required", 3)
        
        print("Filling username...")
        # #region agent log
        import json
        with open('/Users/russellpowers/Grants/.cursor/debug.log', 'a') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"post-fix","hypothesisId":"H1,H2,H5","location":"sdk_cli.py:cmd_auth_login:before_type_username","message":"Before typing username (skipping find_element check)","data":{},"timestamp":int(__import__('time').time()*1000)}) + '\n')
        # #endregion
        # For Playwright, type_text can work directly without needing find_element first
        # The type_text method will handle element finding internally using Playwright's locator API
        success = automator.browser.type_text("username input field or email input field", username)
        if not success:
            # Try alternative description
            success = automator.browser.type_text("login username field", username)
        
        if success:
            # #region agent log
            with open('/Users/russellpowers/Grants/.cursor/debug.log', 'a') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"post-fix","hypothesisId":"H5","location":"sdk_cli.py:cmd_auth_login:username_typed","message":"Username typed successfully","data":{},"timestamp":int(__import__('time').time()*1000)}) + '\n')
            # #endregion
            print("✅ Username filled")
        else:
            # #region agent log
            with open('/Users/russellpowers/Grants/.cursor/debug.log', 'a') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"post-fix","hypothesisId":"H5","location":"sdk_cli.py:cmd_auth_login:username_failed","message":"Username typing failed","data":{},"timestamp":int(__import__('time').time()*1000)}) + '\n')
            # #endregion
            self._error("Could not fill username field", 4)
        
        import time
        time.sleep(0.5)
        
        print("Filling password...")
        # For Playwright, type_text can work directly without needing find_element first
        success = automator.browser.type_text("password input field", password)
        if success:
            print("✅ Password filled")
        else:
            self._error("Could not fill password field", 4)
        
        time.sleep(0.5)
        
        # Step 6: Submit Login
        self._print_step_header(6, "Submit Login")
        print("Ready to click login button and submit form.")
        
        if not non_interactive:
            if not self._prompt_yes_no("Continue?", default=True):
                self._error("Login submission required", 3)
        
        print("Clicking login button...")
        # For Playwright, click can work directly without needing find_element first
        success = automator.browser.click("login button or sign in button")
        if success:
            print("Waiting for page load...")
            # Wait longer for form submission and page navigation
            automator.browser.wait_for(time_seconds=5)
            
            # Check if login was successful - wait a bit more and check again
            import time
            time.sleep(2)  # Additional wait for navigation
            current_url = automator.browser.get_current_url()
            
            # If still on login page, try submitting form directly
            if "login" in current_url.lower():
                print("Still on login page, trying form submission directly...")
                try:
                    # Try to submit the form directly using Playwright
                    from agents.grant_scraper.mcp_server_config import MCPServerConfig
                    config = MCPServerConfig()
                    tools = config.connect_to_server('playwright')
                    if tools:
                        playwright_fill = tools.get('playwright_fill')
                        if playwright_fill:
                            # Get the page from Playwright context
                            # This is a workaround - we'll use the browser's form submission
                            pass
                    
                    # Try pressing Enter on password field as alternative
                    automator.browser.type_text("password input field", password, submit=True)
                    automator.browser.wait_for(time_seconds=5)
                    time.sleep(2)
                    current_url = automator.browser.get_current_url()
                except Exception as e:
                    logger.warning(f"Form submission fallback failed: {e}")
            
            # Final check - wait a bit more and check for error messages
            if "login" in current_url.lower():
                # Wait a bit more in case page is still loading
                time.sleep(2)
                current_url = automator.browser.get_current_url()
                
                if "login" in current_url.lower():
                    # Take screenshot for debugging
                    automator.browser.take_screenshot("login_failed")
                    
                    # Try to check for error messages on the page
                    try:
                        snapshot = automator.browser.take_snapshot()
                        if snapshot and isinstance(snapshot, dict):
                            content = snapshot.get('content', '')
                            if 'error' in content.lower() or 'invalid' in content.lower() or 'incorrect' in content.lower():
                                self._error("Login failed - error message detected on page. Check credentials.", 3)
                    except:
                        pass
                    
                    self._error("Login may have failed - still on login page. Check credentials or try manually.", 3)
            
            print("✅ Login successful!")
            print(f"Current URL: {current_url}")
        else:
            self._error("Could not click login button", 4)
        
        # Step 7: Verification
        verification_results = {}
        if not skip_verification:
            self._print_step_header(7, "Verification")
            
            if non_interactive:
                # In non-interactive mode, do all verifications
                verify_choice_num = 5  # "All of the above"
            else:
                verify_choices = [
                    "Take a snapshot of current page",
                    "Navigate to grants list",
                    "Check available grants",
                    "Skip verification",
                    "All of the above"
                ]
                verify_choice_text = self._prompt_choice(
                    "Would you like to verify login by:",
                    verify_choices,
                    default=verify_choices[4]  # Default to "All of the above"
                )
                verify_choice_num = verify_choices.index(verify_choice_text) + 1
            
            if verify_choice_num == 4:  # Skip verification
                print("Skipping verification")
            else:
                if verify_choice_num in [1, 5]:  # Snapshot or All
                    print("Taking snapshot...")
                    try:
                        snapshot_result = automator.take_verification_snapshot()
                        verification_results['snapshot'] = snapshot_result
                        print(f"✅ Snapshot saved: {snapshot_result.get('screenshot_path', 'N/A')}")
                    except Exception as e:
                        logger.warning(f"Could not take snapshot: {e}")
                
                if verify_choice_num in [2, 3, 5]:  # Navigate/Check grants or All
                    print("Navigating to grants list...")
                    try:
                        if automator._navigate_to_draft_applications():
                            print("✅ Successfully navigated to draft applications")
                            
                            if verify_choice_num in [3, 5]:  # Check grants or All
                                print("Checking available grants...")
                                grants = automator.get_grants_list_after_login()
                                if grants:
                                    print(f"✅ Found {len(grants)} available grants:")
                                    for i, grant in enumerate(grants[:5], 1):  # Show first 5
                                        grant_name = grant.get('name', 'Unknown')
                                        if len(grant_name) > 50:
                                            grant_name = grant_name[:47] + "..."
                                        print(f"  {i}. {grant_name}")
                                    if len(grants) > 5:
                                        print(f"  ... and {len(grants) - 5} more")
                                    verification_results['grants'] = grants
                                else:
                                    print("⚠️  No grants found (may need to check page structure)")
                    except Exception as e:
                        logger.warning(f"Could not navigate to grants list: {e}")
        
        # Step 8: Next Steps
        self._print_step_header(8, "Next Steps")
        print("✅ Login completed successfully!")
        
        if self.output_format == 'human':
            print("\nAvailable commands:")
            print("  1. List grants: python3 -m agents.grant_scraper.sdk_cli browser snapshot")
            print("  2. Start application: python3 -m agents.grant_scraper.sdk_cli workflow full --grant-name \"...\"")
            print("  3. View dashboard: python3 -m agents.grant_scraper.sdk_cli report dashboard")
        
        if not non_interactive:
            next_choices = [
                "Keep browser open",
                "Close browser",
                "Run another command"
            ]
            next_choice = self._prompt_choice(
                "Would you like to:",
                next_choices,
                default=next_choices[0]
            )
            
            if next_choice == next_choices[1]:
                try:
                    automator.close()
                    print("✅ Browser closed")
                except Exception as e:
                    logger.warning(f"Error closing browser: {e}")
        
        # Output final results
        current_url = automator.get_current_page_url()
        result = {
            'status': 'success',
            'message': 'Logged in and verified successfully',
            'username': username,
            'current_url': current_url,
            'verification': verification_results if verification_results else None
        }
        
        self._output(result, "Login")
    
    def cmd_auth_logout(self, args):
        """Logout/close browser."""
        mcp_tools = self._get_mcp_browser_tools()
        if not mcp_tools:
            self._error("MCP browser tools not available", 3)
        
        # Browser close is handled automatically, just confirm
        self._output({'status': 'success', 'message': 'Browser closed'}, "Logout")
    
    # ==================== DATA COMMANDS ====================
    
    def cmd_data_extract(self, args):
        """Extract data from documents."""
        docs_folder = args.docs_folder or "docs"
        grant_name = args.grant_name
        
        extractor = DataExtractor(docs_folder)
        
        document_paths = None
        if args.doc:
            document_paths = [args.doc]
        
        grant_data = extractor.extract_grant_data(grant_name, document_paths)
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(grant_data, f, indent=2, default=str)
        
        self._output({
            'grant_name': grant_name,
            'data': grant_data,
            'output_file': args.output
        }, "Data Extraction")
    
    def cmd_data_validate(self, args):
        """Validate extracted data."""
        docs_folder = args.docs_folder or "docs"
        grant_name = args.grant_name
        
        extractor = DataExtractor(docs_folder)
        grant_data = extractor.extract_grant_data(grant_name, args.doc and [args.doc] or None)
        validation = extractor.validate_extracted_data(grant_data)
        
        self._output({
            'valid': validation['valid'],
            'missing_required': validation.get('missing_required', []),
            'missing_optional': validation.get('missing_optional', []),
            'warnings': validation.get('warnings', [])
        }, "Data Validation")
        
        if not validation['valid']:
            sys.exit(2)
    
    def cmd_data_standardize(self, args):
        """Standardize data format."""
        docs_folder = args.docs_folder or "docs"
        grant_name = args.grant_name
        
        extractor = DataExtractor(docs_folder)
        grant_data = extractor.extract_grant_data(grant_name, args.doc and [args.doc] or None)
        standardized = extractor.get_standardized_data(grant_data)
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(standardized, f, indent=2, default=str)
        
        self._output({
            'grant_name': grant_name,
            'standardized_data': standardized,
            'output_file': args.output
        }, "Data Standardization")
    
    def cmd_data_identify_docs(self, args):
        """Identify relevant documents."""
        docs_folder = args.docs_folder or "docs"
        grant_name = args.grant_name
        organization_name = args.organization_name
        
        extractor = DataExtractor(docs_folder)
        documents = extractor.identify_relevant_documents(grant_name, organization_name)
        
        self._output({
            'grant_name': grant_name,
            'documents': documents,
            'count': len(documents)
        }, "Document Identification")
    
    # ==================== MAPPING COMMANDS ====================
    
    def cmd_mapping_map(self, args):
        """Map data to form fields."""
        # Load data
        if args.data_file:
            with open(args.data_file, 'r') as f:
                data = json.load(f)
        else:
            # Extract fresh
            docs_folder = args.docs_folder or "docs"
            grant_name = args.grant_name
            extractor = DataExtractor(docs_folder)
            grant_data = extractor.extract_grant_data(grant_name, args.doc and [args.doc] or None)
            data = extractor.get_standardized_data(grant_data)
        
        # Initialize mapper
        mapper = FormMapper(
            config_path=args.config,
            use_narratives=args.use_narratives,
            narrative_generator=None  # Will be initialized if needed
        )
        
        # Generate narratives if enabled
        if args.use_narratives:
            api_key = args.openai_api_key or os.getenv('OPENAI_API_KEY')
            if not api_key:
                self._error("OpenAI API key required for narrative generation", 5)
            
            if NarrativeGenerator:
                mapper.narrative_generator = NarrativeGenerator(
                    api_key=api_key,
                    model=args.narrative_model or "gpt-4"
                )
                mapper.use_narratives = True
        
        mapped_fields = mapper.map_data_to_fields(data, grant_name=args.grant_name)
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(mapped_fields, f, indent=2, default=str)
        
        self._output({
            'fields_mapped': len(mapped_fields),
            'mapped_fields': mapped_fields,
            'output_file': args.output
        }, "Field Mapping")
    
    def cmd_mapping_validate_map(self, args):
        """Validate field mappings."""
        if not args.mapped_file:
            self._error("--mapped-file required", 5)
        
        with open(args.mapped_file, 'r') as f:
            mapped_fields = json.load(f)
        
        mapper = FormMapper(config_path=args.config)
        validation = mapper.validate_mapped_fields(mapped_fields)
        
        self._output({
            'valid': validation['valid'],
            'invalid_fields': validation.get('invalid_fields', []),
            'missing_required': validation.get('missing_required', [])
        }, "Mapping Validation")
        
        if not validation['valid']:
            sys.exit(2)
    
    def cmd_mapping_create_instructions(self, args):
        """Create field filling instructions."""
        if not args.mapped_file:
            self._error("--mapped-file required", 5)
        
        with open(args.mapped_file, 'r') as f:
            mapped_fields = json.load(f)
        
        mapper = FormMapper(config_path=args.config)
        instructions = mapper.create_field_filling_instructions(mapped_fields)
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(instructions, f, indent=2, default=str)
        
        self._output({
            'instructions_count': len(instructions),
            'instructions': instructions,
            'output_file': args.output
        }, "Field Filling Instructions")
    
    # ==================== NARRATIVE COMMANDS ====================
    
    def cmd_narrative_generate(self, args):
        """Generate narrative for a specific field."""
        api_key = args.openai_api_key or os.getenv('OPENAI_API_KEY')
        if not api_key:
            self._error("OpenAI API key required", 5)
        
        if not NarrativeGenerator:
            self._error("NarrativeGenerator not available", 5)
        
        # Load grant data
        if args.data_file:
            with open(args.data_file, 'r') as f:
                grant_data = json.load(f)
        else:
            docs_folder = args.docs_folder or "docs"
            extractor = DataExtractor(docs_folder)
            grant_data = extractor.extract_grant_data(args.grant_name, args.doc and [args.doc] or None)
        
        generator = NarrativeGenerator(
            api_key=api_key,
            model=args.model or "gpt-4"
        )
        
        narrative = generator.generate_narrative(
            args.narrative_type,
            args.grant_name,
            grant_data
        )
        
        if narrative:
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(narrative)
            
            self._output({
                'narrative_type': args.narrative_type,
                'narrative': narrative,
                'output_file': args.output
            }, "Narrative Generation")
        else:
            self._error("Failed to generate narrative", 1)
    
    def cmd_narrative_generate_all(self, args):
        """Generate all narratives."""
        api_key = args.openai_api_key or os.getenv('OPENAI_API_KEY')
        if not api_key:
            self._error("OpenAI API key required", 5)
        
        if not NarrativeGenerator:
            self._error("NarrativeGenerator not available", 5)
        
        # Load grant data
        if args.data_file:
            with open(args.data_file, 'r') as f:
                grant_data = json.load(f)
        else:
            docs_folder = args.docs_folder or "docs"
            extractor = DataExtractor(docs_folder)
            grant_data = extractor.extract_grant_data(args.grant_name, args.doc and [args.doc] or None)
        
        generator = NarrativeGenerator(
            api_key=api_key,
            model=args.model or "gpt-4"
        )
        
        narratives = {}
        narrative_types = ['project_description', 'goals', 'impact', 'activities', 'budget', 'technical']
        
        for nar_type in narrative_types:
            narrative = generator.generate_narrative(nar_type, args.grant_name, grant_data)
            if narrative:
                narratives[nar_type] = narrative
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(narratives, f, indent=2, default=str)
        
        self._output({
            'narratives_generated': len(narratives),
            'narratives': narratives,
            'output_file': args.output
        }, "Narrative Generation (All)")
    
    # ==================== BROWSER COMMANDS ====================
    
    def cmd_browser_navigate(self, args):
        """Navigate to URL."""
        mcp_tools = self._get_mcp_browser_tools()
        if not mcp_tools:
            self._error("MCP browser tools not available", 3)
        
        browser = MCPBrowserIntegration()
        browser.initialize_browser(mcp_tools)
        success = browser.navigate(args.url)
        
        if success:
            current_url = browser.get_current_url()
            self._output({
                'status': 'success',
                'url': args.url,
                'current_url': current_url
            }, "Navigation")
        else:
            self._error("Navigation failed", 4)
    
    def cmd_browser_snapshot(self, args):
        """Take page snapshot."""
        mcp_tools = self._get_mcp_browser_tools()
        if not mcp_tools:
            self._error("MCP browser tools not available", 3)
        
        browser = MCPBrowserIntegration()
        browser.initialize_browser(mcp_tools)
        snapshot = browser.take_snapshot()
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(snapshot, f, indent=2, default=str)
        
        self._output({
            'snapshot': snapshot,
            'output_file': args.output
        }, "Page Snapshot")
    
    def cmd_browser_find(self, args):
        """Find element on page."""
        mcp_tools = self._get_mcp_browser_tools()
        if not mcp_tools:
            self._error("MCP browser tools not available", 3)
        
        browser = MCPBrowserIntegration()
        browser.initialize_browser(mcp_tools)
        element = browser.find_element(args.description, return_action=args.return_action)
        
        self._output({
            'description': args.description,
            'element': element
        }, "Element Find")
    
    def cmd_browser_click(self, args):
        """Click element."""
        mcp_tools = self._get_mcp_browser_tools()
        if not mcp_tools:
            self._error("MCP browser tools not available", 3)
        
        browser = MCPBrowserIntegration()
        browser.initialize_browser(mcp_tools)
        success = browser.click(args.description, element_ref=args.element_ref)
        
        self._output({
            'status': 'success' if success else 'failed',
            'description': args.description
        }, "Click Element")
        
        if not success:
            sys.exit(1)
    
    def cmd_browser_type(self, args):
        """Type text into field."""
        mcp_tools = self._get_mcp_browser_tools()
        if not mcp_tools:
            self._error("MCP browser tools not available", 3)
        
        browser = MCPBrowserIntegration()
        browser.initialize_browser(mcp_tools)
        success = browser.type_text(
            args.description,
            args.text,
            element_ref=args.element_ref,
            slowly=args.slowly
        )
        
        self._output({
            'status': 'success' if success else 'failed',
            'description': args.description,
            'text_length': len(args.text)
        }, "Type Text")
        
        if not success:
            sys.exit(1)
    
    def cmd_browser_select(self, args):
        """Select dropdown option."""
        mcp_tools = self._get_mcp_browser_tools()
        if not mcp_tools:
            self._error("MCP browser tools not available", 3)
        
        browser = MCPBrowserIntegration()
        browser.initialize_browser(mcp_tools)
        values = args.values.split(',') if isinstance(args.values, str) else args.values
        success = browser.select_option(args.description, values, element_ref=args.element_ref)
        
        self._output({
            'status': 'success' if success else 'failed',
            'description': args.description,
            'values': values
        }, "Select Option")
        
        if not success:
            sys.exit(1)
    
    def cmd_browser_screenshot(self, args):
        """Take screenshot."""
        mcp_tools = self._get_mcp_browser_tools()
        if not mcp_tools:
            self._error("MCP browser tools not available", 3)
        
        browser = MCPBrowserIntegration()
        browser.initialize_browser(mcp_tools)
        screenshot_path = browser.take_screenshot(args.name or "screenshot")
        
        self._output({
            'status': 'success',
            'screenshot_path': screenshot_path
        }, "Screenshot")
    
    def cmd_browser_wait(self, args):
        """Wait for condition."""
        mcp_tools = self._get_mcp_browser_tools()
        if not mcp_tools:
            self._error("MCP browser tools not available", 3)
        
        browser = MCPBrowserIntegration()
        browser.initialize_browser(mcp_tools)
        success = browser.wait_for(
            text=args.text,
            text_gone=args.text_gone,
            time_seconds=args.time
        )
        
        self._output({
            'status': 'success' if success else 'failed'
        }, "Wait")
        
        if not success:
            sys.exit(1)
    
    # ==================== FORM COMMANDS ====================
    
    def cmd_form_start(self, args):
        """Start new application."""
        username = args.username or os.getenv('4CULTURE_USERNAME', 'Keyisaccess')
        password = args.password or os.getenv('4CULTURE_PASSWORD', 'Outlaw22!!')
        
        mcp_tools = self._get_mcp_browser_tools()
        if not mcp_tools:
            self._error("MCP browser tools not available", 3)
        
        automator = ApplicationAutomator(username, password, mcp_tools=mcp_tools)
        success = automator.start_new_application(args.grant_name)
        
        self._output({
            'status': 'success' if success else 'failed',
            'grant_name': args.grant_name
        }, "Start Application")
        
        if not success:
            sys.exit(1)
    
    def cmd_form_extract_structure(self, args):
        """Extract form structure."""
        username = args.username or os.getenv('4CULTURE_USERNAME', 'Keyisaccess')
        password = args.password or os.getenv('4CULTURE_PASSWORD', 'Outlaw22!!')
        
        mcp_tools = self._get_mcp_browser_tools()
        if not mcp_tools:
            self._error("MCP browser tools not available", 3)
        
        automator = ApplicationAutomator(username, password, mcp_tools=mcp_tools)
        form_structure = automator.extract_form_structure()
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(form_structure, f, indent=2, default=str)
        
        self._output({
            'form_structure': form_structure,
            'output_file': args.output
        }, "Form Structure")
    
    def cmd_form_fill(self, args):
        """Fill form field(s)."""
        username = args.username or os.getenv('4CULTURE_USERNAME', 'Keyisaccess')
        password = args.password or os.getenv('4CULTURE_PASSWORD', 'Outlaw22!!')
        
        mcp_tools = self._get_mcp_browser_tools()
        if not mcp_tools:
            self._error("MCP browser tools not available", 3)
        
        # Load instructions
        if args.instructions_file:
            with open(args.instructions_file, 'r') as f:
                instructions = json.load(f)
        else:
            # Single field fill
            instructions = [{
                'field_name': args.field_name,
                'value': args.value,
                'field_type': args.field_type or 'text',
                'action': 'type'
            }]
        
        automator = ApplicationAutomator(username, password, mcp_tools=mcp_tools)
        result = automator.fill_form_fields(instructions)
        
        self._output({
            'success': result.get('success', False),
            'filled_fields': result.get('filled_fields', []),
            'failed_fields': result.get('failed_fields', [])
        }, "Fill Form")
        
        if not result.get('success'):
            sys.exit(1)
    
    def cmd_form_fill_all(self, args):
        """Fill all form fields."""
        self.cmd_form_fill(args)  # Same implementation
    
    def cmd_form_validate(self, args):
        """Check for validation errors."""
        username = args.username or os.getenv('4CULTURE_USERNAME', 'Keyisaccess')
        password = args.password or os.getenv('4CULTURE_PASSWORD', 'Outlaw22!!')
        
        mcp_tools = self._get_mcp_browser_tools()
        if not mcp_tools:
            self._error("MCP browser tools not available", 3)
        
        automator = ApplicationAutomator(username, password, mcp_tools=mcp_tools)
        errors = automator.handle_form_validation_errors()
        
        self._output({
            'has_errors': len(errors) > 0,
            'errors': errors,
            'error_count': len(errors)
        }, "Form Validation")
        
        if errors:
            sys.exit(2)
    
    def cmd_form_save(self, args):
        """Save draft."""
        username = args.username or os.getenv('4CULTURE_USERNAME', 'Keyisaccess')
        password = args.password or os.getenv('4CULTURE_PASSWORD', 'Outlaw22!!')
        
        mcp_tools = self._get_mcp_browser_tools()
        if not mcp_tools:
            self._error("MCP browser tools not available", 3)
        
        automator = ApplicationAutomator(username, password, mcp_tools=mcp_tools)
        result = automator.save_draft()
        
        self._output({
            'success': result.get('success', False),
            'draft_url': result.get('draft_url'),
            'message': result.get('message')
        }, "Save Draft")
        
        if not result.get('success'):
            sys.exit(1)
    
    # ==================== WORKFLOW COMMANDS ====================
    
    def cmd_workflow_full(self, args):
        """Run complete workflow."""
        docs_folder = args.docs_folder or "docs"
        config_path = args.config or "agents/grant_scraper/grant_config.yaml"
        
        mcp_tools = self._get_mcp_browser_tools()
        
        workflow = AutomationWorkflow(
            username=args.username or os.getenv('4CULTURE_USERNAME', 'Keyisaccess'),
            password=args.password or os.getenv('4CULTURE_PASSWORD', 'Outlaw22!!'),
            docs_folder=docs_folder,
            config_path=config_path,
            use_narratives=args.use_narratives,
            openai_api_key=args.openai_api_key or os.getenv('OPENAI_API_KEY'),
            narrative_model=args.narrative_model,
            mcp_tools=mcp_tools,
            db_path=args.db_path or "agents/grant_scraper/grants.db"
        )
        
        document_paths = None
        if args.doc:
            document_paths = [args.doc]
        
        result = workflow.run_automation(
            grant_name=args.grant_name,
            document_paths=document_paths,
            dry_run=args.dry_run
        )
        
        # Generate report
        if not args.dry_run:
            report_path = args.report or f"grant_application_report_{args.grant_name.replace(' ', '_')}.md"
            workflow.generate_report(result, report_path)
        
        self._output({
            'success': result.get('success', False),
            'steps_completed': result.get('steps_completed', []),
            'steps_failed': result.get('steps_failed', []),
            'draft_saved': result.get('draft_saved', False),
            'draft_url': result.get('draft_url'),
            'report_path': report_path if not args.dry_run else None
        }, "Full Workflow")
        
        if not result.get('success'):
            sys.exit(1)
    
    def cmd_workflow_custom(self, args):
        """Run custom workflow from steps."""
        steps = args.steps.split(',') if isinstance(args.steps, str) else args.steps
        
        # Initialize workflow state
        self.workflow_state = WorkflowState()
        self.workflow_state.set_grant_name(args.grant_name)
        
        # Execute steps
        for step in steps:
            step = step.strip()
            if step == 'login':
                # Login step
                pass  # Implement step execution
            elif step == 'extract':
                # Extract step
                pass
            # Add more step handlers
        
        self._output({
            'workflow_id': self.workflow_state.workflow_id,
            'steps_executed': steps,
            'progress': self.workflow_state.get_progress()
        }, "Custom Workflow")
    
    # ==================== DATABASE COMMANDS ====================
    
    def cmd_database_add(self, args):
        """Add grant to database."""
        db = GrantDatabase(args.db_path or "agents/grant_scraper/grants.db")
        
        grant_data = {
            'name': args.name,
            'identifier': args.identifier or args.name.lower().replace(' ', '-'),
            'deadline': args.deadline,
            'status': args.status or 'planned',
            'amount_requested': args.amount,
            'organization_name': args.organization,
            'project_title': args.project_title,
            'description': args.description,
            'priority': args.priority or 5
        }
        
        grant_id = db.add_grant(grant_data)
        db.close()
        
        self._output({
            'grant_id': grant_id,
            'grant_name': args.name
        }, "Add Grant")
    
    def cmd_database_update(self, args):
        """Update grant status."""
        db = GrantDatabase(args.db_path or "agents/grant_scraper/grants.db")
        
        update_kwargs = {}
        if args.status:
            update_kwargs['status'] = args.status
        if args.progress:
            update_kwargs['progress_percentage'] = args.progress
        if args.current_step:
            update_kwargs['current_step'] = args.current_step
        
        db.update_grant_status(args.grant_id, args.status or 'planned', **update_kwargs)
        db.close()
        
        self._output({
            'grant_id': args.grant_id,
            'status': args.status
        }, "Update Grant")
    
    def cmd_database_get(self, args):
        """Get grant details."""
        db = GrantDatabase(args.db_path or "agents/grant_scraper/grants.db")
        grant = db.get_grant_details(args.grant_id)
        db.close()
        
        if grant:
            self._output({'grant': grant}, "Grant Details")
        else:
            self._error(f"Grant {args.grant_id} not found", 1)
    
    def cmd_database_list(self, args):
        """List grants by status."""
        db = GrantDatabase(args.db_path or "agents/grant_scraper/grants.db")
        grants = db.get_grants_by_status(args.status)
        db.close()
        
        self._output({
            'status': args.status or 'all',
            'count': len(grants),
            'grants': grants
        }, "List Grants")
    
    def cmd_database_timeline(self, args):
        """Get grants by month."""
        db = GrantDatabase(args.db_path or "agents/grant_scraper/grants.db")
        timeline = db.get_grants_by_month()
        db.close()
        
        self._output({'timeline': timeline}, "Grant Timeline")
    
    # ==================== REPORT COMMANDS ====================
    
    def cmd_report_generate(self, args):
        """Generate completion report."""
        if not args.result_file:
            self._error("--result-file required", 5)
        
        with open(args.result_file, 'r') as f:
            result = json.load(f)
        
        workflow = AutomationWorkflow(
            username="dummy",
            password="dummy",
            docs_folder="docs"
        )
        
        report_path = args.output or "grant_report.md"
        workflow.generate_report(result, report_path)
        
        self._output({
            'report_path': report_path
        }, "Report Generation")
    
    def cmd_report_dashboard(self, args):
        """Generate HTML dashboard."""
        dashboard = GrantDashboard()
        output_path = dashboard.generate_dashboard()
        
        self._output({
            'dashboard_path': output_path
        }, "Dashboard Generation")


def create_parser():
    """Create argument parser with all commands."""
    parser = argparse.ArgumentParser(
        description='4Culture Grant Application Automation SDK',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--json', action='store_true', help='Output in JSON format')
    parser.add_argument('--yaml', action='store_true', help='Output in YAML format')
    
    subparsers = parser.add_subparsers(dest='command_group', help='Command group')
    
    # AUTH commands
    auth_parser = subparsers.add_parser('auth', help='Authentication commands')
    auth_sub = auth_parser.add_subparsers(dest='command')
    
    login_parser = auth_sub.add_parser('login', help='Login to 4Culture (interactive)')
    login_parser.add_argument('--username', help='4Culture username')
    login_parser.add_argument('--password', help='4Culture password')
    login_parser.add_argument('--non-interactive', action='store_true', 
                             help='Skip all prompts (use defaults)')
    login_parser.add_argument('--skip-mcp-setup', action='store_true',
                             help='Skip MCP setup (fail if tools not available)')
    login_parser.add_argument('--skip-verification', action='store_true',
                             help='Skip verification steps')
    
    auth_sub.add_parser('logout', help='Logout/close browser')
    
    # DATA commands
    data_parser = subparsers.add_parser('data', help='Data extraction commands')
    data_sub = data_parser.add_subparsers(dest='command')
    
    extract_parser = data_sub.add_parser('extract', help='Extract data from documents')
    extract_parser.add_argument('--grant-name', required=True)
    extract_parser.add_argument('--doc', help='Specific document path')
    extract_parser.add_argument('--docs-folder', default='docs')
    extract_parser.add_argument('--output', help='Output file')
    
    validate_parser = data_sub.add_parser('validate', help='Validate extracted data')
    validate_parser.add_argument('--grant-name', required=True)
    validate_parser.add_argument('--doc', help='Specific document path')
    validate_parser.add_argument('--docs-folder', default='docs')
    
    standardize_parser = data_sub.add_parser('standardize', help='Standardize data format')
    standardize_parser.add_argument('--grant-name', required=True)
    standardize_parser.add_argument('--doc', help='Specific document path')
    standardize_parser.add_argument('--docs-folder', default='docs')
    standardize_parser.add_argument('--output', help='Output file')
    
    identify_parser = data_sub.add_parser('identify-docs', help='Identify relevant documents')
    identify_parser.add_argument('--grant-name', required=True)
    identify_parser.add_argument('--organization-name', help='Organization name')
    identify_parser.add_argument('--docs-folder', default='docs')
    
    # MAPPING commands
    mapping_parser = subparsers.add_parser('mapping', help='Field mapping commands')
    mapping_sub = mapping_parser.add_subparsers(dest='command')
    
    map_parser = mapping_sub.add_parser('map', help='Map data to form fields')
    map_parser.add_argument('--grant-name', required=True)
    map_parser.add_argument('--data-file', help='Standardized data file')
    map_parser.add_argument('--doc', help='Document path')
    map_parser.add_argument('--docs-folder', default='docs')
    map_parser.add_argument('--config', help='Configuration file')
    map_parser.add_argument('--use-narratives', action='store_true')
    map_parser.add_argument('--openai-api-key', help='OpenAI API key')
    map_parser.add_argument('--narrative-model', default='gpt-4')
    map_parser.add_argument('--output', help='Output file')
    
    validate_map_parser = mapping_sub.add_parser('validate-map', help='Validate field mappings')
    validate_map_parser.add_argument('--mapped-file', required=True)
    validate_map_parser.add_argument('--config', help='Configuration file')
    
    instructions_parser = mapping_sub.add_parser('create-instructions', help='Create field filling instructions')
    instructions_parser.add_argument('--mapped-file', required=True)
    instructions_parser.add_argument('--config', help='Configuration file')
    instructions_parser.add_argument('--output', help='Output file')
    
    # NARRATIVE commands
    narrative_parser = subparsers.add_parser('narrative', help='Narrative generation commands')
    narrative_sub = narrative_parser.add_subparsers(dest='command')
    
    gen_parser = narrative_sub.add_parser('generate', help='Generate narrative for field')
    gen_parser.add_argument('--grant-name', required=True)
    gen_parser.add_argument('--narrative-type', required=True)
    gen_parser.add_argument('--data-file', help='Grant data file')
    gen_parser.add_argument('--doc', help='Document path')
    gen_parser.add_argument('--docs-folder', default='docs')
    gen_parser.add_argument('--openai-api-key', help='OpenAI API key')
    gen_parser.add_argument('--model', default='gpt-4')
    gen_parser.add_argument('--output', help='Output file')
    
    gen_all_parser = narrative_sub.add_parser('generate-all', help='Generate all narratives')
    gen_all_parser.add_argument('--grant-name', required=True)
    gen_all_parser.add_argument('--data-file', help='Grant data file')
    gen_all_parser.add_argument('--doc', help='Document path')
    gen_all_parser.add_argument('--docs-folder', default='docs')
    gen_all_parser.add_argument('--openai-api-key', help='OpenAI API key')
    gen_all_parser.add_argument('--model', default='gpt-4')
    gen_all_parser.add_argument('--output', help='Output file')
    
    # BROWSER commands
    browser_parser = subparsers.add_parser('browser', help='Browser automation commands')
    browser_sub = browser_parser.add_subparsers(dest='command')
    
    nav_parser = browser_sub.add_parser('navigate', help='Navigate to URL')
    nav_parser.add_argument('--url', required=True)
    
    browser_sub.add_parser('snapshot', help='Take page snapshot').add_argument('--output', help='Output file')
    
    find_parser = browser_sub.add_parser('find', help='Find element')
    find_parser.add_argument('--description', required=True)
    find_parser.add_argument('--return-action', action='store_true')
    
    click_parser = browser_sub.add_parser('click', help='Click element')
    click_parser.add_argument('--description', required=True)
    click_parser.add_argument('--element-ref', help='Element reference')
    
    type_parser = browser_sub.add_parser('type', help='Type text')
    type_parser.add_argument('--description', required=True)
    type_parser.add_argument('--text', required=True)
    type_parser.add_argument('--element-ref', help='Element reference')
    type_parser.add_argument('--slowly', action='store_true')
    
    select_parser = browser_sub.add_parser('select', help='Select option')
    select_parser.add_argument('--description', required=True)
    select_parser.add_argument('--values', required=True)
    select_parser.add_argument('--element-ref', help='Element reference')
    
    screenshot_parser = browser_sub.add_parser('screenshot', help='Take screenshot')
    screenshot_parser.add_argument('--name', help='Screenshot name')
    
    wait_parser = browser_sub.add_parser('wait', help='Wait for condition')
    wait_parser.add_argument('--text', help='Text to wait for')
    wait_parser.add_argument('--text-gone', help='Text to wait for to disappear')
    wait_parser.add_argument('--time', type=int, help='Time in seconds')
    
    # FORM commands
    form_parser = subparsers.add_parser('form', help='Form automation commands')
    form_sub = form_parser.add_subparsers(dest='command')
    
    start_parser = form_sub.add_parser('start', help='Start new application')
    start_parser.add_argument('--grant-name', required=True)
    start_parser.add_argument('--username', help='4Culture username')
    start_parser.add_argument('--password', help='4Culture password')
    
    extract_struct_parser = form_sub.add_parser('extract-structure', help='Extract form structure')
    extract_struct_parser.add_argument('--username', help='4Culture username')
    extract_struct_parser.add_argument('--password', help='4Culture password')
    extract_struct_parser.add_argument('--output', help='Output file')
    
    fill_parser = form_sub.add_parser('fill', help='Fill form field(s)')
    fill_parser.add_argument('--instructions-file', help='Field filling instructions file')
    fill_parser.add_argument('--field-name', help='Single field name')
    fill_parser.add_argument('--value', help='Field value')
    fill_parser.add_argument('--field-type', default='text')
    fill_parser.add_argument('--username', help='4Culture username')
    fill_parser.add_argument('--password', help='4Culture password')
    
    form_sub.add_parser('fill-all', help='Fill all fields').add_argument('--instructions-file', required=True)
    
    validate_form_parser = form_sub.add_parser('validate', help='Check for validation errors')
    validate_form_parser.add_argument('--username', help='4Culture username')
    validate_form_parser.add_argument('--password', help='4Culture password')
    
    save_parser = form_sub.add_parser('save', help='Save draft')
    save_parser.add_argument('--username', help='4Culture username')
    save_parser.add_argument('--password', help='4Culture password')
    
    # WORKFLOW commands
    workflow_parser = subparsers.add_parser('workflow', help='Workflow commands')
    workflow_sub = workflow_parser.add_subparsers(dest='command')
    
    full_parser = workflow_sub.add_parser('full', help='Run complete workflow')
    full_parser.add_argument('--grant-name', required=True)
    full_parser.add_argument('--doc', help='Document path')
    full_parser.add_argument('--docs-folder', default='docs')
    full_parser.add_argument('--config', help='Configuration file')
    full_parser.add_argument('--username', help='4Culture username')
    full_parser.add_argument('--password', help='4Culture password')
    full_parser.add_argument('--dry-run', action='store_true')
    full_parser.add_argument('--use-narratives', action='store_true')
    full_parser.add_argument('--openai-api-key', help='OpenAI API key')
    full_parser.add_argument('--narrative-model', default='gpt-4')
    full_parser.add_argument('--report', help='Report output path')
    full_parser.add_argument('--db-path', help='Database path')
    
    custom_parser = workflow_sub.add_parser('custom', help='Custom workflow')
    custom_parser.add_argument('--grant-name', required=True)
    custom_parser.add_argument('--steps', required=True, help='Comma-separated list of steps')
    
    # DATABASE commands
    db_parser = subparsers.add_parser('database', help='Database commands')
    db_sub = db_parser.add_subparsers(dest='command')
    
    db_add_parser = db_sub.add_parser('add', help='Add grant')
    db_add_parser.add_argument('--name', required=True)
    db_add_parser.add_argument('--identifier', help='Grant identifier')
    db_add_parser.add_argument('--deadline', help='Deadline')
    db_add_parser.add_argument('--status', default='planned')
    db_add_parser.add_argument('--amount', type=float, help='Amount requested')
    db_add_parser.add_argument('--organization', help='Organization name')
    db_add_parser.add_argument('--project-title', help='Project title')
    db_add_parser.add_argument('--description', help='Description')
    db_add_parser.add_argument('--priority', type=int, help='Priority (1-10)')
    db_add_parser.add_argument('--db-path', help='Database path')
    
    db_update_parser = db_sub.add_parser('update', help='Update grant')
    db_update_parser.add_argument('--grant-id', type=int, required=True)
    db_update_parser.add_argument('--status', help='Status')
    db_update_parser.add_argument('--progress', type=int, help='Progress percentage')
    db_update_parser.add_argument('--current-step', help='Current step')
    db_update_parser.add_argument('--db-path', help='Database path')
    
    db_get_parser = db_sub.add_parser('get', help='Get grant details')
    db_get_parser.add_argument('--grant-id', type=int, required=True)
    db_get_parser.add_argument('--db-path', help='Database path')
    
    db_list_parser = db_sub.add_parser('list', help='List grants')
    db_list_parser.add_argument('--status', help='Filter by status')
    db_list_parser.add_argument('--db-path', help='Database path')
    
    db_sub.add_parser('timeline', help='Get grants by month').add_argument('--db-path', help='Database path')
    
    # REPORT commands
    report_parser = subparsers.add_parser('report', help='Report commands')
    report_sub = report_parser.add_subparsers(dest='command')
    
    report_gen_parser = report_sub.add_parser('generate', help='Generate report')
    report_gen_parser.add_argument('--result-file', required=True)
    report_gen_parser.add_argument('--output', help='Output path')
    
    report_sub.add_parser('dashboard', help='Generate dashboard')
    
    return parser


def main():
    """Main entry point for SDK CLI."""
    parser = create_parser()
    
    # First, check for format flags anywhere in arguments
    output_format = 'human'
    if '--json' in sys.argv:
        output_format = 'json'
        sys.argv.remove('--json')
    elif '--yaml' in sys.argv:
        output_format = 'yaml'
        sys.argv.remove('--yaml')
    
    args = parser.parse_args()
    
    if not args.command_group:
        parser.print_help()
        sys.exit(1)
    
    cli = GrantSDKCLI()
    cli.output_format = output_format
    
    # Route to appropriate command handler
    command_map = {
        ('auth', 'login'): cli.cmd_auth_login,
        ('auth', 'logout'): cli.cmd_auth_logout,
        ('data', 'extract'): cli.cmd_data_extract,
        ('data', 'validate'): cli.cmd_data_validate,
        ('data', 'standardize'): cli.cmd_data_standardize,
        ('data', 'identify-docs'): cli.cmd_data_identify_docs,
        ('mapping', 'map'): cli.cmd_mapping_map,
        ('mapping', 'validate-map'): cli.cmd_mapping_validate_map,
        ('mapping', 'create-instructions'): cli.cmd_mapping_create_instructions,
        ('narrative', 'generate'): cli.cmd_narrative_generate,
        ('narrative', 'generate-all'): cli.cmd_narrative_generate_all,
        ('browser', 'navigate'): cli.cmd_browser_navigate,
        ('browser', 'snapshot'): cli.cmd_browser_snapshot,
        ('browser', 'find'): cli.cmd_browser_find,
        ('browser', 'click'): cli.cmd_browser_click,
        ('browser', 'type'): cli.cmd_browser_type,
        ('browser', 'select'): cli.cmd_browser_select,
        ('browser', 'screenshot'): cli.cmd_browser_screenshot,
        ('browser', 'wait'): cli.cmd_browser_wait,
        ('form', 'start'): cli.cmd_form_start,
        ('form', 'extract-structure'): cli.cmd_form_extract_structure,
        ('form', 'fill'): cli.cmd_form_fill,
        ('form', 'fill-all'): cli.cmd_form_fill_all,
        ('form', 'validate'): cli.cmd_form_validate,
        ('form', 'save'): cli.cmd_form_save,
        ('workflow', 'full'): cli.cmd_workflow_full,
        ('workflow', 'custom'): cli.cmd_workflow_custom,
        ('database', 'add'): cli.cmd_database_add,
        ('database', 'update'): cli.cmd_database_update,
        ('database', 'get'): cli.cmd_database_get,
        ('database', 'list'): cli.cmd_database_list,
        ('database', 'timeline'): cli.cmd_database_timeline,
        ('report', 'generate'): cli.cmd_report_generate,
        ('report', 'dashboard'): cli.cmd_report_dashboard,
    }
    
    handler = command_map.get((args.command_group, args.command))
    if handler:
        try:
            handler(args)
        except Exception as e:
            logger.error(f"Error executing command: {e}", exc_info=True)
            cli._error(str(e), 1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()

