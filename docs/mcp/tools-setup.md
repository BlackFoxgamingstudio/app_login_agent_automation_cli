# MCP Tools Setup and Usage Guide

## Overview

The SDK CLI uses MCP (Model Context Protocol) browser tools for automation. These tools are available in different ways depending on your environment.

## Environment-Specific Setup

### Cursor IDE (Recommended)

In Cursor IDE, MCP browser tools are automatically available via the tool calling interface. The SDK CLI will automatically detect and use them.

**No additional setup required!** Just run:

```bash
python3 -m agents.grant_scraper.sdk_cli auth login \
  --username "YOUR_USERNAME" \
  --password "YOUR_PASSWORD"
```

### Regular Terminal

In a regular terminal environment, MCP tools need to be configured via an MCP server.

**Option 1: Configure MCP Server**

1. Install and configure an MCP server that provides browser tools
2. The SDK CLI will automatically detect tools from the MCP server

**Option 2: Manual Injection**

If you have MCP tools available in your Python environment:

```python3
from agents.grant_scraper.inject_mcp_tools import inject_available_mcp_tools

# Create dictionary of MCP tool functions
mcp_tools = {
    'cursor_ide_browser_navigate': your_navigate_function,
    'cursor_ide_browser_snapshot': your_snapshot_function,
    # ... etc
}

# Inject them
inject_available_mcp_tools(mcp_tools)

# Now SDK CLI can use them
from agents.grant_scraper.sdk_cli import GrantSDKCLI
cli = GrantSDKCLI()
# MCP tools will now be available
```

## Available MCP Tools

The SDK CLI supports multiple MCP tool implementations:

### Cursor IDE Browser Tools
- `mcp_cursor-ide-browser_browser_navigate` - Navigate to URL
- `mcp_cursor-ide-browser_browser_snapshot` - Take page snapshot
- `mcp_cursor-ide-browser_browser_click` - Click element
- `mcp_cursor-ide-browser_browser_type` - Type text
- `mcp_cursor-ide-browser_browser_select_option` - Select dropdown
- `mcp_cursor-ide-browser_browser_wait_for` - Wait for condition
- `mcp_cursor-ide-browser_browser_get_url` - Get current URL
- `mcp_cursor-ide-browser_browser_take_screenshot` - Take screenshot

### Browserbase/Stagehand Tools
- `mcp_Browserbase_browserbase_session_create` - Create session
- `mcp_Browserbase_browserbase_stagehand_navigate` - Navigate
- `mcp_Browserbase_browserbase_stagehand_act` - Perform action
- `mcp_Browserbase_browserbase_stagehand_observe` - Observe page
- `mcp_Browserbase_browserbase_stagehand_extract` - Extract data
- `mcp_Browserbase_browserbase_screenshot` - Take screenshot

## Testing MCP Tools Availability

```bash
# Test if MCP tools are available
python3 -c "
from agents.grant_scraper.sdk_cli import GrantSDKCLI
cli = GrantSDKCLI()
tools = cli._get_mcp_browser_tools()
if tools:
    print(f'✅ Found {len(tools)} MCP tools')
    print(f'Tools: {list(tools.keys())[:5]}...')
else:
    print('⚠️  MCP tools not available')
    print('In Cursor IDE, tools are automatically available')
"
```

## Login Test Results

✅ **Login functionality verified and working**

Test performed on December 23, 2025:
- Successfully navigated to login page
- Successfully filled username and password fields
- Successfully clicked login button
- Successfully authenticated and redirected to draft applications page

**Current URL after login:** `https://apply.4culture.org/draft-applications`

## Troubleshooting

### "MCP browser tools not available" Error

**In Cursor IDE:**
- MCP tools should be automatically available
- If not working, check Cursor IDE MCP server configuration
- Restart Cursor IDE if needed

**In Regular Terminal:**
- Configure MCP server with browser tools
- Or use manual injection method (see above)
- Or use workflow commands that don't require browser automation

### Tools Not Detected

The SDK CLI checks multiple sources:
1. Manually injected tools
2. Built-in namespace
3. Module globals
4. Frame globals

If tools aren't found, they may need to be injected manually.

## Best Practices

1. **Use Cursor IDE** for browser automation (tools automatically available)
2. **Use environment variables** for credentials (more secure)
3. **Test login first** before running full workflows
4. **Check tool availability** before running browser commands
5. **Use JSON output** for programmatic use: `--json` flag

## Example: Complete Login Workflow

```bash
# 1. Check if tools are available
python3 -m agents.grant_scraper.sdk_cli auth login --help

# 2. Login (in Cursor IDE)
python3 -m agents.grant_scraper.sdk_cli auth login \
  --username "YOUR_USERNAME" \
  --password "YOUR_PASSWORD"

# 3. Verify login with JSON output
python3 -m agents.grant_scraper.sdk_cli --json auth login \
  --username "YOUR_USERNAME" \
  --password "YOUR_PASSWORD"
```

## Integration with Workflows

Once logged in, you can proceed with other commands:

```bash
# After login, start application
python3 -m agents.grant_scraper.sdk_cli form start \
  --grant-name "Moving Stories"

# Fill form
python3 -m agents.grant_scraper.sdk_cli form fill \
  --instructions-file instructions.json

# Save draft
python3 -m agents.grant_scraper.sdk_cli form save
```

The SDK CLI maintains browser session state, so you can chain commands together.

