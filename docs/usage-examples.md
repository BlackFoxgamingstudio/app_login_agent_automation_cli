# SDK CLI Usage Examples

## Quick Start

### 1. Login to 4Culture Portal

```bash
# Basic login
python3 -m agents.grant_scraper.sdk_cli auth login \
  --username "YOUR_USERNAME" \
  --password "YOUR_PASSWORD"

# With JSON output
python3 -m agents.grant_scraper.sdk_cli --json auth login \
  --username "YOUR_USERNAME" \
  --password "YOUR_PASSWORD"

# Using environment variables
export 4CULTURE_USERNAME="YOUR_USERNAME"
export 4CULTURE_PASSWORD="YOUR_PASSWORD"
python3 -m agents.grant_scraper.sdk_cli auth login
```

**Note:** MCP browser tools must be available. In Cursor IDE, they are automatically available.

### 2. Extract Data from Documents

```bash
# Extract grant data
python3 -m agents.grant_scraper.sdk_cli data extract \
  --grant-name "Moving Stories: Short-Form Graphic Novels for King County Metro Transit RapidRide" \
  --output extracted_data.json

# With JSON output
python3 -m agents.grant_scraper.sdk_cli --json data extract \
  --grant-name "Moving Stories" \
  --doc docs/02-green-stem-expo-technical.md
```

### 3. Validate Data

```bash
python3 -m agents.grant_scraper.sdk_cli data validate \
  --grant-name "Moving Stories"
```

### 4. Map Data to Form Fields

```bash
# Without narratives
python3 -m agents.grant_scraper.sdk_cli mapping map \
  --grant-name "Moving Stories" \
  --data-file standardized.json \
  --output mapped_fields.json

# With narrative generation
python3 -m agents.grant_scraper.sdk_cli mapping map \
  --grant-name "Moving Stories" \
  --use-narratives \
  --openai-api-key "your-api-key" \
  --output mapped_fields.json
```

### 5. Start New Application

```bash
python3 -m agents.grant_scraper.sdk_cli form start \
  --grant-name "Moving Stories: Short-Form Graphic Novels for King County Metro Transit RapidRide"
```

### 6. Fill Form Fields

```bash
# Fill all fields from instructions file
python3 -m agents.grant_scraper.sdk_cli form fill \
  --instructions-file instructions.json

# Fill single field
python3 -m agents.grant_scraper.sdk_cli form fill \
  --field-name "Project Title" \
  --value "My Project" \
  --field-type "text"
```

### 7. Save Draft

```bash
python3 -m agents.grant_scraper.sdk_cli form save
```

### 8. Complete Workflow

```bash
# Full automation workflow
python3 -m agents.grant_scraper.sdk_cli workflow full \
  --grant-name "Moving Stories" \
  --use-narratives \
  --openai-api-key "your-api-key"

# Dry run (extract and map only)
python3 -m agents.grant_scraper.sdk_cli workflow full \
  --grant-name "Moving Stories" \
  --dry-run
```

### 9. Database Operations

```bash
# Add grant to database
python3 -m agents.grant_scraper.sdk_cli database add \
  --name "Moving Stories" \
  --deadline "2026-01-13" \
  --status planned \
  --amount 50000

# Update grant status
python3 -m agents.grant_scraper.sdk_cli database update \
  --grant-id 1 \
  --status in_progress \
  --progress 50 \
  --current-step "Form Filling"

# List grants
python3 -m agents.grant_scraper.sdk_cli database list --status in_progress

# Get grant details
python3 -m agents.grant_scraper.sdk_cli database get --grant-id 1
```

### 10. Generate Reports

```bash
# Generate completion report
python3 -m agents.grant_scraper.sdk_cli report generate \
  --result-file result.json \
  --output report.md

# Generate dashboard
python3 -m agents.grant_scraper.sdk_cli report dashboard
```

## Browser Commands

### Navigate

```bash
python3 -m agents.grant_scraper.sdk_cli browser navigate \
  --url "https://apply.4culture.org"
```

### Take Snapshot

```bash
python3 -m agents.grant_scraper.sdk_cli browser snapshot \
  --output snapshot.json
```

### Click Element

```bash
python3 -m agents.grant_scraper.sdk_cli browser click \
  --description "Submit button"
```

### Type Text

```bash
python3 -m agents.grant_scraper.sdk_cli browser type \
  --description "Email field" \
  --text "user@example.com"
```

### Take Screenshot

```bash
python3 -m agents.grant_scraper.sdk_cli browser screenshot \
  --name "form-filled"
```

## Narrative Generation

### Generate Single Narrative

```bash
python3 -m agents.grant_scraper.sdk_cli narrative generate \
  --grant-name "Moving Stories" \
  --narrative-type "project_description" \
  --openai-api-key "your-api-key" \
  --output narrative.txt
```

### Generate All Narratives

```bash
python3 -m agents.grant_scraper.sdk_cli narrative generate-all \
  --grant-name "Moving Stories" \
  --openai-api-key "your-api-key" \
  --output all_narratives.json
```

## Complete Example Workflow

```bash
# Step 1: Extract data
python3 -m agents.grant_scraper.sdk_cli data extract \
  --grant-name "Moving Stories" \
  --output data.json

# Step 2: Validate
python3 -m agents.grant_scraper.sdk_cli data validate \
  --grant-name "Moving Stories"

# Step 3: Standardize
python3 -m agents.grant_scraper.sdk_cli data standardize \
  --grant-name "Moving Stories" \
  --output standardized.json

# Step 4: Map with narratives
python3 -m agents.grant_scraper.sdk_cli mapping map \
  --grant-name "Moving Stories" \
  --data-file standardized.json \
  --use-narratives \
  --openai-api-key "your-key" \
  --output mapped.json

# Step 5: Create instructions
python3 -m agents.grant_scraper.sdk_cli mapping create-instructions \
  --mapped-file mapped.json \
  --output instructions.json

# Step 6: Login
python3 -m agents.grant_scraper.sdk_cli auth login

# Step 7: Start application
python3 -m agents.grant_scraper.sdk_cli form start \
  --grant-name "Moving Stories"

# Step 8: Fill form
python3 -m agents.grant_scraper.sdk_cli form fill \
  --instructions-file instructions.json

# Step 9: Validate form
python3 -m agents.grant_scraper.sdk_cli form validate

# Step 10: Save draft
python3 -m agents.grant_scraper.sdk_cli form save

# Step 11: Update database
python3 -m agents.grant_scraper.sdk_cli database update \
  --grant-id 1 \
  --status in_progress \
  --progress 100
```

## Output Formats

All commands support multiple output formats:

```bash
# Human-readable (default)
python3 -m agents.grant_scraper.sdk_cli data extract --grant-name "Grant"

# JSON
python3 -m agents.grant_scraper.sdk_cli --json data extract --grant-name "Grant"

# YAML
python3 -m agents.grant_scraper.sdk_cli --yaml data extract --grant-name "Grant"
```

## Error Handling

The CLI uses standard exit codes:

- `0`: Success
- `1`: General error
- `2`: Validation error
- `3`: Authentication error
- `4`: Network error
- `5`: Configuration error

Check exit codes in scripts:

```bash
python3 -m agents.grant_scraper.sdk_cli auth login
if [ $? -eq 0 ]; then
    echo "Login successful"
else
    echo "Login failed"
fi
```

## MCP Tools Availability

**In Cursor IDE:**
- MCP tools are automatically available
- Browser automation commands work immediately

**In Regular Terminal:**
- MCP tools require MCP server configuration
- Browser commands will fail with helpful error messages
- Data extraction and mapping commands work without MCP tools

