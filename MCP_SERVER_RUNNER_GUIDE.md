# MCP Server Runner Guide

Complete guide for running and managing MCP servers for browser automation.

## Quick Start

### Start MCP Server

```bash
# Start default server
python3 -m agents.grant_scraper.mcp_setup_cli run-server

# Start specific server
python3 -m agents.grant_scraper.mcp_setup_cli run-server --server-name cursor-ide-browser

# Start with custom command
python3 -m agents.grant_scraper.mcp_setup_cli run-server --command "npx -y @modelcontextprotocol/server-browserbase"
```

### Using the Runner Directly

```bash
# Start server
python3 -m agents.grant_scraper.mcp_server_runner start

# List running servers
python3 -m agents.grant_scraper.mcp_server_runner list

# Check server health
python3 -m agents.grant_scraper.mcp_server_runner health

# Stop server
python3 -m agents.grant_scraper.mcp_server_runner stop

# Interactive mode
python3 -m agents.grant_scraper.mcp_server_runner interactive
```

## Server Types

### 1. Cursor IDE Browser (Built-in)

**Status:** No separate server needed

Cursor IDE browser tools are built-in and automatically available. No server process is required.

```bash
# This will show that no server is needed
python3 -m agents.grant_scraper.mcp_setup_cli run-server --server-name cursor-ide-browser
```

### 2. Browserbase/Stagehand

**Status:** Requires MCP server package

If using Browserbase, you need to install and run the MCP server:

```bash
# Install MCP server (if not using npx)
npm install -g @modelcontextprotocol/server-browserbase

# Start server with custom command
python3 -m agents.grant_scraper.mcp_setup_cli run-server \
  --command "npx -y @modelcontextprotocol/server-browserbase"
```

### 3. Custom MCP Server

**Status:** Configure and run custom server

```bash
# Configure custom server first
python3 -m agents.grant_scraper.mcp_setup_cli configure

# Then start it
python3 -m agents.grant_scraper.mcp_setup_cli run-server --server-name your-server-name
```

## Server Management

### Check Running Servers

```bash
# List all running servers
python3 -m agents.grant_scraper.mcp_server_runner list

# Output example:
# Running MCP Servers:
#   browserbase (PID: 12345)
#   custom-server (PID: 12346)
```

### Check Server Health

```bash
# Check default server health
python3 -m agents.grant_scraper.mcp_server_runner health

# Check specific server
python3 -m agents.grant_scraper.mcp_server_runner health --server-name browserbase

# Output example:
# {
#   "status": "healthy",
#   "server": "browserbase",
#   "pid": 12345,
#   "cpu_percent": 2.5,
#   "memory_mb": 45.2
# }
```

### Stop Server

```bash
# Stop default server
python3 -m agents.grant_scraper.mcp_setup_cli stop-server

# Stop specific server
python3 -m agents.grant_scraper.mcp_setup_cli stop-server --server-name browserbase

# Stop all servers
python3 -m agents.grant_scraper.mcp_server_runner stop
```

## Interactive Mode

For interactive server management:

```bash
python3 -m agents.grant_scraper.mcp_server_runner interactive
```

This provides a menu-driven interface:
1. Start server
2. Stop server
3. List running servers
4. Check server health
5. Exit

## Integration with SDK CLI

After starting the MCP server, inject tools and use SDK CLI:

```bash
# 1. Start server
python3 -m agents.grant_scraper.mcp_setup_cli run-server

# 2. Inject tools
python3 -m agents.grant_scraper.mcp_setup_cli inject

# 3. Verify status
python3 -m agents.grant_scraper.mcp_setup_cli status

# 4. Use SDK CLI
python3 -m agents.grant_scraper.sdk_cli auth login \
  --username "Keyisaccess" \
  --password "Outlaw22!!"
```

## Process Management

### PID Tracking

Server PIDs are tracked in `~/.mcp_server_pids.json`:

```json
{
  "browserbase": 12345,
  "custom-server": 12346
}
```

### Automatic Cleanup

The runner automatically:
- Detects dead processes
- Removes them from tracking
- Updates PID file

### Manual Process Management

If a server process becomes unresponsive:

```bash
# Find process
ps aux | grep mcp

# Kill manually
kill <PID>

# Or force kill
kill -9 <PID>
```

## Troubleshooting

### Server Won't Start

**Check:**
1. Server configuration exists
2. Command is correct
3. Required dependencies installed
4. Port not already in use

**Debug:**
```bash
# Check configuration
python3 -m agents.grant_scraper.mcp_setup_cli list

# Test with verbose logging
python3 -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from agents.grant_scraper.mcp_server_runner import MCPServerRunner
runner = MCPServerRunner()
runner.start_server()
"
```

### Server Exits Immediately

**Possible causes:**
- Invalid command
- Missing dependencies
- Configuration error
- Port conflict

**Check logs:**
```bash
# Server stderr will show errors
python3 -m agents.grant_scraper.mcp_server_runner start 2>&1
```

### Server Not Found

**Solution:**
1. Configure server first:
   ```bash
   python3 -m agents.grant_scraper.mcp_setup_cli configure
   ```

2. Then start:
   ```bash
   python3 -m agents.grant_scraper.mcp_setup_cli run-server
   ```

## Best Practices

1. **Start server before automation**
   ```bash
   python3 -m agents.grant_scraper.mcp_setup_cli run-server
   python3 -m agents.grant_scraper.mcp_setup_cli inject
   ```

2. **Check health regularly**
   ```bash
   python3 -m agents.grant_scraper.mcp_server_runner health
   ```

3. **Stop server when done**
   ```bash
   python3 -m agents.grant_scraper.mcp_setup_cli stop-server
   ```

4. **Use Cursor IDE for development**
   - No server needed
   - Tools automatically available
   - Best for development and testing

5. **Use separate server for production**
   - More control
   - Better for CI/CD
   - Can run as service

## Examples

### Complete Workflow

```bash
# 1. Configure server
python3 -m agents.grant_scraper.mcp_setup_cli configure

# 2. Start server
python3 -m agents.grant_scraper.mcp_setup_cli run-server

# 3. Verify running
python3 -m agents.grant_scraper.mcp_server_runner list

# 4. Inject tools
python3 -m agents.grant_scraper.mcp_setup_cli inject

# 5. Check status
python3 -m agents.grant_scraper.mcp_setup_cli status

# 6. Use SDK CLI
python3 -m agents.grant_scraper.sdk_cli auth login \
  --username "Keyisaccess" \
  --password "Outlaw22!!"

# 7. Stop server when done
python3 -m agents.grant_scraper.mcp_setup_cli stop-server
```

### Python API Usage

```python3
from agents.grant_scraper.mcp_server_runner import MCPServerRunner

# Create runner
runner = MCPServerRunner()

# Start server
if runner.start_server('browserbase'):
    print("Server started")
    
    # Check health
    health = runner.check_server_health('browserbase')
    print(f"Server status: {health['status']}")
    
    # List running
    running = runner.list_running_servers()
    print(f"Running servers: {len(running)}")
    
    # Stop when done
    runner.stop_server('browserbase')
```

## Notes

- **Cursor IDE**: No server needed, tools are built-in
- **Browserbase**: Requires MCP server package installation
- **Custom**: Requires proper MCP server implementation
- **Process tracking**: PIDs saved in `~/.mcp_server_pids.json`
- **Auto-cleanup**: Dead processes automatically removed

