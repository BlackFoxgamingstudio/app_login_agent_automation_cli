# 4Culture Grant Application Automation CLI

[![CI](https://github.com/BlackFoxgamingstudio/app_login_agent_automation_cli/actions/workflows/ci.yml/badge.svg)](https://github.com/BlackFoxgamingstudio/app_login_agent_automation_cli/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/BlackFoxgamingstudio/app_login_agent_automation_cli/graph/badge.svg)](https://codecov.io/gh/BlackFoxgamingstudio/app_login_agent_automation_cli)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

**Version:** 1.0.0

CLI and SDK for automating 4Culture grant applications and fully automated Google Sites generation. Browser automation (Playwright), MCP support, data extraction, AI narrative generation (OpenAI), and SQLite databases.

## 🚀 How to Run the Solution: 4 Technical Paths
As the Head Technical Documentation Product Manager, I've outlined the four primary execution paths for our automation suite. Please select the option that best suits your current deployment needs.

### Option 1: CLI Login Authorization (Standalone Auth)
**Purpose:** Validates credentials and initiates an authenticated session without running the full pipeline. Ideal for initial setup and credential verification.
**Steps:**
1. Ensure your virtual environment is active and dependencies are installed.
2. Open your terminal in the root directory (`/app_login_agent_automation_cli`).
3. Execute the auth command:
   ```bash
   python3 -m src.grant_automation_cli auth login
   ```
4. Follow the prompt to input your 4Culture `username` and `password` if not already set in environment variables.
5. The system will verify the headless browser connection and confirm successful authentication.

### Option 2: Full End-to-End Workflow Execution
**Purpose:** Runs the complete end-to-end grant automation lifecycle, from data extraction to form submission.
**Steps:**
1. Ensure your grant documentation (`.md` or `.pdf`) is placed in the required `docs/` input directory.
2. In your terminal, execute the full workflow command:
   ```bash
   python3 -m src.grant_automation_cli workflow full --grant-name "Your Grant" --username "USER" --password "PASS"
   ```
3. **Observation:** The CLI will systematically step through:
   - *Data Extraction:* Parsing target documentation.
   - *Narrative Generation:* Formulating AI-driven responses.
   - *Browser Automation:* Headless/headed navigation to 4Culture.
   - *Form Submission:* Mapping and entering the extracted data.
4. Review the generated YAML/JSON summaries in the root or database directories for final validation.

### Option 3: Browser Subagent Login (Interactive/Debug Mode)
**Purpose:** Utilizes an AI-driven or specialized subagent script to step through the browser login sequence visually or via an independent process. Ideal for UI debugging or bypassing CAPTCHAs/dynamic elements.
**Steps:**
1. Navigate to the `agents/grant_scraper/` directory.
2. Review the subagent scripts and configurations.
3. Depending on the subagent's entry point, run the localized Playwright script:
   ```bash
   # Example command (adjust based on subagent target)
   python3 agents/grant_scraper/main.py
   ```
4. If testing visually, ensure Playwright is set to headed mode (`headless=False`) within the agent's initialization parameters to monitor the runtime securely.

### Option 4: Google Sites Automation (End-to-End)
**Purpose:** Fully automates the creation of Google Sites from Markdown templates. It bypasses auth detection and handles the Canvas UI natively.
**Steps:**
1. **Initialize Workspace:** Run the init command to create your workspace directory and generate the `.md` templates from the database.
   ```bash
   python3 -m src.grant_automation_cli gsite init --dir my_new_website
   ```
2. **Fill Templates:** Open the generated `business_profile.md`, `design_preferences.md`, and `page_content.md` files in your target directory and fill out the details.
3. **Authenticate:** Run the Google auth command *once* to sign in manually. The session is saved to avoid bot detection loops.
   ```bash
   python3 -m src.grant_automation_cli gsite auth
   ```
4. **Build the Site:** Run the build command to have Playwright open Google Sites, set the name, apply your theme, and dynamically generate pages and text blocks.
   ```bash
   python3 -m src.grant_automation_cli gsite build --dir my_new_website
   ```

---

## Table of Contents

- [How to Run the Solution: 4 Technical Paths](#-how-to-run-the-solution-4-technical-paths)
- [Overview](#overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

## Overview

<!-- Add a screenshot or GIF here if desired, e.g. ![CLI demo](docs/screenshots/cli-demo.png) -->

- **Workflow automation** — End-to-end from document extraction to form submission
- **Google Sites generation** — Automated site creation, theme selection, and page building
- **Browser automation** — Playwright with optional MCP (Model Context Protocol) integration
- **Data extraction** — From markdown and structured documents
- **Narrative generation** — OpenAI-powered prose from bullet points
- **Embedded Databases** — SQLite-backed tracking, reporting, and template management
- **Output formats** — Human-readable, JSON, YAML

## Installation

### Prerequisites

- Python 3.9+
- [Playwright](https://playwright.dev/python/) (Chromium)
- Optional: OpenAI API key for narrative generation

### Setup

```bash
# Clone and install
git clone https://github.com/BlackFoxgamingstudio/app_login_agent_automation_cli.git
cd app_login_agent_automation_cli
pip install -e .

# Install Playwright browser
playwright install chromium

# Verify
python -m grant_automation_cli --help
```

Or install dependencies only (no package):

```bash
pip install -r requirements.txt
playwright install chromium
```

## Quick Start

```bash
# Interactive login (Grants)
python -m src.grant_automation_cli auth login

# Extract data from documents
python -m src.grant_automation_cli data extract --grant-name "Your Grant" --docs-folder docs --output grant_data.json

# Full workflow (Grants)
python -m src.grant_automation_cli workflow full --grant-name "Your Grant" --username USER --password PASS

# Initialize Google Sites templates
python -m src.grant_automation_cli gsite init --dir target_folder

# Authenticate Google Sites (Run once)
python -m src.grant_automation_cli gsite auth

# Build Google Site automatically
python -m src.grant_automation_cli gsite build --dir target_folder
```

[!NOTE]
Use environment variables for credentials when possible (e.g. `OPENAI_API_KEY`, `4CULTURE_USERNAME`, `4CULTURE_PASSWORD`). Do not commit API keys or passwords.

[!WARNING]
Playwright requires `playwright install chromium` (or another browser) after install. On CI or headless servers, use a headless-compatible environment.

## Documentation

- [Quick Start](docs/quick-start.md)
- [Usage Examples](docs/usage-examples.md)
- [SDK Reference](docs/sdk.md)
- [MCP Setup](docs/mcp/setup-guide.md)
- [SDK Landing Page](docs/index.html) | [API Reference](docs/api.md) (or build with `mkdocs build`) | [Full docs index](docs/README.md)

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) for setup, code style, and pull request process. By participating, you agree to the [Code of Conduct](CODE_OF_CONDUCT.md).

## Contributors

Thanks to everyone who contributes to this project.

<!-- ALL-CONTRIBUTORS-LIST:START -->
<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [All Contributors](https://allcontributors.org) specification. To add yourself, comment on an issue or PR: `@all-contributors please add @your-username for <contribution-type>`.

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE).
