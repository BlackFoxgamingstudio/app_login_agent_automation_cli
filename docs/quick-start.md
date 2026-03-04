# Quick Start - MCP Server

## First Command to Run Server

### Option 1: Using Setup CLI (Recommended)

```bash
# From project root
python3 -m agents.grant_scraper.mcp_setup_cli run-server

# Or from grant_scraper directory
cd agents/grant_scraper
python3 mcp_setup_cli.py run-server
```

### Option 2: Using Server Runner Directly

```bash
# From project root
python3 -m agents.grant_scraper.mcp_server_runner start

# Or from grant_scraper directory
cd agents/grant_scraper
python3 mcp_server_runner.py start
```

## Command Options

### Start with specific server name:
```bash
python3 -m agents.grant_scraper.mcp_setup_cli run-server --server-name cursor-ide-browser
```

### Start with custom command:
```bash
python3 -m agents.grant_scraper.mcp_setup_cli run-server --cmd "npx -y @modelcontextprotocol/server-browserbase"
```

## After Starting Server

1. **Check if server is running:**
   ```bash
   python3 -m agents.grant_scraper.mcp_server_runner list
   ```

2. **Check server health:**
   ```bash
   python3 -m agents.grant_scraper.mcp_server_runner health
   ```

3. **Inject tools:**
   ```bash
   python3 -m agents.grant_scraper.mcp_setup_cli inject
   ```

4. **Use SDK CLI:**
   ```bash
   python3 -m agents.grant_scraper.sdk_cli auth login \
     --username "Keyisaccess" \
     --password "Outlaw22!!"
   ```

## Note

**Cursor IDE Browser Tools:** These are built-in and don't require a separate server. The commands will show a message indicating this is expected behavior.

For other MCP servers (Browserbase, custom), you'll need to configure and start them separately.

