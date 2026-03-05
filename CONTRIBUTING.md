# Contributing to 4Culture Grant Application Automation CLI

Thank you for your interest in contributing. This document explains how to set up your environment, our expectations, and how to submit changes.

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold it.

## How to Contribute

We welcome:

- **Bug reports** — open an issue with steps to reproduce and environment details
- **Feature requests** — open an issue describing the use case and proposed behavior
- **Documentation** — typo fixes, clearer explanations, or new guides
- **Code** — fix bugs or implement features via pull requests

## Development Setup

### Prerequisites

- Python 3.9 or higher
- [Playwright](https://playwright.dev/python/) (Chromium for browser automation)
- Optional: OpenAI API key for narrative generation features

### Steps

1. **Fork and clone the repository.**

2. **Create a virtual environment (recommended):**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # On Windows: .venv\Scripts\activate
   ```

3. **Install the project in editable mode with dev dependencies:**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Install Playwright browsers (if not already installed):**
   ```bash
   playwright install chromium
   ```

5. **Install pre-commit hooks (recommended):**
   ```bash
   pre-commit install
   pre-commit run --all-files   # Optional: run once on existing files
   ```

### Running Tests

```bash
pytest
```

With coverage:

```bash
pytest --cov=src/grant_automation_cli --cov-report=term-missing
```

### Code Style and Linting

- We use [Ruff](https://docs.astral.sh/ruff/) for linting and formatting.
- Config is in `pyproject.toml` under `[tool.ruff]`.
- Run manually:
  ```bash
  ruff check .
  ruff format .
  ```
- Pre-commit runs these automatically before each commit.

## Pull Request Process

1. **Open an issue** first for non-trivial changes so we can align on approach (optional but welcome for large changes).

2. **Create a branch** from the default branch (e.g. `main`):
   ```bash
   git checkout -b fix/short-description
   ```

3. **Make your changes.** Keep commits focused. We encourage [Conventional Commits](https://www.conventionalcommits.org/) (e.g. `feat: add X`, `fix: correct Y`).

4. **Run tests and lint:**
   ```bash
   pytest
   ruff check . && ruff format --check .
   ```

5. **Push and open a pull request.** Fill in the PR template:
   - Link to any related issue
   - Describe what changed and why
   - Confirm tests pass and documentation is updated if needed

6. **Address review feedback.** Maintainers may request changes; we’ll work with you to get the PR merged.

## Ground Rules

- Be respectful and constructive in issues and PRs.
- Keep the scope of a PR manageable; split large work into smaller PRs when possible.
- Document user-facing behavior in the README or `docs/` as relevant.
- Do not commit secrets (API keys, passwords). Use environment variables and document them in README or CONTRIBUTING.

## Questions?

Open a [GitHub Discussion](https://github.com/BlackFoxgamingstudio/app_login_agent_automation_cli/discussions) or an issue with the "question" label.

Thank you for contributing!
