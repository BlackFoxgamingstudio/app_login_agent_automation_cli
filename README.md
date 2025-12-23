# 4Culture Grant Application Automation System

## Overview

The 4Culture Grant Application Automation System is a comprehensive python3-based solution designed to streamline the process of applying for grants through the 4Culture application portal. This system automates the tedious and time-consuming task of manually filling out grant application forms by extracting relevant information from your existing grant documentation and automatically populating the required fields.

The system is particularly valuable for organizations that maintain detailed grant documentation in markdown format, as it can intelligently parse these documents, extract structured data (such as organization information, project descriptions, budgets, and contact details), and map this data to the appropriate form fields in the 4Culture application portal. This not only saves significant time but also reduces the risk of errors that can occur during manual data entry.

Whether you're applying for a single grant or managing multiple grant applications, this automation system provides a consistent, reliable, and efficient workflow that ensures all your grant information is accurately transferred from your documentation to the application form.

## What This System Does

The 4Culture Grant Application Automation System performs several critical functions that transform the grant application process from a manual, error-prone task into an automated, streamlined workflow. At its core, the system acts as an intelligent bridge between your grant documentation and the 4Culture application portal.

**Document Processing and Data Extraction**: The system begins by scanning your documentation folder (typically containing markdown files with grant information) and identifying which documents are relevant to the specific grant you're applying for. It then uses advanced parsing techniques to extract structured data from these documents, including organization profiles, project descriptions, budget breakdowns, contact information, timelines, and technical specifications. The extraction process is intelligent enough to handle various document formats and structures, recognizing key information even when it's presented in different ways.

**Data Validation and Standardization**: Once data is extracted, the system performs comprehensive validation to ensure all required information is present and correctly formatted. It checks for missing required fields, validates data types (such as email addresses, phone numbers, and budget amounts), and identifies any inconsistencies or potential issues. The extracted data is then standardized into a consistent format that can be reliably mapped to form fields, regardless of how it was originally structured in your source documents.

**Form Field Mapping**: The system includes a sophisticated mapping engine that translates your extracted data into the specific field requirements of the 4Culture application form. This mapping handles different field types (text inputs, text areas, dropdowns, date pickers, file uploads) and understands the relationships between fields, including conditional fields that may appear based on previous selections. The mapping is configurable through YAML configuration files, allowing you to customize how your data maps to form fields for different grant types.

**Browser Automation**: The system integrates with browser automation tools (via MCP/playwright) to interact with the 4Culture web portal. It can automatically log in to your account, navigate to the appropriate grant application page, start a new application, and fill in all the form fields with the extracted and mapped data. The automation includes error handling, retry logic, and screenshot capture for debugging purposes.

**Workflow Orchestration**: All these components are orchestrated through a comprehensive workflow system that manages the entire process from start to finish. The workflow handles error recovery, provides progress tracking, generates detailed reports, and ensures that each step is completed successfully before proceeding to the next.

## Detailed Use Cases

### Use Case 1: First-Time Grant Application

If you're applying for a grant for the first time, the system can help you organize your existing documentation and ensure nothing is missed. You might have grant information scattered across multiple documents - perhaps an organization profile in one file, project details in another, and budget information in a spreadsheet or separate document. The automation system can identify all relevant documents, extract the necessary information, and consolidate it into a single, complete application.

For example, when applying for the "Moving Stories: Short-Form Graphic Novels for King County Metro Transit RapidRide" grant, the system will automatically identify that your `02-green-stem-expo-technical.md` document contains relevant information about Key Tech Labs and the Green STEM Expo project. It will extract your organization's mission statement, project description, budget requirements, and contact information, then prepare all of this data for automatic form filling.

### Use Case 2: Multiple Grant Applications

Organizations often apply for multiple grants, and each application may require similar information but in slightly different formats or with different emphasis. The automation system excels in this scenario because it can reuse your core documentation while adapting the extracted data to meet the specific requirements of each grant application. You can run the automation multiple times with different grant names, and the system will intelligently extract and format the relevant information for each application.

### Use Case 3: Updating Existing Applications

If you need to update or revise an existing grant application, the system can extract the latest information from your updated documentation and help you quickly update the form fields. This is particularly useful when project details change, budgets are revised, or new information becomes available. Instead of manually updating each field, you can simply run the automation again with your updated documents.

### Use Case 4: Data Validation and Quality Assurance

Even if you prefer to fill out forms manually, the automation system serves as an excellent quality assurance tool. You can use the extract and validate commands to ensure all required information is present in your documentation before you begin the manual application process. The system will identify missing fields, validate data formats, and provide warnings about potential issues, helping you catch problems early in the process.

## How to Use the Program

### Getting Started

Before using the automation system, ensure you have python3 3.7 or higher installed on your system. The system is designed to work with your existing grant documentation, so make sure your markdown files are organized in a `docs` folder (or specify a custom path). While the system can work without PyYAML, installing it is recommended for full configuration file support:

```bash
pip install pyyaml
```

### Step-by-Step Usage Guide

#### Step 1: Prepare Your Documentation

The system works best when your grant documentation is well-structured. While it can extract information from various formats, having clear sections for organization information, project descriptions, budgets, and contact details will yield the best results. Your documents should be in markdown format (`.md` files) and placed in the `docs` folder.

For the "Moving Stories" grant application, the system is configured to look for information in `02-green-stem-expo-technical.md`, which should contain details about Key Tech Labs and the Green STEM Expo project. This document should include sections such as "Organization Profile," "Project Information," "Budget Details," and "Contact Information."

