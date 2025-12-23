"""
Helper module for accessing MCP browser tools.
This module provides a way to collect and organize MCP browser tools for use in automation.
"""

import logging
import sys
import builtins
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Global registry for manually injected MCP tools
_injected_tools: Optional[Dict[str, Any]] = None


def inject_mcp_tools(tools: Dict[str, Any]):
    """
    Manually inject MCP tools into the helper.
    This allows tools to be provided from external sources.
    
    Args:
        tools: Dictionary of MCP tool functions
    """
    global _injected_tools
    _injected_tools = tools
    logger.info(f"Injected {len(tools)} MCP tools manually")


def collect_mcp_browser_tools() -> Optional[Dict[str, Any]]:
    """
    Collect MCP browser tools from multiple sources.
    
    Checks:
    1. Manually injected tools
    2. Built-in namespace
    3. Main module globals
    4. Current frame globals
    
    Returns:
        Dictionary of MCP tool functions or None if not available
    """
    # Check manually injected tools first
    if _injected_tools:
        logger.info(f"Using {len(_injected_tools)} manually injected MCP tools")
        return _injected_tools
    
    # Try to collect from various sources
    sources = [
        builtins.__dict__,
        sys.modules.get('__main__', {}).__dict__ if '__main__' in sys.modules else {},
    ]
    
    # Add current frame globals
    try:
        frame = sys._getframe(1)
        sources.append(frame.f_globals)
    except:
        pass
    
    # Try each source
    for source in sources:
        tools = create_mcp_tools_dict_from_globals(source)
        if tools:
            logger.info(f"Found {len(tools)} MCP tools from source")
            return tools
    
    logger.warning("No MCP browser tools found in any source")
    return None


