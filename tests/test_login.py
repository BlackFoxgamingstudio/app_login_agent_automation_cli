#!/usr/bin/env python3
"""
Test script for browser login functionality.

DEVELOPER GUIDELINE: Integration Testing & Boundaries
Integration tests interacting with external services (like 4Culture) should be 
marked (e.g., `@pytest.mark.integration`) so they can be easily excluded from 
fast local test runs. Handle missing environment variables gracefully.

This demonstrates how to use the SDK CLI login command programmatically.
"""

import os
import sys

import pytest

from grant_automation_cli.application_automator import ApplicationAutomator
from grant_automation_cli.sdk_cli import GrantSDKCLI


@pytest.mark.integration
def test_login():
    """Test login functionality."""
    print("=" * 60)
    print("Testing Browser Login Functionality")
    print("=" * 60)

    # Get credentials
    username = os.getenv("4CULTURE_USERNAME", "")
    password = os.getenv("4CULTURE_PASSWORD", "")

    print(f"\nUsername: {username}")
    print(f"Password: {'*' * len(password)}")

    # Initialize CLI
    cli = GrantSDKCLI()

    # Try to get MCP tools
    print("\n1. Checking for MCP browser tools...")
    mcp_tools = cli._get_mcp_browser_tools()

    if not mcp_tools:
        print("   ❌ MCP browser tools not available")
        print("\n   Note: MCP tools are only available in MCP-enabled environments.")
        print("   In Cursor IDE, MCP tools should be automatically available.")
        print("   In regular terminal, you may need to configure MCP server.")
        return False

    print(f"   ✅ Found {len(mcp_tools)} MCP browser tools")
    print(f"   Tools: {', '.join(list(mcp_tools.keys())[:5])}...")

    # Test login
    print("\n2. Attempting to login...")
    try:
        automator = ApplicationAutomator(username, password, mcp_tools=mcp_tools)
        success = automator.login()

        if success:
            current_url = automator.get_current_page_url()
            print("   ✅ Login successful!")
            print(f"   Current URL: {current_url}")

            # Take a screenshot
            screenshot = automator.browser.take_screenshot("login_test")
            if screenshot:
                print(f"   Screenshot saved: {screenshot}")

            # Close browser
            automator.close()
            return True
        else:
            print("   ❌ Login failed")
            return False

    except Exception as e:
        print(f"   ❌ Error during login: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_login()
    sys.exit(0 if success else 1)
