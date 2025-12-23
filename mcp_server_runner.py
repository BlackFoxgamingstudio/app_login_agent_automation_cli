#!/usr/bin/env python3
"""
MCP Server Runner
Provides functionality to start, stop, and manage MCP server processes.
"""

import sys
from pathlib import Path

# Add parent directory to path BEFORE any other imports
# This allows the module to be run from any directory
# Path structure: /path/to/Grants/agents/grant_scraper/mcp_server_runner.py
# Project root is 2 levels up: /path/to/Grants
_script_file = Path(__file__).resolve()
_script_dir = _script_file.parent
_project_root = _script_dir.parent.parent  # Go up 2 levels: grant_scraper -> agents -> Grants

if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

# Now import everything else
import logging
import subprocess
import os
import signal
import json
import time
from typing import Dict, Any, Optional, List

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None

logger = logging.getLogger(__name__)


class MCPServerRunner:
    """Manages MCP server process lifecycle."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize MCP server runner.
        
        Args:
            config_path: Path to MCP server configuration file
        """
        from agents.grant_scraper.mcp_server_config import MCPServerConfig
        self.config = MCPServerConfig(config_path)
        self.processes: Dict[str, subprocess.Popen] = {}
        self.pid_file = Path.home() / '.mcp_server_pids.json'
        self._load_running_servers()
    
    def _load_running_servers(self):
        """Load information about currently running servers."""
        if not PSUTIL_AVAILABLE:
            return
        
        if self.pid_file.exists():
            try:
                with open(self.pid_file, 'r') as f:
                    pid_data = json.load(f)
                    for server_name, pid in pid_data.items():
                        if psutil.pid_exists(pid):
                            try:
                                proc = psutil.Process(pid)
                                if proc.is_running():
                                    logger.info(f"Found running server: {server_name} (PID: {pid})")
                            except psutil.NoSuchProcess:
                                pass
            except Exception as e:
                logger.warning(f"Error loading server PIDs: {e}")
    
    def _save_running_servers(self):
        """Save information about running servers."""
        pid_data = {}
        for server_name, proc in self.processes.items():
            if proc.poll() is None:  # Process is still running
                pid_data[server_name] = proc.pid
        
        try:
            with open(self.pid_file, 'w') as f:
                json.dump(pid_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving server PIDs: {e}")
    
    def start_server(self, server_name: Optional[str] = None, 
                    command: Optional[str] = None) -> bool:
        """
        Start an MCP server.
        
        Args:
            server_name: Name of configured server (uses default if not provided)
            command: Custom command to run (overrides server config)
            
        Returns:
            True if server started successfully, False otherwise
        """
        if server_name:
            server_config = self.config.get_server_config(server_name)
            if not server_config:
                logger.error(f"Server '{server_name}' not found in configuration")
                return False
        else:
            server_name = self.config.config.get('default_server')
            if not server_name:
                logger.error("No default server configured")
                return False
            server_config = self.config.get_server_config(server_name)
        
        if server_name in self.processes:
            proc = self.processes[server_name]
            if proc.poll() is None:
                logger.info(f"Server '{server_name}' is already running (PID: {proc.pid})")
                return True
        
        # Determine command to run
        if command:
            cmd = command.split()
        else:
            cmd = self._get_server_command(server_config)
            if not cmd:
                logger.error(f"Could not determine command for server '{server_name}'")
                return False
        
        try:
            logger.info(f"Starting MCP server: {server_name}")
            logger.info(f"Command: {' '.join(cmd)}")
            
            # Start server process
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                text=True
            )
            
            self.processes[server_name] = proc
            self._save_running_servers()
            
            # Wait a moment to check if it started successfully
            time.sleep(0.5)
            if proc.poll() is None:
                logger.info(f"✅ Server '{server_name}' started (PID: {proc.pid})")
                return True
            else:
                # Process exited immediately - check for errors
                stdout, stderr = proc.communicate()
                logger.error(f"Server '{server_name}' exited immediately")
                if stderr:
                    logger.error(f"Error: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error starting server '{server_name}': {e}")
            return False
    
    def _get_server_command(self, server_config: Dict[str, Any]) -> Optional[List[str]]:
        """
        Get command to run for a server configuration.
        
        Args:
            server_config: Server configuration dictionary
            
        Returns:
            Command as list of strings or None
        """
        server_type = server_config.get('type')
        config = server_config.get('config', {})
        
        if server_type == 'cursor-ide-browser':
            # Cursor IDE browser is built-in, no separate server needed
            logger.info("Cursor IDE browser tools are built-in, no server to start")
            return None
        
        elif server_type == 'playwright':
            # Playwright MCP server
            package = config.get('package', '@playwright/mcp@latest')
            return ['npx', '-y', package]
        
        elif server_type == 'browserbase':
            # Browserbase might use a specific command
            api_key = config.get('api_key')
            package = config.get('package', '@modelcontextprotocol/server-browserbase')
            return ['npx', '-y', package]
        
        elif server_type == 'custom':
            # Custom server command
            cmd = config.get('command') or config.get('url')
            if cmd:
                if isinstance(cmd, str):
                    return cmd.split()
                return cmd
        
        # Try to find MCP server in PATH
        mcp_servers = ['mcp-server', 'mcp_server', 'npx', 'node']
        
        for mcp_cmd in mcp_servers:
            try:
                result = subprocess.run(
                    ['which', mcp_cmd],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    # Found command, construct server command
                    if mcp_cmd == 'npx':
                        # Try common MCP server packages
                        server_package = config.get('package', '@modelcontextprotocol/server-browserbase')
                        return ['npx', '-y', server_package]
                    return [mcp_cmd]
            except:
                continue
        
        return None
    
    def stop_server(self, server_name: Optional[str] = None) -> bool:
        """
        Stop a running MCP server.
        
        Args:
            server_name: Name of server to stop (stops all if not provided)
            
        Returns:
            True if server stopped successfully, False otherwise
        """
        if server_name:
            if server_name not in self.processes:
                logger.info(f"Server '{server_name}' is not running (not in running processes)")
                return True  # Already stopped, so success
            
            proc = self.processes[server_name]
            if proc.poll() is None:
                logger.info(f"Stopping server '{server_name}' (PID: {proc.pid})")
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                    logger.info(f"✅ Server '{server_name}' stopped")
                except subprocess.TimeoutExpired:
                    logger.warning(f"Server '{server_name}' didn't stop, killing...")
                    proc.kill()
                    proc.wait()
                    logger.info(f"✅ Server '{server_name}' killed")
                
                del self.processes[server_name]
                self._save_running_servers()
                return True
            else:
                logger.info(f"Server '{server_name}' is not running (process already exited)")
                del self.processes[server_name]
                self._save_running_servers()
                return True
        else:
            # Stop all servers
            stopped = True
            for name in list(self.processes.keys()):
                if not self.stop_server(name):
                    stopped = False
            return stopped
    
    def list_running_servers(self) -> List[Dict[str, Any]]:
        """
        List currently running MCP servers.
        
        Returns:
            List of server information dictionaries
        """
        running = []
        for server_name, proc in self.processes.items():
            if proc.poll() is None:
                server_info = {
                    'name': server_name,
                    'pid': proc.pid,
                    'status': 'running'
                }
                
                if PSUTIL_AVAILABLE:
                    try:
                        proc_info = psutil.Process(proc.pid)
                        server_info['cpu_percent'] = proc_info.cpu_percent()
                        server_info['memory_mb'] = proc_info.memory_info().rss / 1024 / 1024
                    except psutil.NoSuchProcess:
                        # Process died
                        del self.processes[server_name]
                        continue
                
                running.append(server_info)
        
        self._save_running_servers()
        return running
    
    def check_server_health(self, server_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Check health of MCP server.
        
        Args:
            server_name: Name of server to check (checks default if not provided)
            
        Returns:
            Health status dictionary
        """
        if not server_name:
            server_name = self.config.config.get('default_server')
        
        if not server_name:
            return {'status': 'error', 'message': 'No server configured'}
        
        if server_name not in self.processes:
            return {'status': 'not_running', 'server': server_name}
        
        proc = self.processes[server_name]
        if proc.poll() is None:
            health = {
                'status': 'healthy',
                'server': server_name,
                'pid': proc.pid
            }
            
            if PSUTIL_AVAILABLE:
                try:
                    proc_info = psutil.Process(proc.pid)
                    health['cpu_percent'] = proc_info.cpu_percent()
                    health['memory_mb'] = proc_info.memory_info().rss / 1024 / 1024
                except psutil.NoSuchProcess:
                    return {'status': 'dead', 'server': server_name}
            
            return health
        else:
            return {'status': 'stopped', 'server': server_name}


def run_mcp_server_interactive():
    """Interactive MCP server management."""
    runner = MCPServerRunner()
    
    print("=" * 60)
    print("MCP Server Runner")
    print("=" * 60)
    
    while True:
        print("\nOptions:")
        print("  1. Start server")
        print("  2. Stop server")
        print("  3. List running servers")
        print("  4. Check server health")
        print("  5. Exit")
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == '1':
            server_name = input("Server name (default: use default server): ").strip() or None
            if runner.start_server(server_name):
                print("✅ Server started successfully")
            else:
                print("❌ Failed to start server")
        
        elif choice == '2':
            server_name = input("Server name (default: stop all): ").strip() or None
            if runner.stop_server(server_name):
                print("✅ Server stopped successfully")
            else:
                print("❌ Failed to stop server")
        
        elif choice == '3':
            running = runner.list_running_servers()
            if running:
                print("\nRunning Servers:")
                for server in running:
                    cpu_info = f"CPU: {server.get('cpu_percent', 0):.1f}%" if 'cpu_percent' in server else ""
                    mem_info = f"Memory: {server.get('memory_mb', 0):.1f} MB" if 'memory_mb' in server else ""
                    info_parts = [cpu_info, mem_info]
                    info_str = ", ".join([p for p in info_parts if p])
                    if info_str:
                        print(f"  - {server['name']} (PID: {server['pid']}, {info_str})")
                    else:
                        print(f"  - {server['name']} (PID: {server['pid']})")
            else:
                print("\nNo servers running")
        
        elif choice == '4':
            server_name = input("Server name (default: check default): ").strip() or None
            health = runner.check_server_health(server_name)
            print(f"\nServer Health: {health['status']}")
            if 'pid' in health:
                print(f"  PID: {health['pid']}")
            if 'cpu_percent' in health:
                print(f"  CPU: {health['cpu_percent']:.1f}%")
            if 'memory_mb' in health:
                print(f"  Memory: {health['memory_mb']:.1f} MB")
            if 'message' in health:
                print(f"  Message: {health['message']}")
        
        elif choice == '5':
            print("Exiting...")
            break
        
        else:
            print("Invalid option")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='MCP Server Runner')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    subparsers.required = True
    
    # Start command
    start_parser = subparsers.add_parser('start', help='Start MCP server')
    start_parser.add_argument('--server-name', help='Server name to start')
    start_parser.add_argument('--cmd', dest='custom_command', help='Custom command to run')
    
    # Stop command
    stop_parser = subparsers.add_parser('stop', help='Stop MCP server')
    stop_parser.add_argument('--server-name', help='Server name to stop')
    
    # List command
    subparsers.add_parser('list', help='List running servers')
    
    # Health command
    health_parser = subparsers.add_parser('health', help='Check server health')
    health_parser.add_argument('--server-name', help='Server name to check')
    
    # Interactive command
    subparsers.add_parser('interactive', help='Interactive server management')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    runner = MCPServerRunner()
    
    if args.command == 'start':
        success = runner.start_server(
            server_name=getattr(args, 'server_name', None),
            command=getattr(args, 'custom_command', None)
        )
        sys.exit(0 if success else 1)
    
    elif args.command == 'stop':
        success = runner.stop_server(
            server_name=getattr(args, 'server_name', None)
        )
        sys.exit(0 if success else 1)
    
    elif args.command == 'list':
        running = runner.list_running_servers()
        if running:
            print("\nRunning MCP Servers:")
            for server in running:
                print(f"  {server['name']} (PID: {server['pid']})")
        else:
            print("\nNo servers running")
    
    elif args.command == 'health':
        health = runner.check_server_health(
            server_name=getattr(args, 'server_name', None)
        )
        print(json.dumps(health, indent=2))
    
    elif args.command == 'interactive':
        run_mcp_server_interactive()

