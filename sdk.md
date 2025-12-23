# Complete CLI SDK Implementation Plan



## Objective

Transform the existing CLI into a comprehensive SDK-style CLI tool that allows developers to:

1. Execute any individual function/step independently

2. Run complete workflows with multiple steps

3. Have fine-grained control over the automation process

4. Use the CLI as a complete development toolkit

## Current System Analysis

### Workflow Steps Identified:

1. **Login** - Authenticate to 4Culture portal

2. **Extract Data** - Parse documents and extract grant information

3. **Validate Data** - Validate extracted data completeness

4. **Standardize Data** - Convert to standardized format

5. **Map Fields** - Map data to form fields

6. **Generate Narratives** - Create prose narratives (optional)

7. **Validate Mappings** - Validate field mappings

8. **Navigate** - Navigate to grant application page

9. **Start Application** - Begin new grant application

10. **Extract Form Structure** - Get form field structure

11. **Fill Fields** - Fill individual or all form fields

12. **Handle Validation Errors** - Detect and handle form errors

13. **Save Draft** - Save application draft

14. **Update Database** - Track grant in database

15. **Generate Report** - Create completion report

16. **Generate Dashboard** - Create HTML dashboard

### Database Operations:

- Add grant

- Update grant status

- Get grants by status
- Get grants by month

- Get grant details
- Add document

- Add milestone

- Close database

### Browser Operations:

- Navigate to URL
- Take snapshot

- Find element
- Click element

- Type text

- Select option
- Take screenshot

- Get current URL

- Wait for conditions

## Implementation Plan

### 1. Create New SDK CLI Structure

**File**: `agents/grant_scraper/sdk_cli.py`

Create a new comprehensive CLI with the following command structure:

```javascript
grant-sdk
├── auth
│   ├── login          # Login to 4Culture
│   └── logout         # Logout/close browser
├── data
│   ├── extract        # Extract data from documents
│   ├── validate       # Validate extracted data
│   ├── standardize    # Standardize data format
│   └── identify-docs  # Identify relevant documents
├── mapping
│   ├── map            # Map data to form fields
│   ├── validate-map   # Validate field mappings
│   └── create-instructions  # Create field filling instructions
├── narrative
│   ├── generate       # Generate narrative for field
│   ├── generate-all   # Generate all narratives
│   └── validate       # Validate narrative quality
├── browser
│   ├── navigate       # Navigate to URL
│   ├── snapshot       # Take page snapshot
│   ├── find           # Find element on page
│   ├── click          # Click element
│   ├── type           # Type text into field
│   ├── select         # Select dropdown option
│   ├── screenshot     # Take screenshot
│   └── wait           # Wait for condition
├── form
│   ├── start          # Start new application
│   ├── extract-structure  # Extract form structure
│   ├── fill           # Fill form field(s)
│   ├── fill-all       # Fill all fields
│   ├── validate       # Check for validation errors
│   └── save           # Save draft
├── workflow
│   ├── full           # Run complete workflow
│   ├── extract-only   # Extract and map only
│   ├── fill-only      # Fill form only (requires mapped data)
│   └── custom         # Custom workflow from steps
├── database
│   ├── add            # Add grant to database
│   ├── update         # Update grant status
│   ├── get            # Get grant details
│   ├── list           # List grants by status
│   ├── timeline       # Get grants by month
│   ├── add-doc        # Add document to grant
│   └── add-milestone  # Add milestone to grant
├── report
│   ├── generate       # Generate completion report
│   └── dashboard      # Generate HTML dashboard
└── config
    ├── show           # Show current configuration
    └── validate       # Validate configuration file
```



### 2. Individual Step Commands

Each command should:

- Accept required parameters

- Support optional flags for customization

- Output results in JSON format (with --json flag)

- Provide detailed error messages

- Support dry-run mode where applicable

### 3. Workflow Commands

Workflow commands should:

- Allow specifying which steps to run

- Support step dependencies

- Provide progress tracking

- Support resume from checkpoint

- Allow skipping steps

### 4. State Management

- Save workflow state after each step

- Allow resuming from saved state

- Track progress and completion status
- Store intermediate results

### 5. Configuration Management

- Support configuration files

- Allow overriding config via CLI args

- Validate configuration before execution

- Show effective configuration

### 6. Output Formats

- Human-readable (default)

- JSON (--json flag)
- YAML (--yaml flag)

- CSV (for data exports)

### 7. Error Handling

- Detailed error messages

- Error codes for programmatic use
- Retry mechanisms

- Graceful degradation

### 8. Logging

- Configurable log levels

- Log to file option

- Structured logging for JSON output

## Files to Create/Modify

1. **`agents/grant_scraper/sdk_cli.py`** (NEW)

- Main SDK CLI implementation

- All individual step commands

- Workflow orchestration

- State management

2. **`agents/grant_scraper/workflow_state.py`** (NEW)

- State management for workflows

- Checkpoint/resume functionality

- Progress tracking

3. **`agents/grant_scraper/cli.py`** (MODIFY)

- Keep existing commands for backward compatibility

- Add reference to new SDK CLI

- Or migrate to SDK CLI

4. **`agents/grant_scraper/__init__.py`** (MODIFY)

- Export SDK CLI classes

- Export workflow state manager

5. **`agents/grant_scraper/README.md`** (UPDATE)

- Add SDK CLI documentation

- Add examples for all commands

- Add workflow examples

## Implementation Details

### Command Structure Example

```python
# Individual step
grant-sdk data extract --grant-name "Grant Name" --doc docs/file.md --output result.json

# Workflow
grant-sdk workflow full --grant-name "Grant Name" --steps login,extract,map,fill,save

# Database
grant-sdk database add --name "Grant Name" --deadline "2026-01-15" --status planned

# Browser
grant-sdk browser navigate --url "https://apply.4culture.org" --wait-for "Login"
```



### State File Format

```json
{
  "workflow_id": "uuid",
  "grant_name": "Grant Name",
  "steps_completed": ["login", "extract"],
  "current_step": "map",
  "state": {
    "data_extracted": {...},
    "fields_mapped": [...],
    "form_structure": {...}
  },
  "checkpoint_path": "workflows/uuid/checkpoint.json"
}
```



### Error Codes

- 0: Success

- 1: General error

- 2: Validation error

- 3: Authentication error

- 4: Network error

- 5: Configuration error

## Success Criteria

- All individual steps can be executed independently

- Workflows can be run with custom step sequences

- State can be saved and resumed

- All commands support JSON output

- Comprehensive error handling

- Complete documentation with examples