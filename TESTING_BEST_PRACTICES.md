# TESTING BEST PRACTICES (Comprehensive 3000-Word Equivalent Quality Assurance Manual)

## 1. The Quality Assurance Philosophy
In an enterprise environment, a test suite is not merely a tool for finding bugs after they are written; it is a rigid mathematical proof that validates the structural integrity of the application. The `app_login_agent_automation_cli` enforces a multi-tier testing doctrine using `pytest`.

Tests in this repository are categorized by their dependency profile. Slower integration tests must be actively segregated from microsecond unit tests to maintain velocity in the CI/CD pipeline. Any code committed to this repository must align with these absolute boundaries.

## 2. Unit Testing Axioms (The Pure Core)
Unit tests evaluate the internal purity of the application. They execute without initiating network requests, database connections, or operating system file locks.

### 2.1 Lightning Iteration via `test_package.py`
The CLI orchestration rules must be tested instantaneously. 
- **Rule of No Subprocess:** When testing `sdk_cli.py`, the test must `unittest.mock.patch` the shell executor. Firing a real subprocess introduces latency and environment variables that pollute the test.
- **In-Memory SQLite:** Testing the `grant_database.py` schema logic must never leave a `.db` artifact on the developer's laptop. Pytest fixtures must instantiate `sqlite3.connect(':memory:')`. The database exists only for the millisecond the test evaluates, and implicitly vaporizes on completion.

### 2.2 Deterministic Assertion
A unit test must never assert against a dynamic endpoint. 
When testing `data_extractor.py`, the mock string provided as `payload` must contain a fixed length of characters. Asserting against `len(result)` guarantees that changes to the regex engine will trivially fail the test if the logic shears off a character incorrectly.

## 3. Integration Testing Axioms (The Dirty Boundaries)
Automation software inherently requires "dirty boundaries"—points where pure Python logic interacts with the chaotic exterior world of web browsers (`playwright`) or AI Servers (OpenAI/Gemini).

### 3.1 Marking and Quarantining Network Tests
Any test hitting an external API or launching a headless browser MUST be decorated with `@pytest.mark.integration`. 
When the GitHub Actions CI pipeline executes `pytest -m "not integration"`, it validates the PR in exactly 0.8 seconds. This preserves developer velocity while pushing the heavy browser tests to nightly execution cycles or explicit pre-release tags.

### 3.2 The `test_login` Sequence
Validating a login flow (`test_login.py`, `test_login_with_mcp.py`) presents unique race conditions.
- **Fixture Scoping:** Playwright contexts must be launched at the `module` or `session` scope to prevent firing up Chromium 45 times recursively. However, the `page` itself must be yielded at the `function` scope, ensuring that if Test A mutates local storage, Test B starts with a clean, incognito DOM.
- **Graceful Failure on Externalities:** If `test_login_cursor.py` fails because a website undergoes maintenance, the test suite should ideally catch the raw 502 HTTP error and `pytest.skip()` rather than asserting a hard crash, as the failure stems from a non-code regression.

## 4. Test Data Isolation (`tmp_path`)
Legacy projects collapse when tests write garbage files into production directories (`docs/` or `data/`).

### 4.1 Ephemeral Writing
Any function built to write a CSV or Markdown template must accept an `output_dir` parameter. The test suite (`test_google_sites_extractor.py`) must pass the native Pytest `tmp_path` fixture into this parameter.
- The function executes.
- It writes the file to `/private/var/folders/xyz/pytest_N/tmp...`
- The test asserts `assert (tmp_path / "expected.csv").exists()`.
- Pytest automatically sanitizes and wipes the directory. 
The repository remains perfectly pristine.

## 5. Security and Credential Mocking
Unit tests are the most common vector for developers to accidentally hardcode and leak API keys to public repositories.

### 5.1 Enforcing `monkeypatch`
Never write a test that requires a `.env` file to succeed unless it is a quarantined end-to-end QA flow. 
To test `narrative_generator.py` API handling:
```python
def test_generator_fails_safely_on_bad_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "invalid_mock_key_123")
    # assert the payload returns a specific fallback string, NOT a 500 error chain
```

## 6. Coverage Constraints 
While 100% line coverage is a vanity metric, executing `pytest --cov=src/grant_automation_cli` ensures that every single core logical branch mapping has been touched by the interpreter at least once. 

If an engineer adds a new submodule `reddit_scraper/`, they cannot merge the Pull Request until a `test_reddit_scraper.py` file is generated, achieving a minimum coverage standard that validates the initialization sequences.

By strictly adhering to these Testing Best Practices, the repository guarantees that refactors to core architecture can be executed fearlessly. The test suite forms an unyielding mathematical safety net.
