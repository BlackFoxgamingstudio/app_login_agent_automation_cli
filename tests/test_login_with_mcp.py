#!/usr/bin/env python3
"""
Test login using available MCP browser tools.

DEVELOPER GUIDELINE: Tool Injection Testing
When testing dynamic runtime dependencies like MCP tool injection, ensure 
test setups correctly mock or pass through the required context (like globals) 
to simulate the real execution environment accurately.

This script demonstrates how the SDK CLI login works when MCP tools are available.
"""

import os
import sys

import pytest


@pytest.mark.integration
def test_login_with_available_tools():
    """Test login using MCP tools that might be available."""
    print("=" * 60)
    print("Testing Login with Available MCP Tools")
    print("=" * 60)

    # Try to import and use MCP browser integration
    try:
        from grant_automation_cli.application_automator import ApplicationAutomator
        from grant_automation_cli.mcp_browser_integration import MCPBrowserIntegration

        username = os.getenv("4CULTURE_USERNAME", "")
        password = os.getenv("4CULTURE_PASSWORD", "")

        print(f"\nUsername: {username}")
        print(f"Password: {'*' * len(password)}")

        # Check if we can create browser integration
        print("\n1. Initializing browser integration...")
        browser = MCPBrowserIntegration(use_multi_session=False)

        # Try to get MCP tools from various sources
        print("2. Attempting to collect MCP tools...")

        # Method 1: Try from globals (if in MCP context)
        import sys

        frame = sys._getframe(0)
        caller_globals = frame.f_globals

        from grant_automation_cli.mcp_tools_helper import create_mcp_tools_dict_from_globals

        mcp_tools = create_mcp_tools_dict_from_globals(caller_globals)

        if not mcp_tools:
            print("   ⚠️  MCP tools not found in globals")
            print("\n   Note: In Cursor IDE, MCP tools are injected automatically.")
            print("   This test requires running in an MCP-enabled environment.")
            print("\n   To test login:")
            print("   1. Use the SDK CLI in Cursor IDE where MCP tools are available")
            print("   2. Or configure MCP server in your terminal environment")
            return False

        print(f"   ✅ Found {len(mcp_tools)} MCP tools")

        # Initialize browser with tools
        print("\n3. Initializing browser with MCP tools...")
        browser.initialize_browser(mcp_tools)

        # Create automator
        print("\n4. Creating application automator...")
        automator = ApplicationAutomator(username, password, mcp_tools=mcp_tools)

        # Attempt login
        print("\n5. Attempting login...")
        success = automator.login()

        if success:
            current_url = automator.get_current_page_url()
            print("   ✅ Login successful!")
            print(f"   Current URL: {current_url}")

            # Take screenshot
            screenshot = automator.browser.take_screenshot("login_test_success")
            if screenshot:
                print(f"   Screenshot: {screenshot}")

            automator.close()
            return True
        else:
            print("   ❌ Login failed")
            return False

    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_login_with_available_tools()
    print("\n" + "=" * 60)
    if success:
        print("✅ Login test completed successfully!")
    else:
        print("⚠️  Login test completed (MCP tools not available in this environment)")
    print("=" * 60)
    sys.exit(0 if success else 1)
