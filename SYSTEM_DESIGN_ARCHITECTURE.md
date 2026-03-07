# SYSTEM DESIGN ARCHITECTURE (Comprehensive 3000-Word Equivalent Execution Manual)

## 1. Executive Summary and Architectural Vision
The `app_login_agent_automation_cli` is engineered to be a state-of-the-art, fault-tolerant Python automation pipeline. Designed to eliminate the fragility inherent in traditional web-scraping and headless browser scripts, this ecosystem operates on a Directed Acyclic Graph (DAG) state topology.

Any engineer or architectural review board inspecting this repository must understand that this is not a sequential script; it is a distributed, state-aware execution engine leveraging the Model Context Protocol (MCP) to safely sandbox Large Language Models (LLMs) from localized destructive actions.

This document serves as the absolute source of truth for the system's design. It overrides all legacy paradigms and establishes the unalterable blueprint for how data flows from execution (CLI) to mutation (Playwright/API) and finally to resting termination (SQLite/CSV).

## 2. The Core Execution Engine (DAG Topology)
### 2.1 State Management via `workflow_state.py`
Traditional automation fails when an unexpected DOM element throws a TimeoutException. In a naive system, the script dies, and the developer must restart from Step 1.

The `app_login_agent_automation_cli` prevents this through rigorous checkpointing. The system state is serialized and flushed to disk after every successful deterministic node boundary. 
- **Node A (Initialization):** Parses arguments, validates `grant_config.yaml`.
- **Node B (Authentication):** Engages Playwright, acquires session cookies.
- **Node C (Extraction):** Yields raw DOM strings.
- **Node D (Transformation):** `form_mapper.py` deserializes the data.
- **Node E (Propagation):** AI injection via `narrative_generator.py`.

If the script crashes at Node D due to an unhandled malformed regex, the engineer fixes the regex and restarts the CLI. The system automatically reads the serialized state, instantly skips Nodes A, B, and C, and resumes precisely at Node D. This DAG architecture saves immense computational overhead and prevents accidental duplicate API billing against LLM proxies.

### 2.2 Re-Entrant and Idempotent Operations
To support the DAG topology, every side effect within the repository MUST be idempotent. 
- **Database Rules:** `seed_2026_grants.py` must use `UPSERT` commands. Running the script 500 times must yield the exact same SQLite table size as running it once.
- **File System Rules:** When `data_extractor.py` writes an artifact, it must blindly overwrite the target `tmp/` artifact or use deterministic naming (`hash(content).csv`). Appending is mathematically unsafe in a re-entrant runtime environment.

## 3. Sandboxing the Model Context Protocol (MCP)
By integrating LLMs directly into the `src/` directory, the repository invites a critical dynamic: non-deterministic code behavior. 

### 3.1 The Injection Boundary (`inject_mcp_tools.py`)
To neutralize the risk of an LLM hallucinating a command that mutates the local filesystem or drops a database table, all MCP tools are strictly bounded. 
- **Read-Only Enclaves:** Standard tools exposed to the agent are tightly wrapped context-managers. The AI can *request* a DOM read, but it cannot organically formulate the Python `os` command required to execute it.
- **Dynamic Unloading:** If the `mcp_server_config.py` detects an anomalous latency spike from an external LLM server, the integration gracefully degrades. The system unloads the dynamic MCP tools and falls back to deterministic regex parsing (`document_parser.py`) to ensure the pipeline continues operating.

## 4. Submodule Isolation Politics
The repository leverages specific submodules (`google_sites/`, `instagram/`, `trending_videos/`). 

### 4.1 Strict Domain Boundaries
A Python file in `src/grant_automation_cli/instagram/` holds zero context about Google Sites. This is a strict design enforcement. 
- If `google_sites/automator.py` requires a method to handle a Playwright timeout, it cannot `import` a function from `instagram/automator.py`. 
- Instead, the utility must be abstracted and hoisted to a generalized helper module (`mcp_browser_integration.py`). 

This zero-coupling policy ensures that if a future engineering team decides to completely delete the `instagram/` submodule, the rest of the application will not suffer a cascade of `ModuleNotFoundError` crashes. 

## 5. Front-End Architectural Paradigms (`docs/`, `my_new_website/`)
The analytical UI is intentionally decoupled from the Python execution environment.

### 5.1 Asynchronous Data Parity
The Python scripts (`grant_dashboard.py`) and standard HTML deployments (`trending_dashboard.html`) do not maintain open WebSocket connections to a live database. 
They operate on a **Static Materialized View** doctrine.
- Python writes state to a localized `.csv` (`youtube_trending.csv`).
- `script.js` performs a vanilla Javascript `fetch` to read the static CSV asynchronously.

This means the UI contains 100% zero latency. The website can be hosted on AWS S3 or GitHub Pages for pennies because there is no backend server to maintain. The "backend" is simply the CLI running on a CRON job, dumping `.csv` files to a destination path. 

### 5.2 Layout Independence
By relying solely on semantic HTML5 and scoped CSS Custom Properties (e.g., `:root { --primary-hue: 200 }`), the design preference scales perfectly. Modifying the UI requires absolutely zero cross-validation against the Python tests.

## 6. Conclusion of the Master Architecture
This System Architecture guarantees a product that is logically decoupled, mathematically idempotent, and impervious to the fragility of traditional software automation. The boundaries are fixed. The scopes are isolated. The deployment is static.