#### Step 2: Extract and Validate Data

Before running the full automation, it's wise to first extract and validate your data to ensure everything is in order. This step helps you identify any missing information or formatting issues before attempting to fill the form.

Run the extract command to see what data the system can extract from your documents:

```bash
python3 -m agents.grant_scraper.cli extract \
  --grant-name "Moving Stories: Short-Form Graphic Novels for King County Metro Transit RapidRide" \
  --doc docs/02-green-stem-expo-technical.md \
  --output extracted_data.json
```

This command will scan your document, extract all relevant information, and save it to a JSON file. Review this file to verify that all necessary information was correctly extracted. The output will show you the organization name, project description, budget amounts, contact information, and other key details that will be used in the application.

Next, validate the extracted data to ensure it meets the requirements:

```bash
python3 -m agents.grant_scraper.cli validate \
  --grant-name "Moving Stories: Short-Form Graphic Novels for King County Metro Transit RapidRide" \
  --config agents/grant_scraper/grant_config.yaml
```

The validation process checks for required fields, validates data formats (such as email addresses and phone numbers), and identifies any potential issues. If validation fails, the system will tell you exactly which fields are missing or invalid, allowing you to update your documentation before proceeding.

#### Step 3: Run a Dry Run

Before actually filling out the form, perform a dry run to see how the system would map your data to form fields without making any changes to the actual application:

```bash
python3 -m agents.grant_scraper.cli automate \
  --grant-name "Moving Stories: Short-Form Graphic Novels for King County Metro Transit RapidRide" \
  --dry-run
```

The dry run will extract and map all your data, showing you exactly which fields would be filled and with what values. This is an excellent way to review the automation before it actually interacts with the 4Culture portal. The output will include a detailed list of all fields that would be filled, their values, and any warnings or issues that were identified.

#### Step 4: Run Full Automation

Once you're satisfied with the data extraction and mapping, you can run the full automation. This will actually log in to the 4Culture portal, navigate to the grant application, and fill out the form:

**Basic automation (without narrative generation):**
```bash
python3 -m agents.grant_scraper.cli automate \
  --grant-name "Moving Stories: Short-Form Graphic Novels for King County Metro Transit RapidRide" \
  --username Keyisaccess \
  --password "Outlaw22!!" \
  --config agents/grant_scraper/grant_config.yaml
```

**With narrative generation (requires OpenAI API key):**
```bash
# Option 1: Using environment variable
export OPENAI_API_KEY='your-api-key-here'
python3 -m agents.grant_scraper.cli automate \
  --grant-name "Moving Stories: Short-Form Graphic Novels for King County Metro Transit RapidRide" \
  --use-narratives

# Option 2: Using CLI argument
python3 -m agents.grant_scraper.cli automate \
  --grant-name "Moving Stories: Short-Form Graphic Novels for King County Metro Transit RapidRide" \
  --use-narratives \
  --openai-api-key 'your-api-key-here'
```

**Getting an OpenAI API Key:**
1. Go to https://platform.openai.com/api-keys
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key and use it as shown above
5. **Important:** Never commit your API key to version control!

**Important Note**: The current implementation prepares all data and field mappings, but the actual browser interaction (clicking buttons, filling fields) requires integration with browser MCP tools. The system provides all the necessary data and instructions for form filling, but you may need to complete the browser automation steps manually or extend the CLI to use MCP browser tools directly.

