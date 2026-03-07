# Source Directory (`src/`) - Lowest-Level Best Practices & Checklist

This document contains the lowest-level, file-by-file checklist for every component within the `src/` directory. All features are mapped to their specific execution files to ensure developer guidelines are fully implemented.

## Directory Overview
The `src/` directory houses the core business logic, composed of the primary module `grant_automation_cli` and its advanced submodules for specific integrations (Google Sites, Instagram, Trending Videos).

---

## File-Level Checklists: Core Business Logic (`src/grant_automation_cli/`)

### 1. `application_automator.py`
- **Feature**: Automates browser interactions for application forms using Playwright.
- **Detailed Checklist**:
  - [x] Include module docstring emphasizing robust element selection and dynamic waits.
  - [x] Ensure `@pytest.mark.integration` compatibility for functions simulating clicks/typing.
  - [x] Implement robust logging for page timeouts.

### 2. `automation_workflow.py`
- **Feature**: Orchestrates the multi-step automation workflow.
- **Detailed Checklist**:
  - [x] Include developer guideline for DAG (Directed Acyclic Graph) workflow management.
  - [x] Ensure state recovery mechanisms in case of pipeline failure.
  - [x] Validate strict error boundaries between steps.

### 3. `cli.py` & `sdk_cli.py` & `dashboard_cli.py` & `mcp_setup_cli.py`
- **Feature**: Handles command-line argument parsing and delegation.
- **Detailed Checklist**:
  - [x] Add guidelines on keeping CLI handlers "thin" by delegating business logic.
  - [x] Ensure comprehensive help text (`--help` arguments exist for all subcommands).
  - [x] Validate exit status codes (0 for success, non-zero for errors).

### 4. `data_extractor.py` & `document_parser.py`
- **Feature**: Parses unstructured application data (e.g., PDFs, YAML).
- **Detailed Checklist**:
  - [x] Include guidelines on handling malformed data gracefully without hard crashing.
  - [x] Standardize file path operations using `pathlib.Path` or `os.path`.
  - [x] Enforce fallback data types for optional fields.

### 5. `form_mapper.py`
- **Feature**: Maps parsed data schemas to specific form UI actions.
- **Detailed Checklist**:
  - [x] Implement explicit mappings for dropdowns, radios, and text inputs.
  - [x] Document strategies for UI discrepancies (e.g., hidden inputs).

### 6. `grant_database.py` & `seed_2026_grants.py`
- **Feature**: Manages the SQLite internal database and data seeding.
- **Detailed Checklist**:
  - [x] Include security guidelines preventing SQL Injection via parameterized queries (`?`).
  - [x] Ensure data seeding is idempotent (use `UPSERT` / `ON CONFLICT DO UPDATE`).
  - [x] Handle connection pooling and graceful closing.

### 7. `grant_dashboard.py` (Streamlit)
- **Feature**: Generates the local analytical dashboard.
- **Detailed Checklist**:
  - [x] Document caching strategies for heavy database queries (e.g., `@st.cache_data`).
  - [x] Separate layout logic from data retrieval logic.

### 8. `scraper.py`
- **Feature**: Web scraping logic for the 4Culture application portal.
- **Detailed Checklist**:
  - [x] Enforce guidelines against overly generic CSS selectors to prevent fragility.
  - [x] Include retry logic for failed HTTP requests or timeout elements.

### 9. `workflow_state.py`
- **Feature**: Manages checkpointing and resuming functionality.
- **Detailed Checklist**:
  - [x] Document atomic state changes to prevent corrupted save files.
  - [x] Ensure thread-safe or process-safe file writing where applicable.

### 10. `narrative_generator.py`
- **Feature**: Interfaces with the Gemini/OpenAI API to generate text.
- **Detailed Checklist**:
  - [x] Document prompt engineering guidelines and bounding AI outputs.
  - [x] Implement strict fallback mechanisms for API timeouts/quota limits.

### 11. MCP Integration Files (`mcp_browser_integration.py`, `mcp_server_config.py`, `mcp_server_runner.py`, `mcp_tools_direct.py`, `mcp_tools_helper.py`, `inject_mcp_tools.py`)
- **Feature**: Integrates the Model Context Protocol (MCP) toolsets for LLM interaction logic.
- **Detailed Checklist**:
  - [x] Document dynamic loading constraints and isolated tool injection.
  - [x] Ensure environment variables control MCP verbosity and execution paths.
  - [x] Provide graceful degradation if the MCP server is unreachable.

---

## File-Level Checklists: Submodules

### `google_sites/` Submodule
- **`automator.py`**:
  - [x] Document safe browser navigation and timeout defaults.
- **`cli.py`**:
  - [x] Outline argument validation logic.
- **`database.py`**:
  - [x] Replicate SQL safety measures implemented in `grant_database.py`.
- **`extractor.py`**:
  - [x] Enforce Markdown extraction resilience (using regex or tokenizers).

### `instagram/` Submodule
- **`ai_generator.py`**:
  - [x] Verify API quota management and fallback configurations.
- **`automator.py`**:
  - [x] Add selector safety checks, as social media DOMs frequently change.
- **`cli.py`**:
  - [x] Keep command logic thin.
- **`database.py`**:
  - [x] Enforce date/time standardization (ISO formats) for social media tracking.

### `trending_videos/` Submodule
- **`generator.py`**:
  - [x] Validate robust JSON parsing from LLM outputs (stripping markdown backticks).
  - [x] Enforce static fallback data (mocks) for complete API failure resilience.
