# Templates Directory (`templates/`) - Lowest-Level Best Practices & Checklist

This document contains the lowest-level, file-by-file checklist for every component within the `templates/` directory.

## Directory Overview
The `templates/` directory houses scaffolding used for payload generation, UI scaffolding, or document parsing mechanisms.

---

## File-Level Checklists

### 1. `business_profile.md`
- **Feature**: Holds mock schema for business entity configurations.
- **Detailed Checklist**:
  - [x] Standardize schema placeholders (`[Mock Data]`) for predictable Regex/parsing logic.
  - [x] Document markdown structure (Header bounds) to prevent parser desyncs.

### 2. `design_preferences.md`
- **Feature**: Template for recording UX parameters.
- **Detailed Checklist**:
  - [x] Define standardized checkbox strings (`- [ ]`, `- [X]`) for explicit state detection.
  - [x] Enforce clear key-value pair demarcations (`**Key:** [Value]`).

### 3. `page_content.md`
- **Feature**: Defines page hierarchies and content routing templates.
- **Detailed Checklist**:
  - [x] Implement strict demarcation blocks (`## Page: Name`) for layout chunking logic.
  - [x] Include fallback default logic inside the python `extractor.py` if optional tags are missing.