The automation process will:
1. Extract data from your documents
2. Validate and standardize the data
3. Map the data to form fields
4. Generate a detailed report showing what was done
5. Provide field-by-field instructions for form filling (if browser automation isn't fully integrated)

#### Step 5: Review and Complete

After the automation runs, review the generated report to see which fields were successfully prepared, which fields need manual attention, and any warnings or errors that occurred. The report will be saved as a Markdown file and will include:
- A summary of all steps completed
- A list of all fields that were mapped
- Any validation errors or warnings
- Screenshots captured during the process (if enabled)
- Next steps for completing the application

Even if the automation doesn't complete every step automatically, it will have prepared all your data in a structured format that makes manual completion much faster and more accurate.

#### Step 6: View Planning Dashboard

Generate and view the HTML dashboard to see all your grants organized by deadline, status, and priority:

```bash
python3 -m agents.grant_scraper.cli dashboard
```

This will generate `grant_dashboard.html` which you can open in any browser. The dashboard shows:
- All planned grant applications
- Applications in progress with completion status
- Submitted and completed applications
- Grants organized by deadline month
- Priority-based view for strategic planning
- Complete workflow documentation

The dashboard is automatically updated when you run automation workflows, so it always reflects the current status of all your grant applications.

### Using the python3 API

For more advanced use cases or integration with other systems, you can use the python3 API directly:

```python3
from agents.grant_scraper import AutomationWorkflow

# Initialize the workflow with your credentials and configuration
workflow = AutomationWorkflow(
    username="Keyisaccess",
    password="Outlaw22!!",
    docs_folder="docs",
    config_path="agents/grant_scraper/grant_config.yaml"
)

# Run the automation for a specific grant
result = workflow.run_automation(
    grant_name="Moving Stories: Short-Form Graphic Novels for King County Metro Transit RapidRide",
    document_paths=["docs/02-green-stem-expo-technical.md"],
    dry_run=False  # Set to True for testing without filling the form
)

# Generate a detailed report
report = workflow.generate_report(result, "automation_report.md")
print(report)

# Check the result status
if result['success']:
    print("Automation completed successfully!")
    print(f"Fields filled: {len(result.get('fields_filled', []))}")
else:
    print("Automation encountered errors:")
    for error in result.get('errors', []):
        print(f"  - {error}")
```

The python3 API gives you programmatic control over the automation process, allowing you to integrate it into larger workflows, customize the behavior, or build additional tools on top of it.

## File Structure

The grant scraper system is organized into a clear directory structure that separates different concerns and makes the codebase maintainable and easy to navigate. Here's the complete file structure:

```
agents/grant_scraper/
├── __init__.py                    # Package initialization and exports
├── README.md                      # This documentation file
├── scraper.py                     # Base scraper class for 4Culture portal
├── document_parser.py             # Markdown document parsing and extraction
├── data_extractor.py              # Data extraction and validation service
├── form_mapper.py                 # Form field mapping and validation
├── application_automator.py       # Browser automation extension
├── automation_workflow.py         # Main workflow orchestrator
├── cli.py                         # Command-line interface
├── grant_database.py              # Database for grant planning and tracking
├── grant_dashboard.py             # HTML dashboard generator
├── dashboard_cli.py               # Dashboard management CLI
├── narrative_generator.py         # OpenAI narrative generation
├── mcp_browser_integration.py     # MCP browser tools integration
├── mcp_tools_helper.py            # MCP tools helper functions
├── seed_2026_grants.py            # Database seeding script for 2026 grants
├── grant_config.yaml              # Grant-specific configuration
├── grant_list_snapshot.yaml       # Snapshot of grants list
├── grant_dashboard.html           # Generated HTML dashboard
├── grants.db                      # SQLite database for grant tracking
├── 4culture-grants-list.png       # Screenshot of grants list page
└── screenshots/                   # Directory for automation screenshots
    └── (screenshots saved here during automation)
```

### File Descriptions

**`__init__.py`**: This file initializes the package and exports all the main classes, making them easily importable. It defines the public API of the grant_scraper module, allowing you to import classes like `AutomationWorkflow`, `DocumentParser`, and `DataExtractor` directly.

**`README.md`**: Comprehensive documentation covering all aspects of the system, including usage instructions, architecture details, configuration, and troubleshooting.

**`scraper.py`**: Contains the base `GrantScraper` class that provides fundamental functionality for interacting with the 4Culture portal. This includes URL constants, basic login methods, and grant list retrieval. It serves as the foundation that other components build upon.

**`document_parser.py`**: Implements the `DocumentParser` class responsible for parsing markdown files and extracting structured data. This module contains all the logic for reading markdown content, identifying sections, extracting values using regular expressions, and organizing information into structured dictionaries. It handles various data types including organization info, project details, budgets, contact information, timelines, and technical specifications.

**`data_extractor.py`**: Contains the `DataExtractor` class that orchestrates the data extraction process. It identifies which documents are relevant to a specific grant, coordinates the parsing of multiple documents, merges data from different sources, and performs validation to ensure data quality. This is the component that ties together document parsing with grant-specific requirements.

**`form_mapper.py`**: Implements the `FormMapper` class that translates extracted data into form field mappings. It loads configuration from YAML files, maps data fields to form fields, handles different field types (text, textarea, select, number, etc.), validates mapped fields, and creates instructions for form filling. This component is crucial for ensuring data is correctly formatted for the application form.

**`application_automator.py`**: Extends the base `GrantScraper` class with form automation capabilities. It provides methods for starting new applications, navigating forms, filling fields, handling validation errors, and saving drafts. While the actual browser interaction is handled via MCP tools, this module provides the structured interface and methods for automation.

**`automation_workflow.py`**: Contains the `AutomationWorkflow` class that orchestrates the entire automation process. This is the main coordinator that brings together all the other components, manages the workflow state, handles errors, generates reports, and ensures the process completes successfully. It's the high-level interface that users interact with.

**`cli.py`**: Implements the command-line interface for the automation system. It provides four main commands (extract, validate, automate, dashboard) with comprehensive argument parsing, help text, and error handling. This is the primary entry point for users who want to run the automation from the command line.

**`grant_database.py`**: Contains the `GrantDatabase` class that manages a SQLite database for tracking grant applications, status, progress, deadlines, and planning information. The database automatically tracks grants as you run the automation workflow and provides query methods for dashboard generation.

**`grant_dashboard.py`**: Implements the `GrantDashboard` class that generates a comprehensive HTML dashboard for grant planning and tracking. The dashboard includes multiple views (Timeline, Status, Priority, Documentation), search functionality, export capabilities, and complete workflow documentation.

**`dashboard_cli.py`**: Standalone CLI for managing the grant database and generating dashboards. Provides commands for adding grants, updating status, and generating the HTML dashboard.

**`narrative_generator.py`**: Contains the `NarrativeGenerator` class that uses OpenAI API to convert structured data (bullet points, lists) into complete prose narratives suitable for grant applications. Includes comprehensive templates for different narrative types.

**`mcp_browser_integration.py`**: Provides `MCPBrowserIntegration` class that abstracts browser automation using MCP tools (Browserbase/Stagehand and Cursor IDE browser). Provides unified interface for navigation, clicking, typing, and other browser actions.

**`mcp_tools_helper.py`**: Helper module for dynamically retrieving MCP browser tools from the global namespace, enabling integration with Cursor IDE's agent environment.

**`seed_2026_grants.py`**: Script to seed the database with all relevant grants for 2026, including deadlines, amounts, descriptions, and priority levels.

**`grant_config.yaml`**: YAML configuration file that defines grant-specific settings, document mappings, field mappings, required vs optional fields, form navigation structure, browser automation settings, and narrative generation configuration. This file is essential for customizing the automation for different grant types and should be modified when applying for different grants.

**`grant_list_snapshot.yaml`**: A snapshot file that contains a record of grants found during a previous scraping session. This can be useful for reference or for understanding what grants were available at a particular time.

**`4culture-grants-list.png`**: A screenshot of the grants list page captured during initial setup. This serves as documentation of what the portal looks like and can be useful for understanding the interface structure.

**`screenshots/`**: Directory where screenshots are automatically saved during automation runs. These screenshots are captured at key steps (login, navigation, form filling, errors) and are invaluable for debugging and verification purposes.

### Dependencies

The system depends on several external packages:
- **python3 Standard Library**: `os`, `pathlib`, `typing`, `logging`, `re`, `json`, `datetime`, `time`, `argparse`, `sqlite3`
- **PyYAML** (optional but recommended): For parsing YAML configuration files
- **OpenAI** (optional): For narrative generation (`pip install openai`)
- **Browser MCP Tools**: For actual browser automation (handled externally via MCP)

### Integration Points

The grant_scraper system integrates with:
- **Documentation Folder** (`docs/`): Source of grant information in markdown format
- **Configuration Files**: YAML files for grant-specific settings
- **Database** (`grants.db`): SQLite database for grant planning and tracking
- **Browser Automation Tools**: MCP/playwright tools for web interaction
- **Output Files**: Generated reports, extracted data JSON, HTML dashboard, and screenshots

## Architecture and Components

The automation system is built with a modular architecture that separates concerns and makes each component independently testable and maintainable. Understanding the architecture helps you customize the system for your specific needs.

### DocumentParser Component

The `DocumentParser` is responsible for reading and parsing markdown files. It uses regular expressions and pattern matching to identify and extract structured information from your documents. The parser is designed to be flexible and can handle various document structures, but it works best with well-organized documents that have clear section headings.

The parser extracts information in several categories:
- **Organization Information**: Name, mission statement, organizational structure, tax status (501(c)(3)), founding year, and budget information
- **Project Information**: Project title, description, goals, impact statements, target audience, activities, and expected outcomes
- **Budget Information**: Total requested amount, line items with individual costs, matching funds information, and budget breakdowns by category
- **Contact Information**: Contact person name, email address, phone number, physical address, and website URL
- **Timeline Information**: Project start and end dates, deadlines, milestones, and project duration
- **Technical Information**: Technical specifications, equipment lists, infrastructure requirements, and technical needs

The parser handles edge cases such as missing sections, incomplete information, and various formatting styles. It also extracts metadata from document frontmatter if present, which can provide additional context for the extraction process.

### DataExtractor Component

The `DataExtractor` builds on the DocumentParser by identifying which documents are relevant to a specific grant application and merging data from multiple sources. This is particularly useful when your grant information is spread across multiple documents or when you want to combine information from different sources.

The extractor uses intelligent matching to identify relevant documents based on grant name keywords and organization information. It then merges data from all relevant documents, prioritizing non-empty values and combining lists where appropriate. For example, if one document has budget line items and another has additional budget information, the extractor will combine them into a comprehensive budget breakdown.

The extractor also performs validation to ensure data quality. It checks for required fields, validates data formats, and identifies potential issues. The validation results help you understand what information might be missing or need attention before proceeding with the application.

### FormMapper Component

The `FormMapper` translates your extracted data into the specific format required by the 4Culture application form. This component uses a configuration file (`grant_config.yaml`) that defines how each data field maps to form fields, what field types are expected, and what validation rules apply.

The mapper handles different field types appropriately:
- **Text fields**: Simple string values that are trimmed and validated for length
- **Textarea fields**: Longer text that may be formatted with line breaks
- **Select/Dropdown fields**: Values that must match specific options
- **Number fields**: Numeric values that are validated and formatted
- **Date fields**: Date values that are parsed and formatted consistently
- **Email/Phone fields**: Contact information that is validated for format

The mapper also handles conditional fields - fields that may or may not appear based on other field values. This is important for complex forms where certain sections are only relevant under specific conditions.

### ApplicationAutomator Component

The `ApplicationAutomator` extends the base `GrantScraper` class with form automation capabilities. While the base scraper handles login and navigation, the automator adds methods for form interaction, field filling, and draft saving.

The automator is designed to work with browser automation tools (MCP/playwright) to interact with the web interface. It provides a structured interface for:
- Starting new applications
- Navigating multi-page forms
- Filling form fields with extracted data
- Handling form validation errors
- Saving draft applications
- Capturing screenshots for debugging

The automator includes retry logic for failed operations and comprehensive error handling to ensure the automation process is robust and can recover from common issues.

### AutomationWorkflow Component

The `AutomationWorkflow` is the orchestrator that coordinates all the other components. It manages the complete process from document extraction through form filling, handling errors, tracking progress, and generating reports.

The workflow follows a clear sequence:
1. **Data Extraction**: Uses DataExtractor to identify and extract relevant information
2. **Data Validation**: Validates extracted data to ensure completeness and correctness
3. **Data Standardization**: Converts extracted data into a standardized format
4. **Form Mapping**: Uses FormMapper to map data to form fields
5. **Field Validation**: Validates mapped fields before form filling
6. **Browser Automation**: Coordinates browser interaction (via MCP tools or manual steps)
7. **Error Handling**: Captures and reports any errors that occur
8. **Report Generation**: Creates a comprehensive report of the automation process

The workflow maintains state throughout the process, allowing it to resume from checkpoints if needed and providing detailed progress information.

### CLI Interface

The command-line interface provides an easy-to-use entry point for the automation system. It supports four main operations:
- **Extract**: Extract and display data from documents without any form interaction
- **Validate**: Validate extracted data to ensure it meets requirements
- **Automate**: Run the complete automation workflow
- **Dashboard**: Generate HTML dashboard for grant planning and tracking

The CLI includes comprehensive help text and examples, making it accessible even to users who aren't familiar with the underlying python3 code. It handles argument parsing, error reporting, and output formatting, providing a user-friendly experience.

### Grant Database Component

The `GrantDatabase` provides persistent storage for grant planning and tracking. It automatically tracks grants as you run the automation workflow, storing:
- Grant information (name, deadline, amount, organization, project details)
- Application status and progress
- Current step in the workflow
- Draft URLs and report paths
- Errors and warnings
- Timeline milestones
- Document associations

The database enables strategic planning by organizing grants by deadline month, status, and priority, making it easy to see what's coming up and what needs attention.

### Grant Dashboard Component

The `GrantDashboard` generates a comprehensive HTML dashboard that provides stakeholders with a visual overview of all grant applications. The dashboard includes:

- **Timeline View**: Grants organized by deadline month with color-coded indicators (past/current/upcoming)
- **Status View**: Grants grouped by status (Planned, In Progress, Submitted, Completed)
- **Priority View**: Grants sorted by priority level for strategic planning
- **Documentation View**: Complete workflow documentation and usage instructions
- **Search Functionality**: Filter grants by name or description
- **Export Capability**: Export grant data to CSV
- **Interactive Cards**: Detailed grant cards with progress bars, deadlines, and status information

The dashboard is automatically updated when you run the automation workflow, ensuring stakeholders always have current information.

### Grant Database Component

The `GrantDatabase` provides persistent storage for grant planning and tracking. It automatically tracks grants as you run the automation workflow, storing:
- Grant information (name, deadline, amount, organization, project details)
- Application status and progress
- Current step in the workflow
- Draft URLs and report paths
- Errors and warnings
- Timeline milestones
- Document associations

The database enables strategic planning by organizing grants by deadline month, status, and priority, making it easy to see what's coming up and what needs attention.

### Grant Dashboard Component

The `GrantDashboard` generates a comprehensive HTML dashboard that provides stakeholders with a visual overview of all grant applications. The dashboard includes:

- **Timeline View**: Grants organized by deadline month with color-coded indicators (past/current/upcoming)
- **Status View**: Grants grouped by status (Planned, In Progress, Submitted, Completed)
- **Priority View**: Grants sorted by priority level for strategic planning
- **Documentation View**: Complete workflow documentation and usage instructions
- **Search Functionality**: Filter grants by name or description
- **Export Capability**: Export grant data to CSV
- **Interactive Cards**: Detailed grant cards with progress bars, deadlines, and status information

The dashboard is automatically updated when you run the automation workflow, ensuring stakeholders always have current information.

## Configuration

### OpenAI API Key Setup

**Important:** The OpenAI API key is NOT stored in the configuration file for security reasons. You must provide it using one of these methods:

1. **Environment Variable (Recommended):**
   ```bash
   export OPENAI_API_KEY='your-api-key-here'
   ```

2. **CLI Argument:**
   ```bash
   --openai-api-key 'your-api-key-here'
   ```

3. **Get Your API Key:**
   - Visit: https://platform.openai.com/api-keys
   - Sign in or create an account
   - Click "Create new secret key"
   - Copy and use the key (it starts with `sk-`)

**Security Note:** Never commit your API key to version control or share it publicly. Always use environment variables or CLI arguments.

## Grant Configuration

The system uses a YAML configuration file (`grant_config.yaml`) to define grant-specific settings, field mappings, and form structure. This configuration file is essential for customizing the automation for different grant types.

### Grant Information

The configuration file starts with basic grant information:
- Grant name and identifier
- Application deadline
- Current status (Open, Closed, etc.)

This information helps the system identify which grant you're applying for and provides context for the automation process.

### Document Mapping

The configuration specifies which documents contain relevant information for the grant application. You can specify a primary document (the main source of information) and additional documents that may contain supplementary information.

For the "Moving Stories" grant, the configuration specifies `02-green-stem-expo-technical.md` as the primary document, which contains information about Key Tech Labs and the Green STEM Expo project.

### Field Mappings

The most important part of the configuration is the field mappings, which define how your extracted data maps to form fields. Each mapping specifies:
- The data field name (from your documents)
- The form field name (on the 4Culture portal)
- The field type (text, textarea, select, number, etc.)
- Whether the field is required
- Any validation rules (max length, min/max values, etc.)

This mapping is crucial because it ensures your data is correctly placed in the right form fields, even if the field names don't exactly match between your documents and the form.

### Form Navigation

The configuration also includes information about the form structure, such as:
- How many pages the form has
- Which fields appear on each page
- The expected order of pages

This information helps the automation system navigate the form correctly and fill fields in the right order.

## Data Flow and Process

Understanding the data flow helps you troubleshoot issues and customize the system for your needs. The complete process follows these steps:

1. **Document Selection**: The system scans your docs folder and identifies documents relevant to the grant. It uses keyword matching and organization information to determine relevance.

2. **Document Parsing**: Relevant documents are parsed to extract structured information. The parser uses pattern matching to identify sections, extract values, and organize information into categories.

3. **Data Merging**: If multiple documents are relevant, their data is merged. The system prioritizes non-empty values and combines lists appropriately.

4. **Data Validation**: Extracted data is validated to ensure required fields are present and data formats are correct. Missing or invalid data is flagged with warnings or errors.

5. **Data Standardization**: Validated data is converted into a standardized format with consistent field names and data types. This standardization makes the data easier to work with in subsequent steps.

6. **Form Field Mapping**: Standardized data is mapped to form fields using the configuration file. The mapper handles type conversions, formatting, and validation.

7. **Field Validation**: Mapped fields are validated to ensure they meet form requirements. This includes checking required fields, validating formats, and ensuring values are within acceptable ranges.

8. **Browser Automation**: The system prepares instructions for browser automation, including which fields to fill, what values to use, and in what order. These instructions can be used with MCP browser tools or for manual completion.

9. **Error Handling**: Throughout the process, errors are captured and logged. The system attempts to continue where possible, but will stop if critical errors occur.

10. **Report Generation**: A comprehensive report is generated documenting the entire process, including what was extracted, what was mapped, what succeeded, and what needs attention.

11. **Database Tracking**: The workflow automatically updates the grant database with progress, status, and completion information, enabling real-time tracking and planning.

12. **Dashboard Update**: The HTML dashboard is regenerated to reflect the latest grant status and progress, providing stakeholders with current information.

## Error Handling and Troubleshooting

The system includes comprehensive error handling to help you identify and resolve issues. Understanding common errors and how to resolve them will make your experience smoother.

### Missing Required Fields

If the system identifies missing required fields, it will stop the automation and report exactly which fields are missing. To resolve this, update your source documents to include the missing information, then run the extraction again.

### Data Format Issues

The system validates data formats (email addresses, phone numbers, dates, etc.). If a format is invalid, it will be flagged in the validation report. Check your source documents to ensure data is formatted correctly.

### Document Not Found

If the system can't find relevant documents, check that:
- Your documents are in the correct folder (default: `docs`)
- Document names match what's expected
- Documents are in markdown format (`.md` files)

### Mapping Errors

If field mapping fails, check your `grant_config.yaml` file to ensure:
- Field names match between your data and the configuration
- Field types are correctly specified
- Required fields are marked as required

### Browser Automation Issues

If browser automation doesn't work as expected, you may need to:
- Check that you're logged in to the 4Culture portal
- Verify that the grant application is available
- Ensure browser MCP tools are properly configured
- Review screenshots captured during the process

## Output and Reports

The system generates several types of output to help you understand what happened and what needs attention.

### Extraction Reports

When you run the extract command, you'll see:
- What data was extracted from your documents
- Which fields were found and which are missing
- Validation results and warnings
- A JSON file with all extracted data (if you specify `--output`)

### Validation Reports

The validate command provides:
- A list of all required fields and their status
- Validation results for each field
- Warnings about potential issues
- Recommendations for fixing problems

### Automation Reports

The full automation generates a comprehensive report including:
- Summary of all steps completed
- List of all fields that were mapped
- Fields that were successfully prepared
- Fields that failed or need attention
- Any errors or warnings encountered
- Screenshots captured during the process
- Next steps for completing the application

All reports are saved as Markdown files that you can review, share, or include in your project documentation.

## Best Practices

To get the best results from the automation system, follow these best practices:

1. **Organize Your Documents**: Keep your grant documentation well-organized with clear section headings. This makes extraction more accurate and reliable.

2. **Use Consistent Formatting**: While the system is flexible, consistent formatting in your documents (especially for dates, amounts, and contact information) will yield better results.

3. **Validate Before Automating**: Always run the extract and validate commands before attempting full automation. This helps you catch issues early.

4. **Review Dry Runs**: Use the dry-run option to review how your data will be mapped before actually filling the form. This gives you a chance to make adjustments.

5. **Keep Configuration Updated**: As you learn more about the form structure, update your `grant_config.yaml` file to improve mapping accuracy.

6. **Save Your Work**: The system saves draft applications, but it's also good practice to keep backups of your extracted data and reports.

7. **Review Reports**: Always review the generated reports to understand what was done and what might need manual attention.

## Login Credentials

For accessing the 4Culture portal:
- **URL**: https://apply.4culture.org/login
- **Username**: Keyisaccess
- **Password**: Outlaw22!!

**Security Note**: Keep these credentials secure and never commit them to version control. Consider using environment variables or a secure credential store for production use.

## Grant Planning and Database

### Database Seeding

To seed the database with all relevant grants for 2026:

```bash
python3 agents/grant_scraper/seed_2026_grants.py
```

This will add all 2026 grants to the database with complete information including deadlines, amounts, descriptions, and priority levels. The database is automatically used by the automation workflow to track grant status and progress.

### Viewing the Dashboard

Generate the HTML dashboard at any time:

```bash
python3 -m agents.grant_scraper.cli dashboard
```

The dashboard will be saved to `agents/grant_scraper/grant_dashboard.html` and can be opened in any browser. It includes:
- Complete grant planning overview
- Timeline view organized by month
- Status tracking (Planned, In Progress, Submitted, Completed)
- Priority-based strategic planning
- Full workflow documentation
- Search and export capabilities

### Database Management

You can also manage the database directly using the dashboard CLI:

```bash
# Add a new grant
python3 -m agents.grant_scraper.dashboard_cli add \
  --name "Grant Name" \
  --deadline "January 15, 2026" \
  --amount 50000 \
  --priority 8

# Update grant status
python3 -m agents.grant_scraper.dashboard_cli update \
  --grant-id 1 \
  --status in_progress \
  --progress 75

# Generate dashboard
python3 -m agents.grant_scraper.dashboard_cli dashboard
```

## Grants Available

### Draft Applications
- **Key Tech Labs** - Status: Working

### Available Grants (Start New Application)
1. **Moving Stories: Short-Form Graphic Novel for King County Metro Transit RapidRide**
   - Deadline: January 13, 2026 at 4pm

2. **Touring Art Roster + Presenter Incentive**
   - Deadline: Open

### 2026 Grant Planning

The database has been seeded with 12 grants for 2026, distributed across all months:
- January: Moving Stories (In Progress)
- February through December: Various grants covering Arts Education, Heritage, Facilities, Collections, Capacity Building, Preservation, and Innovation

View the dashboard to see the complete grant planning overview with deadlines, amounts, and priority levels.

## Additional Resources

- **Screenshots**: Screenshots are automatically captured during automation and saved to the `screenshots/` directory for debugging and verification purposes.

- **Configuration Files**: The `grant_config.yaml` file can be customized for different grant types. Copy and modify it for each new grant application.

- **Logs**: The system uses python3's logging module. Set the log level to DEBUG for more detailed information about the automation process.

## Support and Troubleshooting

If you encounter issues:

1. **Check the Logs**: Review the console output and log files for error messages
2. **Review Reports**: Generated reports often contain helpful information about what went wrong
3. **Validate Data**: Run the validate command to check for data issues
4. **Check Configuration**: Ensure your `grant_config.yaml` file is correct and up to date
5. **Review Screenshots**: If browser automation is involved, check screenshots to see what the system saw

The system is designed to provide clear error messages and helpful guidance when issues occur. Most problems can be resolved by checking the validation reports and updating your source documents or configuration.

## SDK CLI - Complete Developer Toolkit

The SDK CLI provides a comprehensive command-line interface that allows developers to execute any individual function or step independently, or run complete workflows. This makes it a complete development toolkit for grant application automation.

### Installation and Usage

The SDK CLI is available as a python3 module:

```bash
python3 -m agents.grant_scraper.sdk_cli <command-group> <command> [options]
```

Or use the shorter alias (if configured):

```bash
grant-sdk <command-group> <command> [options]
```

### Output Formats

All commands support multiple output formats:

- **Human-readable** (default): Formatted text output
- **JSON**: `--json` flag for programmatic use
- **YAML**: `--yaml` flag for YAML output

Example:
```bash
grant-sdk data extract --grant-name "Grant Name" --json
```

### Command Groups

#### Authentication Commands (`auth`)

**Login to 4Culture:**
```bash
grant-sdk auth login --username "your-username" --password "your-password"
```

**Logout/Close Browser:**
```bash
grant-sdk auth logout
```

#### Data Commands (`data`)

**Extract data from documents:**
```bash
grant-sdk data extract --grant-name "Grant Name" --doc docs/file.md --output extracted.json
```

**Validate extracted data:**
```bash
grant-sdk data validate --grant-name "Grant Name"
```

**Standardize data format:**
```bash
grant-sdk data standardize --grant-name "Grant Name" --output standardized.json
```

**Identify relevant documents:**
```bash
grant-sdk data identify-docs --grant-name "Grant Name" --organization-name "Your Org"
```

#### Mapping Commands (`mapping`)

**Map data to form fields:**
```bash
grant-sdk mapping map --grant-name "Grant Name" --data-file standardized.json --output mapped.json
```

**With narrative generation:**
```bash
grant-sdk mapping map --grant-name "Grant Name" --use-narratives --openai-api-key "your-key" --output mapped.json
```

**Validate field mappings:**
```bash
grant-sdk mapping validate-map --mapped-file mapped.json
```

**Create field filling instructions:**
```bash
grant-sdk mapping create-instructions --mapped-file mapped.json --output instructions.json
```

#### Narrative Commands (`narrative`)

**Generate narrative for specific field:**
```bash
grant-sdk narrative generate --grant-name "Grant Name" --narrative-type "project_description" --openai-api-key "your-key"
```

**Generate all narratives:**
```bash
grant-sdk narrative generate-all --grant-name "Grant Name" --openai-api-key "your-key" --output narratives.json
```

#### Browser Commands (`browser`)

**Navigate to URL:**
```bash
grant-sdk browser navigate --url "https://apply.4culture.org"
```

**Take page snapshot:**
```bash
grant-sdk browser snapshot --output snapshot.json
```

**Find element:**
```bash
grant-sdk browser find --description "Login button"
```

**Click element:**
```bash
grant-sdk browser click --description "Submit button"
```

**Type text:**
```bash
grant-sdk browser type --description "Email field" --text "user@example.com"
```

**Select dropdown option:**
```bash
grant-sdk browser select --description "State dropdown" --values "Washington"
```

**Take screenshot:**
```bash
grant-sdk browser screenshot --name "form-filled"
```

**Wait for condition:**
```bash
grant-sdk browser wait --text "Application saved" --time 10
```

#### Form Commands (`form`)

**Start new application:**
```bash
grant-sdk form start --grant-name "Grant Name"
```

**Extract form structure:**
```bash
grant-sdk form extract-structure --output form-structure.json
```

**Fill form field(s):**
```bash
grant-sdk form fill --instructions-file instructions.json
```

Or fill a single field:
```bash
grant-sdk form fill --field-name "Project Title" --value "My Project" --field-type "text"
```

**Check for validation errors:**
```bash
grant-sdk form validate
```

**Save draft:**
```bash
grant-sdk form save
```

#### Workflow Commands (`workflow`)

**Run complete workflow:**
```bash
grant-sdk workflow full --grant-name "Grant Name" --use-narratives --openai-api-key "your-key"
```

**Dry run (extract and map only):**
```bash
grant-sdk workflow full --grant-name "Grant Name" --dry-run
```

**Custom workflow:**
```bash
grant-sdk workflow custom --grant-name "Grant Name" --steps "login,extract,map,fill,save"
```

#### Database Commands (`database`)

**Add grant to database:**
```bash
grant-sdk database add --name "Grant Name" --deadline "2026-01-15" --status planned --amount 50000
```

**Update grant status:**
```bash
grant-sdk database update --grant-id 1 --status in_progress --progress 50 --current-step "Form Filling"
```

**Get grant details:**
```bash
grant-sdk database get --grant-id 1
```

**List grants by status:**
```bash
grant-sdk database list --status in_progress
```

**Get grants timeline:**
```bash
grant-sdk database timeline
```

#### Report Commands (`report`)

**Generate completion report:**
```bash
grant-sdk report generate --result-file result.json --output report.md
```

**Generate HTML dashboard:**
```bash
grant-sdk report dashboard
```

### Workflow State Management

The SDK includes workflow state management for checkpoint and resume functionality:

**Save workflow state:**
```python3
from agents.grant_scraper import WorkflowState

state = WorkflowState()
state.set_grant_name("Grant Name")
state.add_completed_step("extract")
state.save_checkpoint()
```

**Resume from checkpoint:**
```python3
state = WorkflowState.load_from_checkpoint("workflows/uuid/checkpoint.json")
```

**List all workflows:**
```python3
workflows = WorkflowState.list_workflows()
```

### Complete Workflow Example

Here's a complete example of using the SDK CLI for a full grant application:

```bash
# Step 1: Extract data
grant-sdk data extract --grant-name "Moving Stories" --output data.json

# Step 2: Validate data
grant-sdk data validate --grant-name "Moving Stories"

# Step 3: Standardize data
grant-sdk data standardize --grant-name "Moving Stories" --output standardized.json

# Step 4: Map to form fields with narratives
grant-sdk mapping map --grant-name "Moving Stories" \
  --data-file standardized.json \
  --use-narratives \
  --openai-api-key "your-key" \
  --output mapped.json

# Step 5: Create filling instructions
grant-sdk mapping create-instructions --mapped-file mapped.json --output instructions.json

# Step 6: Login
grant-sdk auth login --username "your-username" --password "your-password"

# Step 7: Start application
grant-sdk form start --grant-name "Moving Stories"

# Step 8: Fill form
grant-sdk form fill --instructions-file instructions.json

# Step 9: Validate form
grant-sdk form validate

# Step 10: Save draft
grant-sdk form save

# Step 11: Add to database
grant-sdk database add --name "Moving Stories" --status in_progress

# Step 12: Generate dashboard
grant-sdk report dashboard
```

### Error Codes

The SDK CLI uses standard exit codes:

- `0`: Success
- `1`: General error
- `2`: Validation error
- `3`: Authentication error
- `4`: Network error
- `5`: Configuration error

### Programmatic Usage

The SDK CLI can also be used programmatically:

```python3
from agents.grant_scraper import GrantSDKCLI

cli = GrantSDKCLI()
cli.output_format = 'json'

# Create a mock args object
class Args:
    grant_name = "Grant Name"
    docs_folder = "docs"
    output = "result.json"

args = Args()
cli.cmd_data_extract(args)
```

### Integration with Existing CLI

The original CLI (`agents.grant_scraper.cli`) remains available for backward compatibility. The SDK CLI provides more granular control and is recommended for developers who need fine-grained control over the automation process.

### Best Practices

1. **Use JSON output for automation**: When scripting, use `--json` flag for easier parsing
2. **Save intermediate results**: Use `--output` flags to save results at each step
3. **Validate early**: Run validation commands before proceeding to next steps
4. **Use workflow state**: Leverage checkpoint/resume for long-running workflows
5. **Handle errors**: Check exit codes and error messages in automated scripts
6. **Test individual steps**: Use individual commands to test and debug before running full workflows

### SDK CLI vs Original CLI

| Feature | Original CLI | SDK CLI |
|---------|-------------|---------|
| Individual step execution | Limited | Full support |
| Workflow customization | Fixed | Flexible |
| Output formats | Human only | Human, JSON, YAML |
| State management | Basic | Advanced (checkpoints) |
| Browser operations | Indirect | Direct control |
| Database operations | Limited | Complete |
| Use case | End users | Developers |

The SDK CLI is the recommended tool for developers building custom automation workflows or integrating the system into larger applications.
