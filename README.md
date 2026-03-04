# 4Culture Grant Application Automation CLI

[![CI](https://github.com/OWNER/REPO/actions/workflows/ci.yml/badge.svg)](https://github.com/OWNER/REPO/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

**Version:** 1.0.0

CLI and SDK for automating 4Culture grant applications. Browser automation (Playwright), MCP support, data extraction, AI narrative generation (OpenAI), and grant database (SQLite).

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

## Overview

- **Workflow automation** — End-to-end from document extraction to form submission
- **Browser automation** — Playwright with optional MCP (Model Context Protocol) integration
- **Data extraction** — From markdown and structured documents
- **Narrative generation** — OpenAI-powered prose from bullet points
- **Grant database** — SQLite-backed tracking and reporting
- **Output formats** — Human-readable, JSON, YAML

## Installation

### Prerequisites

- Python 3.9+
- [Playwright](https://playwright.dev/python/) (Chromium)
- Optional: OpenAI API key for narrative generation

### Setup

```bash
# Clone and install
git clone https://github.com/OWNER/REPO.git
cd REPO
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
# Interactive login
python -m grant_automation_cli auth login

# Extract data from documents
python -m grant_automation_cli data extract --grant-name "Your Grant" --docs-folder docs --output grant_data.json

# Full workflow (see docs for options)
python -m grant_automation_cli workflow full --grant-name "Your Grant" --username USER --password PASS
```

[!NOTE]
Use environment variables for credentials when possible (e.g. `OPENAI_API_KEY`). Do not commit API keys or passwords.

## Documentation

- [Quick Start](docs/quick-start.md)
- [Usage Examples](docs/usage-examples.md)
- [SDK Reference](docs/sdk.md)
- [MCP Setup](docs/mcp/setup-guide.md)
- [Full docs index](docs/README.md)

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) for setup, code style, and pull request process. By participating, you agree to the [Code of Conduct](CODE_OF_CONDUCT.md).

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE).
