"""4Culture Grant Scraper package."""

from .application_automator import ApplicationAutomator
from .automation_workflow import AutomationWorkflow
from .data_extractor import DataExtractor
from .document_parser import DocumentParser
from .form_mapper import FormMapper
from .grant_dashboard import GrantDashboard
from .grant_database import GrantDatabase
from .mcp_browser_integration import MCPBrowserIntegration
from .scraper import GrantScraper
from .workflow_state import WorkflowState

# Import SDK CLI if available
try:
    from .sdk_cli import GrantSDKCLI
except ImportError:
    GrantSDKCLI = None

# Import MCP tools utilities if available
try:
    from .inject_mcp_tools import (
        inject_available_mcp_tools,
        inject_tools_from_dict,
        inject_tools_from_mcp_server,
        setup_mcp_tools_auto,
    )
    from .mcp_server_config import (
        MCPServerConfig,
        configure_mcp_server_interactive,
        get_mcp_tools_from_server,
    )
except ImportError:
    MCPServerConfig = None
    configure_mcp_server_interactive = None
    get_mcp_tools_from_server = None
    inject_available_mcp_tools = None
    inject_tools_from_dict = None
    inject_tools_from_mcp_server = None
    setup_mcp_tools_auto = None

# Import narrative generator if available
try:
    from .narrative_generator import NarrativeGenerator

    __all__ = [
        "GrantScraper",
        "DocumentParser",
        "DataExtractor",
        "FormMapper",
        "ApplicationAutomator",
        "AutomationWorkflow",
        "NarrativeGenerator",
        "MCPBrowserIntegration",
        "GrantDatabase",
        "GrantDashboard",
        "WorkflowState",
    ]
    if GrantSDKCLI:
        __all__.append("GrantSDKCLI")
    if MCPServerConfig:
        __all__.extend(
            [
                "MCPServerConfig",
                "configure_mcp_server_interactive",
                "get_mcp_tools_from_server",
                "inject_available_mcp_tools",
                "inject_tools_from_dict",
                "inject_tools_from_mcp_server",
                "setup_mcp_tools_auto",
            ]
        )
except ImportError:
    __all__ = [
        "GrantScraper",
        "DocumentParser",
        "DataExtractor",
        "FormMapper",
        "ApplicationAutomator",
        "AutomationWorkflow",
        "MCPBrowserIntegration",
        "GrantDatabase",
        "GrantDashboard",
        "WorkflowState",
    ]
    if GrantSDKCLI:
        __all__.append("GrantSDKCLI")
    if MCPServerConfig:
        __all__.extend(
            [
                "MCPServerConfig",
                "configure_mcp_server_interactive",
                "get_mcp_tools_from_server",
                "inject_available_mcp_tools",
                "inject_tools_from_dict",
                "inject_tools_from_mcp_server",
                "setup_mcp_tools_auto",
            ]
        )
