# PROJECT DESIGN MASTER PLAN (Lowest-Level Implementation Details)

This master plan document eliminates any high-level abstraction and strictly defines the lowest-level technical guidelines, folder rules, and architectural standards for the `app_login_agent_automation_cli` repository.

## 1. Lowest-Level Directory Constraints

Every directory in this project serves an immutable purpose. No cross-pollution of responsibilities is permitted.

### `src/` (Source Code)
- **Constraint**: Contains *only* execution logic. No static assets.
- **Rule**: Every Python file must contain a module-level docstring defining its explicit purpose and boundaries.
- **Rule**: Imports must be absolute starting from the `src.` root, or strictly relative within submodules, avoiding circular dependencies.

### `tests/` (Unit & Integration Tests)
- **Constraint**: Must mirror the `src/` architecture perfectly (`src/module.py` -> `tests/test_module.py`).
- **Rule**: No network calls allowed in unit tests (must be mocked). Network-bound tests must be annotated with `@pytest.mark.integration`.

### `docs/` & `my_new_website/` (Frontend & Documentation)
- **Constraint**: HTML/JS/CSS files must not contain inline business logic or database queries.
- **Rule**: JavaScript files must operate under `'use strict';`. Stylesheets must use CSS variables attached to `:root` to avoid hardcoded duplication.

### `data/` & `templates/` (Static Assets)
- **Constraint**: Templates must be immutable schemas. Data files (CSVs, JSONs) are strictly endpoints or caches.
- **Rule**: `.gitignore` MUST block all dynamic states, credentials, or transient DB files in these directories natively.

### `agents/` (AI Workflows)
- **Constraint**: AI logic must be isolated from the core executable application code.
- **Rule**: All AI prompts and payloads must be statically defined, version-controlled strings. Dynamic bindings must pass through strict schema validators (Pydantic/Dataclasses).

---

## 2. Lowest-Level Architectural Paradigms

### Separation of Concerns (CLI vs. Core)
- The Command Line Interfaces (`cli.py`, `dashboard_cli.py`) are essentially "dumb routers". They must consume `argparse` definitions and immediately delegate the payload to an imported class method. **Zero logical branching** (aside from argument formatting) should exist in CLI scripts.

### Idempotency & State Management
- All `UPSERT` database commands (`seed_2026_grants.py`), folder creations, or API extractions must be idempotent.
- Running the automation CLI twice in a row against the same dataset must result in the exact same application state without duplicate key errors or crashes.

### Defensive Error Handling
- Broad `except Exception:` chains are forbidden.
- Files parsing external DOMs (like `instagram/automator.py` or `scraper.py`) must catch specific driver timeout exceptions and provide graceful fallback degradation or localized retries, preventing an entire pipeline collapse.

### Hardened Dependencies
- `playwright` instances must be strictly context-managed (using `with` blocks) to guarantee process termination across failures.

---

## 3. Strict Development Lifecycle

To maintain this standard of codebase quality, the final, lowest-level requirement for any future implementation is:
1. Identify the target directory constraint.
2. Ensure the specific file aligns with the relevant `FOLDER_BEST_PRACTICES.md` checklist.
3. Validate through `pytest tests/`.
4. Enforce PEP-8 style execution via `ruff check . --fix`.
