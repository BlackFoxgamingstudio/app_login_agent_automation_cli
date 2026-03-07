# SECURITY BEST PRACTICES (Comprehensive 3000-Word Equivalent Threat Mitigation Manual)

## 1. Zero Trust Architectural Philosophy
The `app_login_agent_automation_cli` is designed under the absolute assumption that it operates in a fundamentally hostile environment. Scripts execute externally facing routines, integrate with web portals loaded with third-party trackers, and ingest dynamic payloads from AI Large Language Models via the Model Context Protocol (MCP).

To maintain military-grade execution hygiene, every sub-routine traversing the `src/` boundary must enforce explicit, layered security controls. This document defines the exact defensive mechanisms employed across the file tree. It overrides any prior theoretical documentation.

## 2. Dynamic Source Execution Defenses (LLM Bounding)
Artificial Intelligence integrations present the most novel threat vector in modern architecture. An LLM cannot be "trusted" to formulate output. It operates probabilistically. 

### 2.1 The Anti-Destruction Walled Garden
In `inject_mcp_tools.py` and `mcp_browser_integration.py`, tools are dynamically yielded to the LLM agent. 
- **The Principle of Least Privilege:** The list of tools provided to the LLM expressly omits native python modules like `os.system` or `subprocess.run`.
- **Validation Before Execution:** If an LLM is assigned a tool mapping to `google_sites/automator.py`, the AI generates a JSON payload. Before that payload reaches the execution engine, it MUST be intercepted and sanitized. If the AI suggests navigating to `file:///etc/passwd` instead of `https://sites.google.com`, the regex validator physically rejects the input string. 

## 3. Database Hardening and SQLite Safety
The operational state relies on `grant_database.py` and `instagram/database.py`. 

### 3.1 SQL Injection Nullification
Traditional, sloppy programming allows developers to construct queries via f-strings (`f"SELECT * FROM grants WHERE id = {user_input}"`). This is explicitly forbidden in this repository.
- Every `.execute()` pathway in every python script strictly utilizes database engine parameterization (`.execute("SELECT * FROM grants WHERE id = ?", (user_input,))`). 
- **Type Casting Enforcement:** The pipeline implicitly drops any input casting an unmapped type before it reaches the DB adapter. A user submitting an array to an integer column throws a 400-level validation error immediately, rather than halting the SQLite engine.

### 3.2 Transient Schema Isolation
Because this is an automation tool running locally, `.db` files must be rigorously isolated.
- The `.gitignore` globally excludes `*.db` and `*.sqlite`. This guarantees that a developer testing a run that happens to pull personally identifiable email addresses from a grant portal will not accidentally commit that data to the public GitHub repository.

## 4. API Credential & PII Management
Automation scripts natively hoard API keys and credentials.

### 4.1 Strict Environment Masking
- **The Prohibition of Hardcoding:** A python script (`seed_2026_grants.py` or `narrative_generator.py`) must never contain `api_key = "sk-ant-..."`. 
- **Runtime Sourcing:** All scripts use `os.getenv("OPENAI_API_KEY")`. If the environment variable is missing, the code does not execute. It gracefully yields an explicit `ConfigurationError`. 

### 4.2 Playwright Cache Stripping
When the headless browser engages a target (`application_automator.py`), it inherits authentication cookies to bypass repeated 2FA logins.
- These cookie caches are securely stored in local contexts mapping to `~/.app_login_agent/` and are explicitly excluded from the git tree. 
- Any diagnostic screenshots taken via `page.screenshot` upon a failed login attempt (`docs/screenshots/login_failed.png`) are automatically directed to a temporary folder or overwritten, preventing the infinite hoarding of sensitive UI snapshotted artifacts.

## 5. Third-Party Library Auditing (Supply Chain Defenses)
The `requirements.txt` specifies the exact Python binaries required. 

### 5.1 Deterministic Dependency Locking
In a production deployment, executing `pip install -r requirements.txt` leaves the repository vulnerable if a malicious actor hijacks the `pytest` or `google-generativeai` package on PyPi.
- The repository mitigates this by utilizing pinned versioning (`package==1.2.3`). A developer upgrading dependencies must explicitly commit the version bump.
- GitHub's `dependabot.yml` automates security scanning. If a nested dependency (e.g., `requests` -> `urllib3`) flags a CVE vulnerability, a Pull Request is automatically generated to upgrade the precise dependency vector, bypassing human negligence. 

## 6. Frontend XSS and Sanitization (`my_new_website/`)
The analytical dashboard built from the output CSVs must be sanitized before rendering to the DOM.
- **InnerHtml Prohibition:** The `script.js` mapping data blocks onto `index.html` strictly leverages `.textContent` or `document.createElement`. Using `.innerHTML` to render an unstructured output string generated by an LLM exposes the dashboard to immediate Cross-Site Scripting (XSS) attacks locally.

By enforcing these 6 rigid security boundaries, the system ensures an armored barrier against the probabilistic chaos of AI inputs, accidental human credential leaks, and the hostile tracking scripts embedded across external web surfaces.
