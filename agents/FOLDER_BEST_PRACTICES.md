# Agents Directory (`agents/`) - Lowest-Level Best Practices & Checklist

This document contains the lowest-level checklist for AI agent configurations and prompt hierarchies.

## Directory Overview
The `agents/` directory manages AI interaction logic, system prompts, and tool boundary configurations.

---

## Subdirectory Checklists

### 1. `google_sites/`
- **Feature**: Autonomous generation agents for Google Sites structures.
- **Detailed Checklist**:
  - [x] **Prompt Versioning**: Maintain a version history of top-level system prompts.
  - [x] **Fallback Constraints**: Enforce fallback constraints for model rate-limiting (e.g., exponential backoff).
  - [x] **Tool Boundaries**: Ensure AI cannot mutate external environments without explicit verification chains.

### 2. `instagram_campaigns/`
- **Feature**: Autonomous drafting agents for social media narrative construction.
- **Detailed Checklist**:
  - [x] **Hallucination Prevention**: Add strict payload schemas (`JSON` shape validation via Pydantic/dataclasses) to bound AI outputs.
  - [x] **PII Guardrails**: Implement sanitization layers that scrub raw inputs before feeding to the LLM.
  - [x] **Deterministic Seeding**: Standardize temperature boundaries (e.g., `0.2` for logical extraction, `0.7` for creative generation).
