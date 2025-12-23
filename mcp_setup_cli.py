#!/usr/bin/env python3
"""
MCP Tools Setup CLI
Interactive tool for configuring MCP servers and injecting browser tools.
"""

import sys
from pathlib import Path

# Add parent directory to path BEFORE any other imports
# This allows the module to be run from any directory
# Path structure: /path/to/Grants/agents/grant_scraper/mcp_setup_cli.py
# Project root is 2 levels up: /path/to/Grants
_script_file = Path(__file__).resolve()
_script_dir = _script_file.parent
_project_root = _script_dir.parent.parent  # Go up 2 levels: grant_scraper -> agents -> Grants

if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

# Now import everything else
import argparse
import logging

from agents.grant_scraper.mcp_server_config import (
    MCPServerConfig,
    configure_mcp_server_interactive,
    get_mcp_tools_from_server
)
from agents.grant_scraper.mcp_server_runner import MCPServerRunner
from agents.grant_scraper.inject_mcp_tools import (
    inject_available_mcp_tools,
    inject_tools_from_dict,
    inject_tools_from_mcp_server,
    setup_mcp_tools_auto
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def cmd_configure(args):
    """Configure MCP server interactively."""
    configure_mcp_server_interactive()


def cmd_list_servers(args):
    """List configured MCP servers."""
    config = MCPServerConfig()
    servers = config.list_servers()
    
    if servers:
        print("\nConfigured MCP Servers:")
        for server in servers:
            server_config = config.get_server_config(server)
            status = "✅ Enabled" if server_config.get('enabled') else "❌ Disabled"
            server_type = server_config.get('type', 'unknown')
            print(f"  - {server} ({server_type}) - {status}")
        
        default = config.config.get('default_server')
        if default:
            print(f"\nDefault server: {default}")
    else:
        print("\nNo MCP servers configured.")
        print("Run 'configure' to set up a server.")


def cmd_test_connection(args):
    """Test connection to MCP server."""
    server_name = args.server_name
    print(f"\nTesting connection to MCP server: {server_name or 'default'}")
    
    tools = get_mcp_tools_from_server(server_name)
    
    if tools:
        print(f"✅ Successfully connected!")
        print(f"   Found {len(tools)} tools:")
        for tool_name in list(tools.keys())[:10]:
            print(f"   - {tool_name}")
        if len(tools) > 10:
            print(f"   ... and {len(tools) - 10} more")
    else:
        print("❌ Connection failed or no tools available")
        print("\nTroubleshooting:")
        print("  1. Check server configuration")
        print("  2. Verify MCP server is running")
        print("  3. Check server credentials/API keys")


def cmd_inject_tools(args):
    """Inject MCP tools from server."""
    server_name = args.server_name
    
    print(f"\nInjecting MCP tools from server: {server_name or 'default'}")
    
    success = inject_tools_from_mcp_server(server_name)
    
    if success:
        print("✅ Tools injected successfully!")
        print("\nYou can now use browser automation commands:")
        print("  python3 -m agents.grant_scraper.sdk_cli auth login")
    else:
        print("❌ Failed to inject tools")
        print("\nTry:")
        print("  1. Configure MCP server: python3 -m agents.grant_scraper.mcp_setup_cli configure")
        print("  2. Check server connection: python3 -m agents.grant_scraper.mcp_setup_cli test")


def cmd_auto_setup(args):
    """Automatically set up MCP tools."""
    print("\nAttempting automatic MCP tools setup...")
    
    success = setup_mcp_tools_auto()
    
    if success:
        print("✅ MCP tools set up successfully!")
        print("\nYou can now use browser automation commands:")
        print("  python3 -m agents.grant_scraper.sdk_cli auth login")
    else:
        print("❌ Automatic setup failed")
        print("\nTry manual setup:")
        print("  python3 -m agents.grant_scraper.mcp_setup_cli configure")


def cmd_status(args):
    """Show MCP tools status."""
    from agents.grant_scraper.sdk_cli import GrantSDKCLI
    
    print("\n" + "=" * 60)
    print("MCP Tools Status")
    print("=" * 60)
    
    # Check configuration
    config = MCPServerConfig()
    servers = config.list_servers()
    
    print(f"\n1. Configured Servers: {len(servers)}")
    if servers:
        for server in servers:
            server_config = config.get_server_config(server)
            server_type = server_config.get('type', 'unknown') if server_config else 'unknown'
            status = "✅ Enabled" if server_config and server_config.get('enabled') else "❌ Disabled"
            print(f"   - {server} ({server_type}) - {status}")
        default = config.config.get('default_server')
        if default:
            print(f"   Default: {default}")
    else:
        print("   ⚠️  No servers configured")
        print("   Run 'configure' to set up a server")
    
    # Try to auto-setup tools first
    print("\n2. Tool Availability:")
    print("   Attempting to load tools...")
    
    # Try auto-setup
    setup_success = setup_mcp_tools_auto()
    
    # Check tool availability
    cli = GrantSDKCLI()
    tools = cli._get_mcp_browser_tools()
    
    if tools:
        print(f"   ✅ {len(tools)} MCP tools available")
        tool_names = list(tools.keys())[:5]
        print(f"   Tools: {', '.join(tool_names)}...")
        if len(tools) > 5:
            print(f"   ... and {len(tools) - 5} more")
        print("\n   ✅ Browser automation is ready!")
        print("   You can now use: python3 -m agents.grant_scraper.sdk_cli auth login")
    else:
        print("   ❌ No MCP tools available")
        print("\n   To enable tools:")
        print("   - Run: python3 -m agents.grant_scraper.mcp_setup_cli auto-setup")
        print("   - Or: python3 -m agents.grant_scraper.mcp_setup_cli configure")
        print("   - Or: Use in Cursor IDE where tools are automatically available")
    
    print("\n" + "=" * 60)


def main():
    """Main entry point for MCP setup CLI."""
    parser = argparse.ArgumentParser(
        description='MCP Tools Setup and Configuration',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Configure MCP server interactively
  python3 -m agents.grant_scraper.mcp_setup_cli configure
  
  # List configured servers
  python3 -m agents.grant_scraper.mcp_setup_cli list
  
  # Test server connection
  python3 -m agents.grant_scraper.mcp_setup_cli test
  
  # Inject tools from server
  python3 -m agents.grant_scraper.mcp_setup_cli inject
  
  # Auto-setup tools
  python3 -m agents.grant_scraper.mcp_setup_cli auto-setup
  
  # Check status
  python3 -m agents.grant_scraper.mcp_setup_cli status
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    subparsers.required = True
    
    # Configure command
    subparsers.add_parser('configure', help='Configure MCP server interactively')
    
    # List command
    subparsers.add_parser('list', help='List configured MCP servers')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test MCP server connection')
    test_parser.add_argument('--server-name', help='Server name to test')
    
    # Inject command
    inject_parser = subparsers.add_parser('inject', help='Inject MCP tools from server')
    inject_parser.add_argument('--server-name', help='Server name to use')
    
    # Auto-setup command
    subparsers.add_parser('auto-setup', help='Automatically set up MCP tools')
    
    # Status command
    subparsers.add_parser('status', help='Show MCP tools status')
    
    # Run server command
    run_parser = subparsers.add_parser('run-server', help='Start MCP server')
    run_parser.add_argument('--server-name', help='Server name to start')
    run_parser.add_argument('--cmd', dest='custom_command', help='Custom command to run')
    
    # Stop server command
    stop_parser = subparsers.add_parser('stop-server', help='Stop MCP server')
    stop_parser.add_argument('--server-name', help='Server name to stop')
    
    # Parse arguments
    # Debug: Print sys.argv to see what's being passed
    logger.debug(f"sys.argv: {sys.argv}")
    
    # Parse arguments - argparse handles sys.argv automatically
    # When run as module with -m, Python sets sys.argv[0] to module path
    # and sys.argv[1:] to the actual arguments, which argparse handles correctly
    args = parser.parse_args()
    
    if not hasattr(args, 'command') or args.command is None:
        # If no command provided, show help
        logger.error("No command provided in args")
        parser.print_help()
        sys.exit(1)
    
    # Define command handlers
    def cmd_run_server(args):
        """Start MCP server."""
        runner = MCPServerRunner()
        server_name = getattr(args, 'server_name', None)
        command = getattr(args, 'custom_command', None)
        
        print(f"\nStarting MCP server: {server_name or 'default'}")
        success = runner.start_server(server_name=server_name, command=command)
        
        if success:
            print("✅ MCP server started successfully")
            print("\nServer is now running. You can:")
            print("  - Check status: python3 -m agents.grant_scraper.mcp_setup_cli status")
            print("  - Inject tools: python3 -m agents.grant_scraper.mcp_setup_cli inject")
        else:
            print("❌ Failed to start MCP server")
            print("\nTroubleshooting:")
            print("  1. Check server configuration")
            print("  2. Verify server command is correct")
            print("  3. Check if server is already running")
            print("  4. Note: Cursor IDE browser tools are built-in and don't need a server")
    
    def cmd_stop_server(args):
        """Stop MCP server."""
        runner = MCPServerRunner()
        server_name = getattr(args, 'server_name', None)
        
        if server_name:
            print(f"\nStopping MCP server: {server_name}")
        else:
            print(f"\nStopping all MCP servers")
        
        success = runner.stop_server(server_name=server_name)
        
        if success:
            if server_name:
                print(f"✅ MCP server '{server_name}' stopped successfully")
            else:
                print("✅ All MCP servers stopped successfully")
        else:
            print("❌ Failed to stop MCP server")
            print("\nNote: If server was not running, this is expected behavior")
    
    command_map = {
        'configure': cmd_configure,
        'list': cmd_list_servers,
        'test': cmd_test_connection,
        'inject': cmd_inject_tools,
        'auto-setup': cmd_auto_setup,
        'status': cmd_status,
        'run-server': cmd_run_server,
        'stop-server': cmd_stop_server,
    }
    
    handler = command_map.get(args.command)
    if handler:
        try:
            handler(args)
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()

