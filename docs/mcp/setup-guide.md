# MCP Tools Setup Guide

Complete guide for setting up MCP browser tools for grant application automation.

## Quick Start

### In Cursor IDE (Recommended - Automatic)

MCP tools are automatically available in Cursor IDE. Just run:

```bash
python3 -m agents.grant_scraper.sdk_cli auth login \
  --username "YOUR_USERNAME" \
  --password "YOUR_PASSWORD"
```

### In Regular Terminal

You have two options:

## Method 1: Configure MCP Server

### Step 1: Configure Server

```bash
python3 -m agents.grant_scraper.mcp_setup_cli configure
```

This will guide you through:
- Selecting server type (Cursor IDE, Browserbase, or Custom)
- Entering server details
- Setting as default server

### Step 2: Test Connection

```bash
python3 -m agents.grant_scraper.mcp_setup_cli test
```

### Step 3: Inject Tools

```bash
python3 -m agents.grant_scraper.mcp_setup_cli inject
```

### Step 4: Verify

```bash
python3 -m agents.grant_scraper.mcp_setup_cli status
```

### Auto-Setup (All-in-One)

```bash
python3 -m agents.grant_scraper.mcp_setup_cli auto-setup
```

This command:
1. Sets up default MCP server configuration
2. Attempts to connect to server
3. Injects available tools
4. Verifies setup

## Method 2: Manual Tool Injection

If you have MCP tool functions available in your Python environment:

### Option A: Inject from Dictionary

```python3
from agents.grant_scraper.inject_mcp_tools import inject_tools_from_dict

# Create dictionary of tool functions
mcp_tools = {
    'cursor_ide_browser_navigate': my_navigate_function,
    'cursor_ide_browser_snapshot': my_snapshot_function,
    'cursor_ide_browser_click': my_click_function,
    'cursor_ide_browser_type': my_type_function,
    'cursor_ide_browser_select_option': my_select_function,
    'cursor_ide_browser_wait_for': my_wait_function,
    'cursor_ide_browser_take_screenshot': my_screenshot_function,
}

# Inject tools
inject_tools_from_dict(mcp_tools)

# Now SDK CLI can use them
from agents.grant_scraper.sdk_cli import GrantSDKCLI
cli = GrantSDKCLI()
tools = cli._get_mcp_browser_tools()  # Returns tools
```

### Option B: Inject from MCP Server

```python3
from agents.grant_scraper.inject_mcp_tools import inject_tools_from_mcp_server

# Inject tools from configured server
inject_tools_from_mcp_server('server-name')

# Or use default server
inject_tools_from_mcp_server()
```

### Option C: Auto-Setup

```python3
from agents.grant_scraper.inject_mcp_tools import setup_mcp_tools_auto

# Try all methods automatically
setup_mcp_tools_auto()
```

## Server Configuration File

Configuration is stored in `~/.mcp_servers.json`:

```json
{
  "servers": {
    "cursor-ide-browser": {
      "type": "cursor-ide-browser",
      "config": {
        "description": "Cursor IDE built-in browser tools",
        "auto_detect": true
      },
      "enabled": true
    }
  },
  "default_server": "cursor-ide-browser",
  "browser_tools": {}
}
```

## Available MCP Tools

### Cursor IDE Browser Tools
- `mcp_cursor-ide-browser_browser_navigate` - Navigate to URL
- `mcp_cursor-ide-browser_browser_snapshot` - Take page snapshot
- `mcp_cursor-ide-browser_browser_click` - Click element
- `mcp_cursor-ide-browser_browser_type` - Type text
- `mcp_cursor-ide-browser_browser_select_option` - Select dropdown
- `mcp_cursor-ide-browser_browser_wait_for` - Wait for condition
- `mcp_cursor-ide-browser_browser_take_screenshot` - Take screenshot

### Browserbase/Stagehand Tools
- `mcp_Browserbase_browserbase_session_create` - Create session
- `mcp_Browserbase_browserbase_stagehand_navigate` - Navigate
- `mcp_Browserbase_browserbase_stagehand_act` - Perform action
- `mcp_Browserbase_browserbase_stagehand_observe` - Observe page
- `mcp_Browserbase_browserbase_screenshot` - Take screenshot

## Troubleshooting

### "No MCP tools available"

**Solution 1:** Use auto-setup
```bash
python3 -m agents.grant_scraper.mcp_setup_cli auto-setup
```

**Solution 2:** Configure manually
```bash
python3 -m agents.grant_scraper.mcp_setup_cli configure
python3 -m agents.grant_scraper.mcp_setup_cli inject
```

**Solution 3:** Use in Cursor IDE
- MCP tools are automatically available in Cursor IDE
- No configuration needed

### "Connection failed"

**Check:**
1. MCP server is running
2. Server credentials are correct
3. Network connectivity

**Test:**
```bash
python3 -m agents.grant_scraper.mcp_setup_cli test
```

### "Tools not injected"

**Verify:**
```bash
python3 -m agents.grant_scraper.mcp_setup_cli status
```

**Re-inject:**
```bash
python3 -m agents.grant_scraper.mcp_setup_cli inject
```

## Verification

After setup, verify tools are available:

```bash
# Check status
python3 -m agents.grant_scraper.mcp_setup_cli status

# Test login
python3 -m agents.grant_scraper.sdk_cli auth login \
  --username "YOUR_USERNAME" \
  --password "YOUR_PASSWORD"
```

## Best Practices

1. **Use Cursor IDE** for development (tools automatically available)
2. **Configure MCP Server** for production/CI environments
3. **Test connection** before running automation
4. **Check status** regularly to verify tools are available
5. **Use auto-setup** for quick setup in new environments

## Examples

### Complete Setup Workflow

```bash
# 1. Configure server
python3 -m agents.grant_scraper.mcp_setup_cli configure

# 2. Test connection
python3 -m agents.grant_scraper.mcp_setup_cli test

# 3. Inject tools
python3 -m agents.grant_scraper.mcp_setup_cli inject

# 4. Verify
python3 -m agents.grant_scraper.mcp_setup_cli status

# 5. Use SDK CLI
python3 -m agents.grant_scraper.sdk_cli auth login \
  --username "YOUR_USERNAME" \
  --password "YOUR_PASSWORD"
```

### Python API Usage

```python3
from agents.grant_scraper.inject_mcp_tools import setup_mcp_tools_auto
from agents.grant_scraper.sdk_cli import GrantSDKCLI

# Setup tools
setup_mcp_tools_auto()

# Use SDK CLI
cli = GrantSDKCLI()
tools = cli._get_mcp_browser_tools()

if tools:
    print(f"✅ {len(tools)} tools available")
    # Proceed with automation
else:
    print("❌ Tools not available")
```

## Support

For issues or questions:
1. Check status: `python3 -m agents.grant_scraper.mcp_setup_cli status`
2. Review logs for error messages
3. Verify MCP server configuration
4. Test connection separately