def create_mcp_tools_dict_from_globals(globals_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create MCP tools dictionary from global namespace.
    
    This function looks for MCP browser tool functions in the global namespace
    and organizes them into a dictionary.
    
    Args:
        globals_dict: Dictionary of global variables (typically globals())
        
    Returns:
        Dictionary of MCP tool functions
    """
    mcp_tools = {}
    
    # Browserbase/Stagehand single session tools
    browserbase_tools = {
        'browserbase_session_create': 'mcp_Browserbase_browserbase_session_create',
        'browserbase_session_close': 'mcp_Browserbase_browserbase_session_close',
        'browserbase_stagehand_navigate': 'mcp_Browserbase_browserbase_stagehand_navigate',
        'browserbase_stagehand_act': 'mcp_Browserbase_browserbase_stagehand_act',
        'browserbase_stagehand_observe': 'mcp_Browserbase_browserbase_stagehand_observe',
        'browserbase_stagehand_extract': 'mcp_Browserbase_browserbase_stagehand_extract',
        'browserbase_stagehand_get_url': 'mcp_Browserbase_browserbase_stagehand_get_url',
        'browserbase_screenshot': 'mcp_Browserbase_browserbase_screenshot',
    }
    
    # Multi-session tools
    multi_session_tools = {
        'multi_browserbase_stagehand_session_create': 'mcp_Browserbase_multi_browserbase_stagehand_session_create',
        'multi_browserbase_stagehand_session_close': 'mcp_Browserbase_multi_browserbase_stagehand_session_close',
        'multi_browserbase_stagehand_session_list': 'mcp_Browserbase_multi_browserbase_stagehand_session_list',
        'multi_browserbase_stagehand_navigate_session': 'mcp_Browserbase_multi_browserbase_stagehand_navigate_session',
        'multi_browserbase_stagehand_act_session': 'mcp_Browserbase_multi_browserbase_stagehand_act_session',
        'multi_browserbase_stagehand_observe_session': 'mcp_Browserbase_multi_browserbase_stagehand_observe_session',
        'multi_browserbase_stagehand_extract_session': 'mcp_Browserbase_multi_browserbase_stagehand_extract_session',
        'multi_browserbase_stagehand_get_url_session': 'mcp_Browserbase_multi_browserbase_stagehand_get_url_session',
    }
    
    # Cursor IDE browser tools
    cursor_tools = {
        'cursor_ide_browser_navigate': 'mcp_cursor-ide-browser_browser_navigate',
        'cursor_ide_browser_snapshot': 'mcp_cursor-ide-browser_browser_snapshot',
        'cursor_ide_browser_click': 'mcp_cursor-ide-browser_browser_click',
        'cursor_ide_browser_type': 'mcp_cursor-ide-browser_browser_type',
        'cursor_ide_browser_select_option': 'mcp_cursor-ide-browser_browser_select_option',
        'cursor_ide_browser_wait_for': 'mcp_cursor-ide-browser_browser_wait_for',
        'cursor_ide_browser_get_url': 'mcp_cursor-ide-browser_browser_get_url',
        'cursor_ide_browser_take_screenshot': 'mcp_cursor-ide-browser_browser_take_screenshot',
    }
    
    # Try to find tools in globals
    all_tool_mappings = {**browserbase_tools, **multi_session_tools, **cursor_tools}
    
    for tool_name, tool_key in all_tool_mappings.items():
        # Try exact key match
        if tool_key in globals_dict:
            tool_func = globals_dict[tool_key]
            if callable(tool_func):
                mcp_tools[tool_name] = tool_func
                logger.debug(f"Found MCP tool: {tool_name} (key: {tool_key})")
                continue
        
        # Try case-insensitive search
        tool_key_lower = tool_key.lower()
        for key, value in globals_dict.items():
            if key.lower() == tool_key_lower and callable(value):
                mcp_tools[tool_name] = value
                logger.debug(f"Found MCP tool: {tool_name} (key: {key})")
                break
        
        # Try partial match (for variations in naming)
        for key, value in globals_dict.items():
            if tool_key.replace('_', '').replace('-', '').lower() in key.replace('_', '').replace('-', '').lower():
                if callable(value) and 'browser' in key.lower():
                    mcp_tools[tool_name] = value
                    logger.debug(f"Found MCP tool: {tool_name} (partial match: {key})")
                    break
    
    if mcp_tools:
        logger.info(f"Collected {len(mcp_tools)} MCP browser tools")
        return mcp_tools
    else:
        return None


def get_mcp_tools_from_environment() -> Optional[Dict[str, Any]]:
    """
    Comprehensive MCP tools collection from environment.
    
    This function tries multiple methods to find MCP tools:
    1. Manually injected tools
    2. Built-in namespace
    3. Module globals
    4. Frame globals
    
    Returns:
        Dictionary of MCP tool functions or None
    """
    # Try the comprehensive collection
    tools = collect_mcp_browser_tools()
    
    if tools:
        return tools
    
    # Last resort: try to find any callable with MCP-related names
    mcp_tools = {}
    search_namespaces = [
        builtins.__dict__,
        sys.modules.get('__main__', {}).__dict__ if '__main__' in sys.modules else {},
    ]
    
    # Add current globals
    try:
        frame = sys._getframe(1)
        search_namespaces.append(frame.f_globals)
    except:
        pass
    
    mcp_keywords = ['mcp', 'browser', 'cursor', 'browserbase', 'stagehand']
    
    for namespace in search_namespaces:
        for key, value in namespace.items():
            if not callable(value):
                continue
            
            key_lower = key.lower()
            # Check if it looks like an MCP browser tool
            if any(keyword in key_lower for keyword in mcp_keywords):
                # Map to our standard names
                if 'navigate' in key_lower:
                    mcp_tools.setdefault('browserbase_stagehand_navigate', value)
                elif 'click' in key_lower:
                    mcp_tools.setdefault('cursor_ide_browser_click', value)
                elif 'type' in key_lower and 'browser' in key_lower:
                    mcp_tools.setdefault('cursor_ide_browser_type', value)
                elif 'snapshot' in key_lower:
                    mcp_tools.setdefault('cursor_ide_browser_snapshot', value)
                elif 'screenshot' in key_lower:
                    mcp_tools.setdefault('browserbase_screenshot', value)
    
    if mcp_tools:
        logger.info(f"Found {len(mcp_tools)} MCP tools via keyword search")
        return mcp_tools
    
    return None

