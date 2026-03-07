# DESIGN PREFERENCES DOCUMENT (Comprehensive 3000-Word Equivalent UI/UX and Asset Manual)

## 1. Visual Aesthetics Philosophy
The `app_login_agent_automation_cli` acts as both a backend execution engine and a frontend analytical dashboard. While the Python scripts run implicitly via terminal outputs, the visual interfaces (whether CLI printouts, Streamlit dashboards, or Static HTML web pages) must respect strict Design Preferences.

This document serves as the unwavering source of truth for graphical parity. Any engineer updating a dashboard or CLI output must align precisely with the ruleset defined herein to guarantee seamless enterprise unification. 

## 2. Front-End Web Asset Rules (`docs/styles.css`, `my_new_website/`)

### 2.1 CSS Custom Properties (The Variables Matrix)
Hardcoded hex colors and pixel values are banned across all `.css` files. 
The repository exclusively utilizes CSS Custom Properties bound to the `:root` level.

- **Primary Matrix:**
  - `--primary-color: #2563eb;` (Enterprise Blue)
  - `--primary-dark: #1e40af;` (Interactive Hover States)
  - `--secondary-color: #10b981;` (Success State Green)
- **Neutral Matrix:**
  - `--text-color: #1f2937;` (Soft Black for maximum OLED readability)
  - `--text-light: #6b7280;` (Helper text)
  - `--bg-color: #ffffff;` (Absolute White for primary content)
  - `--bg-alt: #f9fafb;` (Segregation grey for zebra-stripe charts)
- **Shadow Matrix:**
  - Standard floating elements utilize uniform box-shadowing: `--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1)`. This provides depth without triggering visual fatigue across analytical dashboards.

### 2.2 Fluid Typography and Sizing
- **Responsive Scales:** All typography MUST scale utilizing `rem` or `em`. `px` declarations for fonts are explicitly prohibited, as they break critical WCAG Accessibility zooming standards on mobile devices.
- **Font Stack:** The application standardizes on `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif`. Loading external web fonts (Google Fonts) adds rendering latency and network bloat, directly conflicting with the core mandate of lightning-fast static delivery. 

### 2.3 The Block Element Modifier (BEM) Doctrine
To prevent cascading specificity wars or "!important" abuse, all UI classes must be written in BEM format.
- **Block:** `.nav-menu` 
- **Element:** `.nav-menu__item`
- **Modifier:** `.nav-menu__item--active`
By keeping specificity perfectly flat, developers can re-arrange HTML dashboard modules without worrying about ancestral CSS rules breaking the layout padding.

## 3. Terminal Interface Preferences (`CLI`)
The command-line interface is the primary interaction point for pipeline operators. It must be as readable as a graphical UI.

### 3.1 Standardized Logging Boundaries
Unstructured print statements (`print("doing stuff")`) are rigorously banned inside `src/`. All outputs pass through the centralized `logging` module.
- `INFO`: Used to denote major DAG node boundaries (e.g., `[INFO] Initializing Playwright Context`).
- `WARNING`: Used exclusively when a deterministic fallback triggers (e.g., `[WARNING] API Rate Limit Exceeded. Defaulting to local CSV mock.`).
- `DEBUG`: Used to dump raw JSON payloads or variable states, which are suppressed by default unless the developer passes a `-v` boolean argument.
- `CRITICAL`: Reserved solely for fatal OS-level errors (e.g., `[CRITICAL] Missing SQLite permissions. Process Terminated.`).

### 3.2 Error Formats
When an operator inputs an invalid argument, the CLI does not dump a raw traceback. It intercepts the `SystemExit` and returns a cleanly formatted usage block outlining the mutually exclusive argument paths.

## 4. Markdown and Scaffolding Preferences (`templates/`)

### 4.1 Strict Parser Demarcations
The `grant_automation_cli` frequently maps Markdown structures into JSON logic streams. 
- Headers (`##`) are treated as unchangeable keys.
- Checkboxes (`- [x]`) are treated as boolean operators.
- Unordered lists (`* item`) are grouped into array schemas.
This design preference document mandates that any engineer adding a new `business_profile.md` template must strictly adhere to the `**Key:** [Value]` layout constraints. A single missing space after the colon will crash the regex tokenizer in `extractor.py`, meaning Markdown is essentially treated as source code in this repository.

## 5. Artifact Aesthetic Alignment
- Generated charts (`trending_dashboard.html`) must utilize the exact D3 or Chart.js color wheels defined in the `:root` CSS variables.
- PDF generation (if triggered by `document_parser.py`) must append the standard `4culture-grants-list.png` logo utilizing relative aspect ratios to prevent squashing.

By adhering to this granular 3000-word design document, the `app_login_agent_automation_cli` ensures absolute visual and functional continuity. Whether a user is reading a terminal output flag at midnight or reviewing an analytical chart at dawn, the aesthetic rules are permanent and unifying.
