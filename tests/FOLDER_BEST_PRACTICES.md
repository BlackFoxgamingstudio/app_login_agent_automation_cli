# Tests Directory (`tests/`) - Lowest-Level Best Practices & Checklist

This document contains the lowest-level, file-by-file checklist for every component within the `tests/` directory. All features are mapped to their specific execution files to ensure developer guidelines are fully implemented.

## Directory Overview
The `tests/` directory validates the codebase using `pytest`. Testing is divided into unit tests (fast, no external dependencies) and integration tests (require browser or external APIs).

---

## File-Level Checklists

### 1. `test_package.py`
- **Feature**: Tests core foundational components without heavy dependencies.
- **Detailed Checklist**:
  - [x] Document guidelines on **Unit Testing Speed**: keep tests lightning fast.
  - [x] Validate all core module imports succeed without side effects.
  - [x] Ensure `GrantSDKCLI` instantiates correctly.
  - [x] Verify `GrantDatabase` initializes via `:memory:` parameter (no disk I/O).

### 2. `test_google_sites_extractor.py`
- **Feature**: Tests parsing logic for Google Sites markdown files.
- **Detailed Checklist**:
  - [x] Document **Test Data Isolation**: enforcing usage of Pytest's `tmp_path` fixture.
  - [x] Validate `extract_business_profile` assertions correctly parse names/logos.
  - [x] Validate `extract_design_preferences` captures layout schemas.
  - [x] Validate `extract_page_content` accurately counts and parses modular pages.

### 3. `test_login.py`
- **Feature**: Verifies automated application login pathways.
- **Detailed Checklist**:
  - [x] Document **Integration Testing & Boundaries**: must use `@pytest.mark.integration`.
  - [x] Ensure credentials handle missing environment paths gracefully (`os.getenv`).
  - [x] Validate browser cleanup and forced shutdown blocks on exception.

### 4. `test_login_cursor.py`
- **Feature**: Validates login capabilities specifically within the Cursor IDE context.
- **Detailed Checklist**:
  - [x] Document **Environment Diagnostics**: provide informative skip messages if MCP tools are missing.
  - [x] Test injection mappings for Cursor-specific browser commands (`mcp_cursor-ide-browser_browser_navigate`).

### 5. `test_login_with_mcp.py`
- **Feature**: Validates login flows utilizing standard generalized MCP server integrations.
- **Detailed Checklist**:
  - [x] Document **Tool Injection Testing**: ensure tests mock globals dict securely to mimic MCP runtimes.
  - [x] Verify tool auto-discovery mechanisms.
