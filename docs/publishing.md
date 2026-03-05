# Publishing to PyPI

This project can be published to the Python Package Index (PyPI) so users can install with `pip install grant-automation-cli`.

## Automated publish (GitHub Actions)

A workflow runs on **release publish**: when you create a new release (e.g. tag `v1.0.0`) and publish it, the workflow builds the package and uploads to PyPI.

### Setup

1. **Create a PyPI account** at [pypi.org](https://pypi.org/account/register/).
2. **Create an API token** (Account → API tokens). Scope it to this project or entire account.
3. **Add the token to this repo**: Settings → Secrets and variables → Actions → New repository secret. Name: `PYPI_API_TOKEN`, value: your token (starts with `pypi-`).

### Releasing

1. Bump version in `pyproject.toml` and update `CHANGELOG.md`.
2. Commit and push.
3. Create a new release on GitHub: Releases → Draft a new release. Choose tag (e.g. `v1.0.0`), title, and paste the CHANGELOG section. Publish.
4. The **Publish to PyPI** workflow will run and upload to PyPI.

### TestPyPI first

To test the upload without publishing to the real PyPI:

- In the workflow, change the upload step to: `twine upload --repository testpypi dist/*`
- Add secret `TESTPYPI_API_TOKEN` and use it for that upload.
- Install from TestPyPI: `pip install --index-url https://test.pypi.org/simple/ grant-automation-cli`

## Manual publish

```bash
pip install build twine
python -m build
twine upload dist/*
```

You will be prompted for your PyPI username and password (or use `__token__` and your API token).
