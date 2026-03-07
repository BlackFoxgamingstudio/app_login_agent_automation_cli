"""
Direct MCP tools wrapper for Cursor IDE environment.

DEVELOPER GUIDELINE: Environment Coupling Avoidance
This module provides direct access to MCP browser tools when available.
Be careful not to tightly couple the core automation logic to Cursor's specific 
IDE environment. Utilize this as a transient adapter that fails gracefully.
"""

import logging
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)


class MCPToolsDirect:
    """
    Direct wrapper for MCP browser tools.
    This class provides a way to use MCP tools directly when they're available
    via the tool calling interface (like in Cursor IDE).
    """

    def __init__(self):
        """Initialize the direct MCP tools wrapper."""
        self.tools: Dict[str, Callable] = {}
        self._initialize_tools()

    def _initialize_tools(self):
        """Initialize MCP tools - to be called with actual tool functions."""
        # This will be populated by the caller who has access to MCP tools
        pass

    def register_tool(self, name: str, tool_func: Callable):
        """Register an MCP tool function."""
        self.tools[name] = tool_func
        logger.debug(f"Registered MCP tool: {name}")

    def get_tools_dict(self) -> Dict[str, Any]:
        """
        Get dictionary of MCP tools for use with MCPBrowserIntegration.

        Returns:
            Dictionary mapping tool names to functions
        """
        # Map to expected tool names
        mapped_tools = {}

        # Cursor IDE browser tools mapping
        cursor_mappings = {
            "cursor_ide_browser_navigate": "mcp_cursor-ide-browser_browser_navigate",
            "cursor_ide_browser_snapshot": "mcp_cursor-ide-browser_browser_snapshot",
            "cursor_ide_browser_click": "mcp_cursor-ide-browser_browser_click",
            "cursor_ide_browser_type": "mcp_cursor-ide-browser_browser_type",
            "cursor_ide_browser_select_option": "mcp_cursor-ide-browser_browser_select_option",
            "cursor_ide_browser_wait_for": "mcp_cursor-ide-browser_browser_wait_for",
            "cursor_ide_browser_get_url": "mcp_cursor-ide-browser_browser_get_url",
            "cursor_ide_browser_take_screenshot": "mcp_cursor-ide-browser_browser_take_screenshot",
        }

        # Browserbase/Stagehand tools
        browserbase_mappings = {
            "browserbase_session_create": "mcp_Browserbase_browserbase_session_create",
            "browserbase_session_close": "mcp_Browserbase_browserbase_session_close",
            "browserbase_stagehand_navigate": "mcp_Browserbase_browserbase_stagehand_navigate",
            "browserbase_stagehand_act": "mcp_Browserbase_browserbase_stagehand_act",
            "browserbase_stagehand_observe": "mcp_Browserbase_browserbase_stagehand_observe",
            "browserbase_stagehand_extract": "mcp_Browserbase_browserbase_stagehand_extract",
            "browserbase_stagehand_get_url": "mcp_Browserbase_browserbase_stagehand_get_url",
            "browserbase_screenshot": "mcp_Browserbase_browserbase_screenshot",
        }

        all_mappings = {**cursor_mappings, **browserbase_mappings}

        # Map registered tools
        for tool_name, tool_key in all_mappings.items():
            if tool_key in self.tools:
                mapped_tools[tool_name] = self.tools[tool_key]

        return mapped_tools if mapped_tools else None


def create_mcp_tools_from_cursor_environment() -> Optional[Dict[str, Any]]:
    """
    Create MCP tools dictionary from Cursor IDE environment.

    This function attempts to create tool wrappers that can be used
    when MCP tools are available via the tool calling interface.

    Returns:
        Dictionary of MCP tool functions or None
    """
    # Note: In Cursor IDE, MCP tools are available via the tool calling interface
    # This function creates a structure that can be populated by the actual tool calls
    # The tools will be injected when available

    tools_wrapper = MCPToolsDirect()

    # Return the wrapper's tool dict (will be empty initially, but structure is ready)
    return tools_wrapper.get_tools_dict()
