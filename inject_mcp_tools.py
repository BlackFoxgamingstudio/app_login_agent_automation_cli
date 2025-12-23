"""
Script to inject MCP tools into the SDK CLI.
This allows MCP tools to be made available to the CLI when running in Cursor IDE.

Usage:
    from agents.grant_scraper.inject_mcp_tools import inject_available_mcp_tools
    inject_available_mcp_tools()
    
    # Now SDK CLI can use MCP tools
    from agents.grant_scraper.sdk_cli import GrantSDKCLI
    cli = GrantSDKCLI()
    mcp_tools = cli._get_mcp_browser_tools()  # Will now return tools
"""

import logging
import sys
from typing import Dict, Any, Optional, Callable

logger = logging.getLogger(__name__)


def inject_available_mcp_tools(mcp_tools_dict: Optional[Dict[str, Any]] = None):
    """
    Inject MCP tools into the helper module.
    
    This function should be called with a dictionary of MCP tool functions
    when they're available (e.g., from Cursor IDE's tool interface).
    
    Args:
        mcp_tools_dict: Dictionary of MCP tool functions to inject
    """
    from .mcp_tools_helper import inject_mcp_tools
    
    if mcp_tools_dict:
        inject_mcp_tools(mcp_tools_dict)
        logger.info(f"Injected {len(mcp_tools_dict)} MCP tools")
        return True
    else:
        # Try to collect from environment
        from .mcp_tools_helper import get_mcp_tools_from_environment
        tools = get_mcp_tools_from_environment()
        if tools:
            inject_mcp_tools(tools)
            logger.info(f"Injected {len(tools)} MCP tools from environment")
            return True
        else:
            logger.warning("No MCP tools available to inject")
            return False


def inject_tools_from_dict(tool_dict: Dict[str, Callable]):
    """
    Inject MCP tools from a dictionary of callable functions.
    
    This is a convenience function for injecting tools that are already
    available as Python callables.
    
    Args:
        tool_dict: Dictionary mapping tool names to callable functions
        
    Example:
        tools = {
            'cursor_ide_browser_navigate': my_navigate_function,
            'cursor_ide_browser_click': my_click_function,
            # ... etc
        }
        inject_tools_from_dict(tools)
    """
    from .mcp_tools_helper import inject_mcp_tools
    
    # Map tool names to expected format
    mapped_tools = {}
    
    # Tool name mappings
    name_mappings = {
        # Cursor IDE browser tools
        'cursor_ide_browser_navigate': 'mcp_cursor-ide-browser_browser_navigate',
        'cursor_ide_browser_snapshot': 'mcp_cursor-ide-browser_browser_snapshot',
        'cursor_ide_browser_click': 'mcp_cursor-ide-browser_browser_click',
        'cursor_ide_browser_type': 'mcp_cursor-ide-browser_browser_type',
        'cursor_ide_browser_select_option': 'mcp_cursor-ide-browser_browser_select_option',
        'cursor_ide_browser_wait_for': 'mcp_cursor-ide-browser_browser_wait_for',
        'cursor_ide_browser_take_screenshot': 'mcp_cursor-ide-browser_browser_take_screenshot',
        # Browserbase tools
        'browserbase_session_create': 'mcp_Browserbase_browserbase_session_create',
        'browserbase_stagehand_navigate': 'mcp_Browserbase_browserbase_stagehand_navigate',
        'browserbase_stagehand_act': 'mcp_Browserbase_browserbase_stagehand_act',
        'browserbase_stagehand_observe': 'mcp_Browserbase_browserbase_stagehand_observe',
        'browserbase_screenshot': 'mcp_Browserbase_browserbase_screenshot',
    }
    
    # Map provided tools
    for tool_name, tool_func in tool_dict.items():
        # Try exact match first
        if tool_name in name_mappings:
            mapped_tools[name_mappings[tool_name]] = tool_func
        # Try reverse lookup (if key is the MCP tool name)
        elif tool_name.startswith('mcp_'):
            mapped_tools[tool_name] = tool_func
        # Try case-insensitive match
        else:
            tool_name_lower = tool_name.lower()
            for key, mcp_key in name_mappings.items():
                if key.lower() == tool_name_lower:
                    mapped_tools[mcp_key] = tool_func
                    break
    
    if mapped_tools:
        inject_mcp_tools(mapped_tools)
        logger.info(f"Injected {len(mapped_tools)} MCP tools from dictionary")
        return True
    else:
        logger.warning("No valid MCP tools found in dictionary")
        return False


def inject_tools_from_mcp_server(server_name: Optional[str] = None) -> bool:
    """
    Inject MCP tools from a configured MCP server.
    
    Args:
        server_name: Name of MCP server (uses default if not provided)
        
    Returns:
        True if tools were injected, False otherwise
    """
    try:
        from .mcp_server_config import get_mcp_tools_from_server
        
        tools = get_mcp_tools_from_server(server_name)
        if tools:
            logger.info(f"Successfully loaded tools from MCP server")
            return True
        else:
            logger.warning("No tools available from MCP server")
            return False
    except ImportError:
        logger.warning("MCP server config module not available")
        return False
    except Exception as e:
        logger.error(f"Error loading tools from MCP server: {e}")
        return False


def create_mcp_tools_from_cursor_functions() -> Optional[Dict[str, Any]]:
    """
    Create MCP tools dictionary from Cursor IDE functions.
    
    This function creates wrapper functions that can call the actual
    MCP tools available in Cursor IDE.
    
    Returns:
        Dictionary of MCP tool wrapper functions
    """
    # Note: In Cursor IDE, MCP tools are available via the tool calling interface
    # This creates a structure that can be used, but the actual tool calls
    # need to be made through the tool interface
    
    tools = {}
    
    # Create wrapper functions that will be called by the integration layer
    # The actual implementation will use the MCP tool calling interface
    
    logger.info("MCP tools structure created for Cursor IDE environment")
    return tools if tools else None


def setup_mcp_tools_auto() -> bool:
    """
    Automatically set up MCP tools from available sources.
    
    Tries multiple methods:
    1. MCP server configuration
    2. Environment detection
    3. Manual injection
    
    Returns:
        True if tools were set up, False otherwise
    """
    logger.info("Attempting automatic MCP tools setup...")
    
    # Try MCP server first
    if inject_tools_from_mcp_server():
        return True
    
    # Try environment detection
    if inject_available_mcp_tools():
        return True
    
    logger.warning("Could not automatically set up MCP tools")
    return False

