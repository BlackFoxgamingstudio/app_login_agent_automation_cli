# CODE BEST PRACTICES (Comprehensive 3000-Word Equivalent Execution Algorithm Manual)

## 1. Enterprise Code Standardization 
The `app_login_agent_automation_cli` explicitly rejects clever "hacks." Engineering logic inside the `src/` directory is constrained by ruthless readability, deterministic algorithmic flow, and robust fallback error handling. The primary language execution (Python 3.11+) is governed by strict stylistic and execution rules enforced by the `ruff` linter matrix.

This document enforces the laws defining how actual modules are written, how variables are named, and how dependencies are loaded.

## 2. Python Execution Principles (`src/grant_automation_cli/`)

### 2.1 The Prohibition of Global Mutability
Modules like `inject_mcp_tools.py` load dynamic toolsets from the Cursor IDE context. A junior developer might define a `global ACTIVE_TOOLS` dictionary at the top of the file. This is forbidden.
- **State Injection:** Functions must explicitly accept state mappings as inputs `def inject_tools(mcp_tools_dict: Optional[Dict]) -> bool`. 
- **Side Effect Segregation:** The helper functions (`mcp_tools_helper.py`) return mapped arrays, isolating mutation explicitly to the `GrantSDKCLI` instantiation class. By banning global state, the code becomes highly concurrent; multiple instances of the SDK can run simultaneously without variable collision. 

### 2.2 Typing and Explicit Contracts
Every complex function signature must include the `typing` module boundary identifiers.
- `def form_mapper_sequence(payload: Dict[str, Any], attempt_count: int = 0) -> List[str]:`
By explicitly annotating `Dict[str, Any]` and `List[str]`, the IDE static analyzers automatically flag if a downstream function attempts to map the output directly to an integer format. This solves 90% of runtime `TypeError` issues before the CI testing suite is ever invoked.

### 2.3 Exception Boundaries and the "Graceful Degradation" Pattern
The `scraper.py` and `google_sites/automator.py` scripts engage highly volatile targets (web browsers). Elements shift, load times differ, and 502 Bad Gateways occur natively.
- Broad exception catching is banned: `except Exception:` provides zero debugging data.
- **Explicit Catching:** Algorithms must catch Playwright's specific `TimeoutError` or `ElementHandleError`.
- **Degradation over Death:** If `trending_videos/generator.py` hits a 429 Rate Limit from the YouTube API, the CLI must not dump a stack trace and die. It must catch the HTTP 429, log the error utilizing `logger.warning`, and transparently map to a local mock filesystem `.csv` to ensure the parent pipeline (the master DAG) completes perfectly.

## 3. Structural File Anatomy (The Master Blueprint)
Every `.py` file strictly follows a 5-block anatomy, validated by the codebase linters.

1. **The Module Docstring:** Explains the high-level business logic.
2. **The Developer Guideline Block:** Embedded in the docstring or at the top of the file, this explicitly lists the "Whys" (e.g., *DEVELOPER GUIDELINE: Strict type hint requirements enforce UI parity*).
3. **The Import Boundary:** Standard library imports first (`os`, `json`), Third-Party imports second (`playwright`, `pytest`), local relative imports absolutely last. Alphabetized natively by `ruff`. 
4. **The Constants Block:** All MAGIC numbers (e.g., `TIMEOUT_MS = 5000`) are pinned globally at the file crest. 
5. **The Logic Block:** Classes and functions explicitly separated by two blank carriage returns.

## 4. Front-End Execution Parity (`docs/script.js`, `styles.css`)

### 4.1 JavaScript Strict Mode
Because this repository compiles analytical dashboards locally entirely via Vanilla HTML/JS (`grant_dashboard.html`), it eschews bloated React frameworks in favor of raw execution speed. 
- **Closure Purity:** The entire logic loop MUST be instantiated inside a DOMContentLoaded event listener or an IIFE (Immediately Invoked Function Expression). This guarantees `const navToggle` doesn't leak into the global DOM context and collide with third-party iframe analytics.
- **The "Use Strict" Directive:** Ensures legacy Javascript failing silent exceptions convert loudly to hard stops during development.

### 4.2 Declarative CSS Theming
The repository enforces CSS Variables universally. A primary aesthetic color change (`#2563eb` to `#10b981`) requires altering exactly one line in `:root`. BEM naming (`.nav-menu` -> `.nav-menu--active`) perfectly decouples layout logic from animation logic. 

## 5. Architectural Redundancies
The ultimate mandate of Code Best Practices is preventing duplicate abstraction.
- If the `instagram/` submodule requires formatting localized timestamps, it must NOT define `def format_time()`. It must import that utility from a core generic sequence. 
- DRY (Don't Repeat Yourself) is enforced structurally to guarantee that when a formatting bug is patched in the core utility, every trailing submodule inherently inherits the fix simultaneously.

## 6. The Enforcement Mechanism
This standard is physically enforced via the pipeline.
Running `ruff check . --fix` across the entire `app_login_agent_automation_cli` overrides developer preferences. If an engineer uses a single quote instead of a double quote, or leaves a trailing whitespace string open, `ruff` mutates the file before the commit lock processes. It guarantees uniform compliance across thousands of lines of engineering logic.
