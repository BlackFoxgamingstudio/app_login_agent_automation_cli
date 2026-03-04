"""Basic package and CLI tests (no browser/MCP required)."""

from grant_automation_cli import (
    DataExtractor,
    DocumentParser,
    FormMapper,
    GrantDashboard,
    GrantDatabase,
    GrantScraper,
    WorkflowState,
)
from grant_automation_cli.sdk_cli import GrantSDKCLI


def test_imports():
    """Core modules can be imported."""
    assert GrantScraper is not None
    assert DocumentParser is not None
    assert DataExtractor is not None
    assert FormMapper is not None
    assert GrantDatabase is not None
    assert GrantDashboard is not None
    assert WorkflowState is not None


def test_sdk_cli_instantiation():
    """GrantSDKCLI can be instantiated and has expected interface."""
    cli = GrantSDKCLI()
    assert cli is not None
    assert hasattr(cli, "cmd_auth_login")
    assert hasattr(cli, "_get_mcp_browser_tools")
    assert hasattr(cli, "output_format")


def test_grant_database_instantiation():
    """GrantDatabase can be instantiated with in-memory DB."""
    db = GrantDatabase(db_path=":memory:")
    assert db is not None
