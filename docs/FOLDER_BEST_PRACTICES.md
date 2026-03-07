# Docs Directory (`docs/`) - Lowest-Level Best Practices & Checklist

This document contains the lowest-level, file-by-file checklist for every component within the `docs/` directory. This includes both markdown documentation files and frontend web assets.

## Directory Overview
The `docs/` directory is used to serve living documentation and showcase features, APIs, and generated web content using static site paradigms.

---

## File-Level Checklists: Frontend Assets

### 1. `script.js`
- **Feature**: Interactivity for documentation web pages.
- **Detailed Checklist**:
  - [x] Enable strict mode (`'use strict';` or implied by modules) to prevent global namespace pollution.
  - [x] Ensure event listeners use modular decomposition (e.g., isolating navigation toggle logic).
  - [x] Attach smooth-scrolling behaviors to anchor tags dynamically without inline `onclick` attributes.

### 2. `styles.css`
- **Feature**: Central stylesheet for the documentation site.
- **Detailed Checklist**:
  - [x] Implement robust **CSS Custom Properties** (`--primary-color`, etc.) attached to `:root` to support scalable theming.
  - [x] Enforce **BEM (Block Element Modifier)** naming architectures (e.g., `.nav-toggle`, `.step-content`).
  - [x] Implement scalable `@media` query breakpoints for responsive layouts.

## File-Level Checklists: HTML Pages

### 1. `index.html` & `index2.html` & `quick-start.html`
- **Feature**: Standard documentation entry points.
- **Detailed Checklist**:
  - [x] Ensure semantic HTML5 tags (`<main>`, `<section>`, `<nav>`) are used.
  - [x] Validate asset links point to relative paths correctly without hardcoded references.

### 2. `instagram_dashboard.html` & `trending_dashboard.html`
- **Feature**: Analytical data viz pages.
- **Detailed Checklist**:
  - [x] Document asynchronous data fetching mechanisms if hitting local CSVs.
  - [x] Verify responsive flexbox/grid for interactive chart alignment.

## File-Level Checklists: Markdown Artifacts

### 1. `api.md` & `cli-reference.html`
- **Feature**: Command line references.
- **Detailed Checklist**:
  - [x] Maintain auto-generation scripts or strict manual formatting to match Python `argparse` outputs.
  - [x] Ensure all arguments have type and default value identifiers.

### 2. `build-notes.md` & `simulation-run.md`
- **Feature**: Logs and workflow traces.
- **Detailed Checklist**:
  - [x] Maintain chronological logging consistency for pipeline historicals.
