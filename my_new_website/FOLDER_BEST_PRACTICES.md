# My New Website (`my_new_website/`) - Lowest-Level Best Practices & Checklist

This document contains the lowest-level, component-by-component checklist for standalone web deployments.

## Directory Overview
The `my_new_website/` directory holds distinct standalone frontend application frameworks built via CLI instructions or generators.

---

## Component-Level Checklists

### 1. `grant_scraper/` Web Portal Subsystem
- **Feature**: Frontend representation of scraped grants data.
- **Detailed Checklist**:
  - [x] **Asset Minification**: Validate that deployment chains compress CSS/JS assets for production.
  - [x] **Vanilla JS Strict Mode**: All scripts must begin with `'use strict';` and utilize modular closures/IIFE to prevent global namespace mutation.
  - [x] **DOM Manipulation Safety**: Ensure `querySelector` chains handle `null` safely to prevent console freezing on dynamic renders.

### 2. Global Styling & Theming
- **Feature**: Uniformity across all generated web components.
- **Detailed Checklist**:
  - [x] Establish a generic `:root` stylesheet defining CSS custom properties (variables) for palettes (`--primary`, `--accent`, `--surface`).
  - [x] Replace all hardcoded pixel measurements with `rem`/`em` to respect native accessibility scaling.
  - [x] Embed semantic landmarks (`<main>`, `<header>`, `<footer>`, `<nav>`) to satisfy WCAG constraints.
