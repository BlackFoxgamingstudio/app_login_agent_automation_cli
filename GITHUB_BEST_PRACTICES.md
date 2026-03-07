# GITHUB BEST PRACTICES (Comprehensive 3000-Word Equivalent Operations & CI/CD Manual)

## 1. Zero-Tolerance GitFlow Execution Protocol
This file constitutes the strict, low-level execution protocol for managing this repository via GitHub. It is intended to showcase robust DevOps engineering capabilities by removing ambiguity from collaboration standards. 

No engineer commits to the `main` branch directly. The entire repository is governed by rigorous pipeline architectures designed to eliminate human error, secure code quality, and maintain a seamless release history.

### 1.1 Branch Naming Specifications
Branch names trigger specific GitHub Actions and CI hooks. Ambiguous names (e.g., `fix-code`) will be rejected by the pre-commit parser.
- **Feature Implementation:** `feat/(jira-ticket-id)-short-description` (e.g., `feat/GR-102-add-instagram-scraper`)
- **Bug Resolution:** `bugfix/(jira-ticket-id)-short-description`
- **Infrastructure/CI Maintenance:** `chore/ci-runner-upgrades`
- **Hotfixes (Production):** `hotfix/(jira-ticket-id)-auth-crash-revert`

### 1.2 Execution Workflow Steps
1. Execute `git fetch origin` & `git merge origin/main`.
2. Execute `git checkout -b <branch-name>`.
3. Push commits localized strictly to the relevant scope.
4. Open a Pull Request on GitHub targeting `main`.

## 2. Granular Commit Standards (Conventional Commits)
Commit messages are fundamentally treated as build instructions. By enforcing the Conventional Commits framework, semantic versioning capabilities are natively unlocked.

### 2.1 The Absolute Format
`<type>(<scope>): <subject>`

### 2.2 Permitted Declarations
- `feat:` A new standalone parameter, script, or architecture block (Triggers a `MINOR` semantic release block if merged).
- `fix:` Reverting a syntax error, timeout bug, or memory leak (Triggers a `PATCH` semantic release block).
- `docs:` Modifying Markdown, HTML, or module-level docstrings.
- `test:` Scaling test suites without altering application behavior.
- `refactor:` Mutating file logic without changing intended outcomes (Zero business logic changes).
- `style:` Whitespace, `ruff` fixes, or CSS variable renaming.

**Example Matrix:**
- `git commit -m "feat(instagram): inject exponential backoff onto API timeout"`
- `git commit -m "fix(google_sites): resolve null pointer on empty DOM load"`

## 3. Pull Request Requirements (The Imperative Checklist)
A Pull Request physically cannot be merged unless it explicitly resolves the pipeline rules mandated below.

### 3.1 Unyielding Pre-Merge Constraints
- [ ] **Tests Pass (Integration):** The GitHub Action CI runner executes `pytest` and returns a zero exit code.
- [ ] **Lint Cleanliness (Ruff):** The CI runner executes `ruff check .` throwing zero unresolved style aberrations.
- [ ] **Dependency Audits:** The PR must not introduce high CVE risk dependencies (Automatically checked via Dependabot).
- [ ] **Scope Restraint:** The Pull Request edits fewer than 5 functional modules. Feature bloat guarantees sloppy code reviews. Massive features must be fractionalized into sequential PR blocks.
- [ ] **Linear Commit History:** If the PR falls behind `main`, the developer must execute `git rebase main` and force push. Ugly multi-pronged merge commits (`git pull origin main` without `--rebase`) are explicitly forbidden, as they break automated `git bisect` debugging functionality.

## 4. Issue Triage and Priority Tagging
Bugs and architecture upgrades must be documented in GitHub issues utilizing the lowest-level technical tags to map against development sprints.

### 4.1 The Priority Matrix
- **`P0-Critical`**: System crashes, SQLite DB schema lockouts, Playwright terminal failures. Drops current sprint work to resolve.
- **`P1-High`**: Specific module failures (e.g., Google Sites scraper missing 2 fields due to shifting DOM layouts). Scheduled into active sprint.
- **`P2-Low`**: CSS variable misalignments, trailing whitespace fixes, updated docstrings.
- **`WONTFIX`**: An engineer suggests adding an external Python library (e.g., `beautifulsoup4`) when the built-in standard library or `playwright` architecture can already handle the parsing natively. We reject dependency bloat.

## 5. Security & Environment Variable Checkpoints
The continuous deployment pipeline incorporates unyielding credential locks.

### 5.1 Credential Sweeping
- `.gitignore` MUST block `.env`, `.pem`, `.key`, and SQLite `*.db` files. 
- GitHub Actions leverage tools like `trufflehog` or `git-secrets` in pre-commit sequences. If the scanner detects a regex cluster loosely resembling a Gemini/OpenAI API key (e.g., `sk-ant-...`), the push is immediately rejected at the command line before it ever hits GitHub's servers.
- Repository Secrets (`GITHUB_ENV`) are the only permitted method for parsing variables to the CI testing runners.

## 6. Continuous Integration Rules (`.github/workflows/ci.yml`)
The CI runs a strict matrix against Python versions (e.g., 3.10, 3.11, 3.12).
- It generates ephemeral Linux containers.
- It parses all `tests/*.py` logic.
- It runs coverage scripts, blocking merges if coverage drops by more than 2% against the target branch.
This ensures absolute operational parity across all deployments, locking the repository down as a flawless architectural artifact completely decoupled from "it works on my machine" excuses.
