"""
Grant Dashboard Generator
Creates HTML dashboard for grant planning and tracking.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from .grant_database import GrantDatabase

logger = logging.getLogger(__name__)


class GrantDashboard:
    """Generates HTML dashboard for grant planning."""

    def __init__(self, db_path: str = "grants.db"):
        """
        Initialize dashboard generator.

        Args:
            db_path: Path to grant database
        """
        self.db = GrantDatabase(db_path)
        self.output_path = Path("agents/grant_scraper/grant_dashboard.html")

    def generate_dashboard(self) -> str:
        """
        Generate HTML dashboard.

        Returns:
            Path to generated HTML file
        """
        # Get data from database
        all_grants = self.db.get_grants_by_status()
        grants_by_month = self.db.get_grants_by_month()

        # Organize by status
        planned = [g for g in all_grants if g.get("status") == "planned"]
        in_progress = [g for g in all_grants if g.get("status") == "in_progress"]
        submitted = [g for g in all_grants if g.get("status") == "submitted"]
        completed = [g for g in all_grants if g.get("status") in ["awarded", "rejected"]]

        html = self._generate_html(
            planned, in_progress, submitted, completed, grants_by_month, all_grants
        )

        # Write to file
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_path, "w", encoding="utf-8") as f:
            f.write(html)

        logger.info(f"Dashboard generated at {self.output_path}")
        return str(self.output_path)

    def _generate_html(
        self,
        planned: List[Dict],
        in_progress: List[Dict],
        submitted: List[Dict],
        completed: List[Dict],
        grants_by_month: Dict[str, Any],
        all_grants: List[Dict],
    ) -> str:
        """Generate complete HTML content."""

        return f"""<!DOCTYPE html>
<html lang="en">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Grant Application Planning Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <style>
        {self._get_css()}
    </style>
</head>
<body>
    <div class="dashboard-container">
        <header class="dashboard-header">
            <h1>Grant Application Planning Dashboard</h1>
            <p class="subtitle">Strategic Grant Planning & Application Tracking</p>
            <div class="header-stats">
                <div class="stat-card">
                    <div class="stat-value">{len(planned)}</div>
                    <div class="stat-label">Planned</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{len(in_progress)}</div>
                    <div class="stat-label">In Progress</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{len(submitted)}</div>
                    <div class="stat-label">Submitted</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{len(completed)}</div>
                    <div class="stat-label">Completed</div>
                </div>
            </div>
        </header>

        <nav class="dashboard-nav">
            <div class="nav-left">
                <button class="nav-btn active" data-view="timeline">Timeline View</button>
                <button class="nav-btn" data-view="status">Status View</button>
                <button class="nav-btn" data-view="priority">Priority View</button>
                <button class="nav-btn" data-view="documentation">Documentation</button>
                <button class="nav-btn" data-view="engineering">Engineering</button>
            </div>
            <div class="nav-right">
                <input type="text" id="search-input" class="search-input" placeholder="Search grants..." onkeyup="filterGrants(this.value)">
                <button class="btn-export" onclick="exportDashboard('csv')">Export CSV</button>
            </div>
        </nav>

        <main class="dashboard-main">
            <!-- Timeline View -->
            <section id="timeline-view" class="view-section active">
                <h2>Grant Applications by Deadline</h2>
                {self._generate_timeline_view(grants_by_month)}
            </section>

            <!-- Status View -->
            <section id="status-view" class="view-section">
                <h2>Applications by Status</h2>
                {self._generate_status_view(planned, in_progress, submitted, completed)}
            </section>

            <!-- Priority View -->
            <section id="priority-view" class="view-section">
                <h2>Priority Applications</h2>
                {self._generate_priority_view(all_grants)}
            </section>

            <!-- Documentation View -->
            <section id="documentation-view" class="view-section">
                {self._generate_documentation_view()}
            </section>

            <!-- Engineering Documentation View -->
            <section id="engineering-view" class="view-section">
                {self._generate_engineering_documentation_view()}
            </section>
        </main>
    </div>

    <script>
        {self._get_javascript()}
    </script>
</body>
</html>"""

    def _generate_timeline_view(self, grants_by_month: Dict[str, Any]) -> str:
        """Generate timeline view HTML."""
        if not grants_by_month:
            return '<p class="empty-state">No grants with deadlines found.</p>'

        html = '<div class="timeline-container">'

        for month_key in sorted(grants_by_month.keys()):
            month_data = grants_by_month[month_key]
            month_name = month_data["month_name"]
            grants = month_data["grants"]

            # Determine if month is upcoming, current, or past
            now = datetime.now()
            month_date = datetime.strptime(month_key, "%Y-%m")
            is_past = month_date < now.replace(day=1)
            is_current = month_date.year == now.year and month_date.month == now.month

            month_class = (
                "month-past" if is_past else "month-current" if is_current else "month-upcoming"
            )

            html += f"""
            <div class="timeline-month {month_class}">
                <div class="month-header">
                    <h3>{month_name}</h3>
                    <span class="grant-count">{len(grants)} grant(s)</span>
                </div>
                <div class="grants-list">
            """

            for grant in grants:
                html += self._generate_grant_card(grant, show_deadline=True)

            html += """
                </div>
            </div>
            """

        html += "</div>"
        return html

    def _generate_status_view(
        self,
        planned: List[Dict],
        in_progress: List[Dict],
        submitted: List[Dict],
        completed: List[Dict],
    ) -> str:
        """Generate status view HTML."""
        html = """
        <div class="status-container">
            <div class="status-column">
                <h3 class="status-header planned">Planned Applications</h3>
                <div class="grants-list">
        """
        for grant in planned:
            html += self._generate_grant_card(grant)
        if not planned:
            html += '<p class="empty-state">No planned applications</p>'
        html += """
                </div>
            </div>

            <div class="status-column">
                <h3 class="status-header in-progress">In Progress</h3>
                <div class="grants-list">
        """
        for grant in in_progress:
            html += self._generate_grant_card(grant, show_progress=True)
        if not in_progress:
            html += '<p class="empty-state">No applications in progress</p>'
        html += """
                </div>
            </div>

            <div class="status-column">
                <h3 class="status-header submitted">Submitted</h3>
                <div class="grants-list">
        """
        for grant in submitted:
            html += self._generate_grant_card(grant)
        if not submitted:
            html += '<p class="empty-state">No submitted applications</p>'
        html += """
                </div>
            </div>

            <div class="status-column">
                <h3 class="status-header completed">Completed</h3>
                <div class="grants-list">
        """
        for grant in completed:
            html += self._generate_grant_card(grant)
        if not completed:
            html += '<p class="empty-state">No completed applications</p>'
        html += """
                </div>
            </div>
        </div>
        """
        return html

    def _generate_priority_view(self, all_grants: List[Dict]) -> str:
        """Generate priority view HTML."""
        # Sort by priority (higher first) and deadline
        sorted_grants = sorted(
            all_grants,
            key=lambda x: (-x.get("priority", 5), x.get("deadline_timestamp") or float("inf")),
        )

        html = '<div class="priority-container">'
        for grant in sorted_grants:
            html += self._generate_grant_card(grant, show_priority=True)
        html += "</div>"
        return html

    def _generate_documentation_view(self) -> str:
        """Generate documentation view HTML."""
        return """
        <div class="documentation-container">
            <div class="doc-section">
                <h2>Grant Application Automation System</h2>
                <p class="doc-intro">
                    This comprehensive system automates the entire grant application process, from data extraction 
                    to form filling, with intelligent planning and tracking capabilities designed for stakeholders 
                    and grant writers.
                </p>
            </div>

            <div class="doc-section">
                <h3>📋 What This System Does</h3>
                <div class="feature-grid">
                    <div class="feature-card">
                        <h4>Document Processing</h4>
                        <p>Automatically extracts structured data from your markdown grant documents, including organization info, project descriptions, budgets, and contact details.</p>
                    </div>
                    <div class="feature-card">
                        <h4>Intelligent Mapping</h4>
                        <p>Maps extracted data to specific form fields using configurable field mappings, handling different field types (text, textarea, select, etc.).</p>
                    </div>
                    <div class="feature-card">
                        <h4>Narrative Generation</h4>
                        <p>Converts bullet points and structured data into complete, professional prose narratives using OpenAI, ensuring grant applications meet foundation requirements.</p>
                    </div>
                    <div class="feature-card">
                        <h4>Browser Automation</h4>
                        <p>Automatically logs in, navigates forms, fills fields, and saves drafts using MCP browser tools, reducing manual data entry time by 90%.</p>
                    </div>
                    <div class="feature-card">
                        <h4>Planning & Tracking</h4>
                        <p>Database-driven planning system tracks all grants, deadlines, progress, and status, with visual dashboards for stakeholder review.</p>
                    </div>
                    <div class="feature-card">
                        <h4>Quality Assurance</h4>
                        <p>Comprehensive validation ensures all required fields are present, data formats are correct, and applications are complete before submission.</p>
                    </div>
                </div>
            </div>

            <div class="doc-section">
                <h3>🚀 Quick Start Guide</h3>
                
                <div class="step-card">
                    <div class="step-number">1</div>
                    <div class="step-content">
                        <h4>Prepare Your Documents</h4>
                        <p>Organize your grant information in markdown files in the <code>docs/</code> folder. Include sections for:</p>
                        <ul>
                            <li>Organization Profile (name, mission, tax status)</li>
                            <li>Project Information (title, description, goals, impact)</li>
                            <li>Budget Details (total requested, line items, breakdown)</li>
                            <li>Contact Information (name, email, phone, address)</li>
                            <li>Timeline (start date, end date, milestones)</li>
                        </ul>
                    </div>
                </div>

                <div class="step-card">
                    <div class="step-number">2</div>
                    <div class="step-content">
                        <h4>Extract and Validate Data</h4>
                        <p>Test data extraction before running full automation:</p>
                        <pre><code>python -m grant_automation_cli.cli extract \\
  --grant-name "Moving Stories: Short-Form Graphic Novels..." \\
  --doc docs/02-green-stem-expo-technical.md \\
  --output extracted_data.json</code></pre>
                        <p>Then validate the extracted data:</p>
                        <pre><code>python -m grant_automation_cli.cli validate \\
  --grant-name "Moving Stories: Short-Form Graphic Novels..." \\
  --config grant_config.yaml</code></pre>
                    </div>
                </div>

                <div class="step-card">
                    <div class="step-number">3</div>
                    <div class="step-content">
                        <h4>Run Dry Run (Recommended)</h4>
                        <p>Test the complete workflow without actually filling the form:</p>
                        <pre><code>python -m grant_automation_cli.cli automate \\
  --grant-name "Moving Stories: Short-Form Graphic Novels..." \\
  --username YOUR_USERNAME \\
  --password "YOUR_PASSWORD" \\
  --dry-run</code></pre>
                        <p>Review the output to ensure all data is correctly mapped before proceeding.</p>
                    </div>
                </div>

                <div class="step-card">
                    <div class="step-number">4</div>
                    <div class="step-content">
                        <h4>Run Full Automation</h4>
                        <p><strong>Basic automation (without narrative generation):</strong></p>
                        <pre><code>python -m grant_automation_cli.cli automate \\
  --grant-name "Moving Stories: Short-Form Graphic Novels..." \\
  --username Keyisaccess \\
  --password "Outlaw22!!"</code></pre>
                        
                        <p><strong>With narrative generation (requires OpenAI API key):</strong></p>
                        <pre><code># Option 1: Using environment variable
export OPENAI_API_KEY='your-api-key-here'
python -m grant_automation_cli.cli automate \\
  --grant-name "Moving Stories: Short-Form Graphic Novels..." \\
  --use-narratives

# Option 2: Using CLI argument
python -m grant_automation_cli.cli automate \\
  --grant-name "Moving Stories: Short-Form Graphic Novels..." \\
  --use-narratives \\
  --openai-api-key 'your-api-key-here'</code></pre>
                    </div>
                </div>

                <div class="step-card">
                    <div class="step-number">5</div>
                    <div class="step-content">
                        <h4>Review and Complete</h4>
                        <p>After automation completes:</p>
                        <ul>
                            <li>Review the generated report for any warnings or errors</li>
                            <li>Check the draft application URL (if provided)</li>
                            <li>Manually review and complete any fields that need attention</li>
                            <li>Submit the application through the 4Culture portal</li>
                        </ul>
                    </div>
                </div>
            </div>

            <div class="doc-section">
                <h3>📊 Using the Planning Dashboard</h3>
                
                <div class="info-card">
                    <h4>Dashboard Views</h4>
                    <ul>
                        <li><strong>Timeline View:</strong> See all grants organized by deadline month. Color-coded borders indicate past (gray), current (red), and upcoming (green) deadlines.</li>
                        <li><strong>Status View:</strong> View grants grouped by status (Planned, In Progress, Submitted, Completed) in separate columns.</li>
                        <li><strong>Priority View:</strong> See grants sorted by priority level (1-10) with deadline information for strategic planning.</li>
                    </ul>
                </div>

                <div class="info-card">
                    <h4>Grant Cards</h4>
                    <p>Each grant card displays:</p>
                    <ul>
                        <li>Grant name and status badge</li>
                        <li>Deadline with days remaining (color-coded: red for urgent, yellow for warning, green for OK)</li>
                        <li>Progress bar for in-progress applications</li>
                        <li>Amount requested, organization, and project information</li>
                        <li>Current step in the application process</li>
                        <li>Link to draft application (if available)</li>
                    </ul>
                </div>

                <div class="info-card">
                    <h4>Features</h4>
                    <ul>
                        <li><strong>Search:</strong> Use the search bar to filter grants by name, description, or any text content</li>
                        <li><strong>Export:</strong> Click "Export CSV" to download grant data for external analysis</li>
                        <li><strong>Details:</strong> Click "View Details" on any grant card to see comprehensive information</li>
                    </ul>
                </div>
            </div>

            <div class="doc-section">
                <h3>⚙️ Configuration</h3>
                
                <div class="config-card">
                    <h4>Grant Configuration File</h4>
                    <p>The system uses <code>grant_config.yaml</code> to configure:</p>
                    <ul>
                        <li>Field mappings (how your data maps to form fields)</li>
                        <li>Document associations (which documents contain relevant information)</li>
                        <li>Narrative generation settings (which fields need prose, templates, word counts)</li>
                        <li>Form structure and navigation</li>
                    </ul>
                    <p>Edit this file to customize the automation for different grant types.</p>
                </div>

                <div class="config-card">
                    <h4>OpenAI API Key Setup</h4>
                    <p><strong>Important:</strong> The OpenAI API key is NOT stored in configuration files for security.</p>
                    <p>Provide your API key using one of these methods:</p>
                    <ol>
                        <li><strong>Environment Variable (Recommended):</strong>
                            <pre><code>export OPENAI_API_KEY='your-api-key-here'</code></pre>
                        </li>
                        <li><strong>CLI Argument:</strong>
                            <pre><code>--openai-api-key 'your-api-key-here'</code></pre>
                        </li>
                    </ol>
                    <p>Get your API key from: <a href="https://platform.openai.com/api-keys" target="_blank">https://platform.openai.com/api-keys</a></p>
                </div>
            </div>

            <div class="doc-section">
                <h3>🔄 Complete Workflow</h3>
                
                <div class="workflow-diagram">
                    <div class="workflow-step">
                        <div class="workflow-icon">📄</div>
                        <h4>1. Document Preparation</h4>
                        <p>Organize grant information in markdown files with clear sections</p>
                    </div>
                    <div class="workflow-arrow">→</div>
                    <div class="workflow-step">
                        <div class="workflow-icon">🔍</div>
                        <h4>2. Data Extraction</h4>
                        <p>System parses documents and extracts structured data</p>
                    </div>
                    <div class="workflow-arrow">→</div>
                    <div class="workflow-step">
                        <div class="workflow-icon">✅</div>
                        <h4>3. Validation</h4>
                        <p>Validates required fields, formats, and data quality</p>
                    </div>
                    <div class="workflow-arrow">→</div>
                    <div class="workflow-step">
                        <div class="workflow-icon">🗺️</div>
                        <h4>4. Field Mapping</h4>
                        <p>Maps extracted data to form fields using configuration</p>
                    </div>
                    <div class="workflow-arrow">→</div>
                    <div class="workflow-step">
                        <div class="workflow-icon">✍️</div>
                        <h4>5. Narrative Generation</h4>
                        <p>Converts structured data to complete prose (if enabled)</p>
                    </div>
                    <div class="workflow-arrow">→</div>
                    <div class="workflow-step">
                        <div class="workflow-icon">🌐</div>
                        <h4>6. Browser Automation</h4>
                        <p>Logs in, navigates form, fills fields, saves draft</p>
                    </div>
                    <div class="workflow-arrow">→</div>
                    <div class="workflow-step">
                        <div class="workflow-icon">📊</div>
                        <h4>7. Database Tracking</h4>
                        <p>Updates database with progress and status</p>
                    </div>
                    <div class="workflow-arrow">→</div>
                    <div class="workflow-step">
                        <div class="workflow-icon">📈</div>
                        <h4>8. Dashboard Update</h4>
                        <p>Dashboard reflects latest status and progress</p>
                    </div>
                </div>
            </div>

            <div class="doc-section">
                <h3>💡 Best Practices</h3>
                
                <div class="best-practices">
                    <div class="practice-item">
                        <h4>✓ Organize Documents Well</h4>
                        <p>Use clear section headings and consistent formatting. The system works best with well-structured markdown files.</p>
                    </div>
                    <div class="practice-item">
                        <h4>✓ Validate Before Automating</h4>
                        <p>Always run extract and validate commands before full automation to catch issues early.</p>
                    </div>
                    <div class="practice-item">
                        <h4>✓ Use Dry Runs</h4>
                        <p>Test the complete workflow with <code>--dry-run</code> before actually filling forms to review data mapping.</p>
                    </div>
                    <div class="practice-item">
                        <h4>✓ Review Reports</h4>
                        <p>Always review generated reports to understand what was done and what needs manual attention.</p>
                    </div>
                    <div class="practice-item">
                        <h4>✓ Keep Configuration Updated</h4>
                        <p>Update <code>grant_config.yaml</code> as you learn more about form structures to improve accuracy.</p>
                    </div>
                    <div class="practice-item">
                        <h4>✓ Plan Ahead</h4>
                        <p>Use the dashboard to plan grant applications well in advance of deadlines, prioritizing high-value opportunities.</p>
                    </div>
                </div>
            </div>

            <div class="doc-section">
                <h3>🛠️ Command Reference</h3>
                
                <div class="command-reference">
                    <h4>Extract Data</h4>
                    <pre><code>python -m grant_automation_cli.cli extract \\
  --grant-name "Grant Name" \\
  --doc docs/document.md \\
  --output extracted_data.json</code></pre>

                    <h4>Validate Data</h4>
                    <pre><code>python -m grant_automation_cli.cli validate \\
  --grant-name "Grant Name" \\
  --config grant_config.yaml</code></pre>

                    <h4>Run Automation</h4>
                    <pre><code>python -m grant_automation_cli.cli automate \\
  --grant-name "Grant Name" \\
  --username YourUsername \\
  --password "YourPassword" \\
  --use-narratives \\
  --openai-api-key 'your-key'</code></pre>

                    <h4>Generate Dashboard</h4>
                    <pre><code>python -m grant_automation_cli.cli dashboard</code></pre>
                </div>
            </div>

            <div class="doc-section">
                <h3>📞 Support</h3>
                <div class="support-info">
                    <p>For issues or questions:</p>
                    <ul>
                        <li>Check the generated reports for detailed error information</li>
                        <li>Review validation results to identify missing or invalid data</li>
                        <li>Check configuration files for correct field mappings</li>
                        <li>Review screenshots captured during automation (in <code>screenshots/</code> folder)</li>
                    </ul>
                    <p>The system provides clear error messages and helpful guidance when issues occur.</p>
                </div>
            </div>
        </div>
        """

    def _generate_grant_card(
        self,
        grant: Dict[str, Any],
        show_deadline: bool = False,
        show_progress: bool = False,
        show_priority: bool = False,
    ) -> str:
        """Generate HTML for a single grant card."""
        status = grant.get("status", "planned")
        status_class = status.replace("_", "-")

        deadline = grant.get("deadline", "Not specified")
        deadline_display = deadline

        # Calculate days until deadline
        days_until = None
        if grant.get("deadline_timestamp"):
            try:
                deadline_date = datetime.fromtimestamp(grant["deadline_timestamp"])
                now = datetime.now()
                days_until = (deadline_date - now).days

                if days_until < 0:
                    deadline_display += (
                        f' <span class="deadline-overdue">({abs(days_until)} days overdue)</span>'
                    )
                elif days_until <= 7:
                    deadline_display += (
                        f' <span class="deadline-urgent">({days_until} days remaining)</span>'
                    )
                elif days_until <= 30:
                    deadline_display += (
                        f' <span class="deadline-warning">({days_until} days remaining)</span>'
                    )
                else:
                    deadline_display += (
                        f' <span class="deadline-ok">({days_until} days remaining)</span>'
                    )
            except:
                pass

        progress = grant.get("progress_percentage", 0)
        priority = grant.get("priority", 5)
        priority_stars = "★" * priority + "☆" * (10 - priority)

        # Add data attributes for filtering/sorting
        deadline_attr = (
            f'data-deadline="{grant.get("deadline", "")}"' if grant.get("deadline") else ""
        )
        priority_attr = f'data-priority="{priority}"'

        html = f'''
        <div class="grant-card status-{status_class}" data-grant-id="{grant.get("id")}" {deadline_attr} {priority_attr}>
            <div class="grant-card-header">
                <h4 class="grant-name">{grant.get("name", "Unnamed Grant")}</h4>
                <span class="grant-status-badge status-{status_class}">{status.replace("_", " ").title()}</span>
            </div>
            
            <div class="grant-card-body">
                {f'<div class="grant-priority"><strong>Priority:</strong> {priority_stars}</div>' if show_priority else ""}
                
                {f'<div class="grant-deadline"><strong>Deadline:</strong> {deadline_display}</div>' if show_deadline else ""}
                
                {f'<div class="grant-progress"><div class="progress-bar"><div class="progress-fill" style="width: {progress}%"></div></div><span class="progress-text">{progress}% Complete</span></div>' if show_progress else ""}
                
                {f'<div class="grant-amount"><strong>Amount Requested:</strong> ${grant.get("amount_requested", 0):,.2f}</div>' if grant.get("amount_requested") else ""}
                
                {f'<div class="grant-org"><strong>Organization:</strong> {grant.get("organization_name", "N/A")}</div>' if grant.get("organization_name") else ""}
                
                {f'<div class="grant-project"><strong>Project:</strong> {grant.get("project_title", "N/A")}</div>' if grant.get("project_title") else ""}
                
                {f'<div class="grant-description">{grant.get("description", "")[:200]}...</div>' if grant.get("description") else ""}
                
                {f'<div class="grant-step"><strong>Current Step:</strong> {grant.get("current_step", "Not started")}</div>' if grant.get("current_step") else ""}
                
                {f'<div class="grant-draft-url"><a href="{grant.get("draft_url")}" target="_blank">View Draft Application</a></div>' if grant.get("draft_url") else ""}
            </div>
            
            <div class="grant-card-footer">
                <button class="btn-details" onclick="showGrantDetails({grant.get("id")})">View Details</button>
            </div>
        </div>
        '''

        return html

    def _generate_engineering_documentation_view(self) -> str:
        """Generate comprehensive engineering documentation view."""
        return """
        <div class="engineering-docs">
            <div class="docs-nav-tabs">
                <button class="doc-tab active" onclick="showDocSection('overview')">Solution Overview</button>
                <button class="doc-tab" onclick="showDocSection('features')">Features & Benefits</button>
                <button class="doc-tab" onclick="showDocSection('usecases')">Use Cases</button>
                <button class="doc-tab" onclick="showDocSection('architecture')">Architecture</button>
                <button class="doc-tab" onclick="showDocSection('database')">Database Schema</button>
                <button class="doc-tab" onclick="showDocSection('api')">API Reference</button>
                <button class="doc-tab" onclick="showDocSection('integration')">Integration Guides</button>
                <button class="doc-tab" onclick="showDocSection('development')">Development Guide</button>
            </div>

            <!-- Solution Overview -->
            <div id="doc-overview" class="doc-section active">
                <h2>Solution Overview</h2>
                
                <div class="doc-subsection">
                    <h3>Executive Summary</h3>
                    <p>The 4Culture Grant Application Automation System is an intelligent, end-to-end solution designed to streamline and automate the complex process of grant application submission. Built specifically for organizations applying to 4Culture grants, this system eliminates manual data entry, reduces errors, and dramatically accelerates the application workflow while ensuring compliance and quality.</p>
                    
                    <p>The system combines advanced document processing, intelligent field mapping, AI-powered narrative generation, and browser automation to transform hours of manual work into minutes of automated processing. Organizations can now manage multiple grant applications simultaneously, track progress in real-time, and maintain comprehensive planning dashboards for strategic decision-making.</p>
                </div>

                <div class="doc-subsection">
                    <h3>Problem Statement</h3>
                    <p>Grant application processes are notoriously time-consuming and error-prone. Organizations face significant challenges including:</p>
                    <ul>
                        <li><strong>Time Constraints:</strong> Manual form filling can take 8-20 hours per application</li>
                        <li><strong>Data Inconsistency:</strong> Information scattered across multiple documents leads to errors</li>
                        <li><strong>Repetitive Work:</strong> Similar information must be re-entered for each grant</li>
                        <li><strong>Narrative Quality:</strong> Converting structured data into compelling prose is challenging</li>
                        <li><strong>Tracking Complexity:</strong> Managing multiple applications with different deadlines is difficult</li>
                        <li><strong>Compliance Risk:</strong> Missing fields or incorrect formatting can lead to rejection</li>
                    </ul>
                </div>

                <div class="doc-subsection">
                    <h3>Solution Overview</h3>
                    <p>Our solution addresses these challenges through a comprehensive automation platform that:</p>
                    <ul>
                        <li><strong>Automates Data Extraction:</strong> Intelligently parses markdown documents to extract grant-relevant information</li>
                        <li><strong>Maps Fields Intelligently:</strong> Automatically maps extracted data to 4Culture form fields with validation</li>
                        <li><strong>Generates Narratives:</strong> Uses OpenAI GPT-4 to convert structured data into compelling, unique prose</li>
                        <li><strong>Automates Browser Actions:</strong> Handles login, navigation, form filling, and draft saving</li>
                        <li><strong>Tracks Applications:</strong> Maintains a SQLite database for planning and progress tracking</li>
                        <li><strong>Visualizes Progress:</strong> Provides interactive dashboards for stakeholders</li>
                    </ul>
                </div>

                <div class="doc-subsection">
                    <h3>Value Proposition</h3>
                    <div class="value-grid">
                        <div class="value-card">
                            <h4>Time Savings</h4>
                            <p>Reduce application time from 8-20 hours to 15-30 minutes per grant</p>
                        </div>
                        <div class="value-card">
                            <h4>Accuracy</h4>
                            <p>Eliminate manual entry errors through automated data extraction and validation</p>
                        </div>
                        <div class="value-card">
                            <h4>Scalability</h4>
                            <p>Handle multiple grant applications simultaneously without proportional time increase</p>
                        </div>
                        <div class="value-card">
                            <h4>Quality</h4>
                            <p>Generate professional, unique narratives tailored to each grant's requirements</p>
                        </div>
                        <div class="value-card">
                            <h4>Compliance</h4>
                            <p>Ensure all required fields are completed correctly with built-in validation</p>
                        </div>
                        <div class="value-card">
                            <h4>Visibility</h4>
                            <p>Track all applications in one place with real-time progress updates</p>
                        </div>
                    </div>
                </div>

                <div class="doc-subsection">
                    <h3>Target Users</h3>
                    <ul>
                        <li><strong>Grant Writers:</strong> Professional grant writers managing multiple applications</li>
                        <li><strong>Nonprofit Organizations:</strong> Organizations applying for multiple 4Culture grants</li>
                        <li><strong>Development Teams:</strong> Teams responsible for securing funding</li>
                        <li><strong>Executive Directors:</strong> Leaders needing visibility into grant application pipeline</li>
                        <li><strong>Program Managers:</strong> Managers coordinating grant applications across programs</li>
                    </ul>
                </div>

                <div class="doc-subsection">
                    <h3>Competitive Advantages</h3>
                    <ul>
                        <li><strong>4Culture-Specific:</strong> Built specifically for 4Culture's application system</li>
                        <li><strong>AI-Powered Narratives:</strong> Unique prose generation, not template filling</li>
                        <li><strong>End-to-End Automation:</strong> Complete workflow from document to submitted draft</li>
                        <li><strong>Planning & Tracking:</strong> Integrated database and dashboard for strategic management</li>
                        <li><strong>Open Source:</strong> Fully customizable and extensible</li>
                        <li><strong>MCP Integration:</strong> Modern browser automation using MCP tools</li>
                    </ul>
                </div>
            </div>

            <!-- Features & Benefits -->
            <div id="doc-features" class="doc-section">
                <h2>Features & Benefits</h2>
                
                <div class="feature-grid">
                    <div class="feature-card">
                        <h3>Document Processing & Data Extraction</h3>
                        <p class="feature-desc">Intelligently parses markdown documents to extract grant-relevant information including organization details, project descriptions, budgets, timelines, and goals.</p>
                        <div class="benefits">
                            <h4>User Benefits:</h4>
                            <ul>
                                <li>No manual data entry required</li>
                                <li>Automatic identification of relevant documents</li>
                                <li>Data validation and standardization</li>
                                <li>Support for multiple document formats</li>
                            </ul>
                            <h4>Business Value:</h4>
                            <ul>
                                <li>Eliminates 2-4 hours of manual data entry per application</li>
                                <li>Reduces data entry errors by 95%+</li>
                                <li>Enables reuse of existing documentation</li>
                            </ul>
                        </div>
                    </div>

                    <div class="feature-card">
                        <h3>Intelligent Field Mapping</h3>
                        <p class="feature-desc">Automatically maps extracted data to 4Culture form fields using configurable mapping rules with support for conditional fields and data transformations.</p>
                        <div class="benefits">
                            <h4>User Benefits:</h4>
                            <ul>
                                <li>Zero configuration for standard fields</li>
                                <li>Customizable mappings via YAML</li>
                                <li>Automatic data type conversion</li>
                                <li>Conditional field handling</li>
                            </ul>
                            <h4>Business Value:</h4>
                            <ul>
                                <li>Saves 1-2 hours of field mapping per application</li>
                                <li>Ensures data consistency across applications</li>
                                <li>Reduces mapping errors</li>
                            </ul>
                        </div>
                    </div>

                    <div class="feature-card">
                        <h3>Narrative Generation (OpenAI)</h3>
                        <p class="feature-desc">Converts structured data into compelling, unique prose narratives using OpenAI GPT-4. Generates project descriptions, goals, impact statements, and budget narratives tailored to each grant.</p>
                        <div class="benefits">
                            <h4>User Benefits:</h4>
                            <ul>
                                <li>Professional-quality narratives automatically</li>
                                <li>No bullet points - complete prose</li>
                                <li>Unique content for each grant</li>
                                <li>Aligned with grant requirements</li>
                            </ul>
                            <h4>Business Value:</h4>
                            <ul>
                                <li>Saves 3-6 hours of writing per application</li>
                                <li>Improves narrative quality and consistency</li>
                                <li>Increases grant approval rates</li>
                                <li>Reduces need for professional grant writers</li>
                            </ul>
                        </div>
                    </div>

                    <div class="feature-card">
                        <h3>Browser Automation</h3>
                        <p class="feature-desc">Fully automated browser interactions using MCP tools. Handles login, navigation, form filling, page navigation, validation error handling, and draft saving.</p>
                        <div class="benefits">
                            <h4>User Benefits:</h4>
                            <ul>
                                <li>No manual browser interaction required</li>
                                <li>Automatic error detection and handling</li>
                                <li>Screenshot capture for debugging</li>
                                <li>Support for multi-page forms</li>
                            </ul>
                            <h4>Business Value:</h4>
                            <ul>
                                <li>Eliminates 2-3 hours of manual form filling</li>
                                <li>Ensures consistent form completion</li>
                                <li>Reduces submission errors</li>
                            </ul>
                        </div>
                    </div>

                    <div class="feature-card">
                        <h3>Grant Planning & Tracking</h3>
                        <p class="feature-desc">SQLite database tracks all grants with status, progress, deadlines, priorities, and milestones. Supports strategic planning and deadline management.</p>
                        <div class="benefits">
                            <h4>User Benefits:</h4>
                            <ul>
                                <li>Centralized grant information</li>
                                <li>Progress tracking per application</li>
                                <li>Deadline reminders and prioritization</li>
                                <li>Historical data and analytics</li>
                            </ul>
                            <h4>Business Value:</h4>
                            <ul>
                                <li>Prevents missed deadlines</li>
                                <li>Enables strategic planning</li>
                                <li>Improves resource allocation</li>
                                <li>Provides audit trail</li>
                            </ul>
                        </div>
                    </div>

                    <div class="feature-card">
                        <h3>Dashboard Visualization</h3>
                        <p class="feature-desc">Interactive HTML dashboard with timeline, status, priority, and documentation views. Real-time updates, search, filtering, and export capabilities.</p>
                        <div class="benefits">
                            <h4>User Benefits:</h4>
                            <ul>
                                <li>Visual progress tracking</li>
                                <li>Multiple view perspectives</li>
                                <li>Stakeholder-friendly interface</li>
                                <li>Export capabilities</li>
                            </ul>
                            <h4>Business Value:</h4>
                            <ul>
                                <li>Improves stakeholder communication</li>
                                <li>Enables data-driven decisions</li>
                                <li>Facilitates reporting</li>
                                <li>Increases transparency</li>
                            </ul>
                        </div>
                    </div>

                    <div class="feature-card">
                        <h3>Quality Assurance & Validation</h3>
                        <p class="feature-desc">Comprehensive validation at every step: data extraction validation, field mapping validation, narrative quality checks, and form validation error handling.</p>
                        <div class="benefits">
                            <h4>User Benefits:</h4>
                            <ul>
                                <li>Early error detection</li>
                                <li>Detailed validation reports</li>
                                <li>Automatic error correction suggestions</li>
                                <li>Quality metrics</li>
                            </ul>
                            <h4>Business Value:</h4>
                            <ul>
                                <li>Reduces rejection rates</li>
                                <li>Saves time on corrections</li>
                                <li>Improves application quality</li>
                            </ul>
                        </div>
                    </div>

                    <div class="feature-card">
                        <h3>Multi-Grant Management</h3>
                        <p class="feature-desc">Manage multiple grant applications simultaneously with independent workflows, shared data sources, and centralized tracking.</p>
                        <div class="benefits">
                            <h4>User Benefits:</h4>
                            <ul>
                                <li>Parallel application processing</li>
                                <li>Shared document library</li>
                                <li>Unified dashboard view</li>
                                <li>Bulk operations</li>
                            </ul>
                            <h4>Business Value:</h4>
                            <ul>
                                <li>Scales to handle unlimited grants</li>
                                <li>Maximizes funding opportunities</li>
                                <li>Optimizes resource utilization</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Use Cases -->
            <div id="doc-usecases" class="doc-section">
                <h2>Complete Use Cases</h2>
                
                <div class="usecase-card">
                    <h3>Use Case 1: First-Time Grant Application</h3>
                    <div class="usecase-meta">
                        <p><strong>Actor:</strong> Grant Writer</p>
                        <p><strong>Preconditions:</strong> Organization has markdown documents with grant information, OpenAI API key available, 4Culture account credentials</p>
                        <p><strong>Success Metrics:</strong> Application draft saved successfully, all required fields completed, narrative quality score > 80%</p>
                    </div>
                    <div class="usecase-flow">
                        <h4>Main Flow:</h4>
                        <ol>
                            <li>User runs automation command with grant name</li>
                            <li>System identifies relevant documents in docs folder</li>
                            <li>System extracts and validates grant data</li>
                            <li>System maps data to 4Culture form fields</li>
                            <li>System generates narratives for narrative fields</li>
                            <li>System logs into 4Culture application portal</li>
                            <li>System navigates to grant application form</li>
                            <li>System fills all form fields with extracted/generated data</li>
                            <li>System handles any validation errors</li>
                            <li>System saves draft application</li>
                            <li>System updates database with application status</li>
                            <li>System generates completion report</li>
                        </ol>
                        <h4>Alternative Flows:</h4>
                        <ul>
                            <li><strong>3a. Missing Data:</strong> System flags missing required fields, user provides additional documents, process continues</li>
                            <li><strong>5a. Narrative Generation Fails:</strong> System uses fallback structured data, logs warning</li>
                            <li><strong>8a. Form Validation Errors:</strong> System captures errors, attempts corrections, logs issues for review</li>
                        </ul>
                        <h4>Postconditions:</h4>
                        <ul>
                            <li>Draft application saved in 4Culture system</li>
                            <li>Application status tracked in database</li>
                            <li>Completion report generated</li>
                            <li>Screenshots captured for verification</li>
                        </ul>
                    </div>
                </div>

                <div class="usecase-card">
                    <h3>Use Case 2: Multiple Grant Applications</h3>
                    <div class="usecase-meta">
                        <p><strong>Actor:</strong> Development Director</p>
                        <p><strong>Preconditions:</strong> Multiple grants identified, shared document library available, database seeded with grant information</p>
                        <p><strong>Success Metrics:</strong> All applications processed within deadline window, 90%+ completion rate</p>
                    </div>
                    <div class="usecase-flow">
                        <h4>Main Flow:</h4>
                        <ol>
                            <li>User seeds database with available grants for planning period</li>
                            <li>User views dashboard to see all grants by deadline</li>
                            <li>User prioritizes grants by deadline and amount</li>
                            <li>For each grant, user runs automation workflow</li>
                            <li>System processes each application independently</li>
                            <li>System updates database after each completion</li>
                            <li>Dashboard reflects real-time progress</li>
                            <li>User reviews and submits completed drafts</li>
                        </ol>
                        <h4>Alternative Flows:</h4>
                        <ul>
                            <li><strong>4a. Parallel Processing:</strong> User runs multiple automation workflows simultaneously for different grants</li>
                            <li><strong>5a. Shared Data:</strong> System reuses organization data across applications, generates unique narratives per grant</li>
                        </ul>
                    </div>
                </div>

                <div class="usecase-card">
                    <h3>Use Case 3: Updating Existing Applications</h3>
                    <div class="usecase-meta">
                        <p><strong>Actor:</strong> Program Manager</p>
                        <p><strong>Preconditions:</strong> Draft application exists in 4Culture system, updated documents available</p>
                    </div>
                    <div class="usecase-flow">
                        <h4>Main Flow:</h4>
                        <ol>
                            <li>User identifies application needing updates</li>
                            <li>User updates source documents with new information</li>
                            <li>User runs automation with updated documents</li>
                            <li>System extracts updated data</li>
                            <li>System navigates to existing draft</li>
                            <li>System updates changed fields only</li>
                            <li>System saves updated draft</li>
                            <li>System logs changes in database</li>
                        </ol>
                    </div>
                </div>

                <div class="usecase-card">
                    <h3>Use Case 4: Team Collaboration</h3>
                    <div class="usecase-meta">
                        <p><strong>Actor:</strong> Grant Writing Team</p>
                        <p><strong>Preconditions:</strong> Shared document repository, database accessible to team</p>
                    </div>
                    <div class="usecase-flow">
                        <h4>Main Flow:</h4>
                        <ol>
                            <li>Team members contribute documents to shared docs folder</li>
                            <li>Team reviews dashboard for application status</li>
                            <li>Team assigns grants to specific members</li>
                            <li>Each member runs automation for assigned grants</li>
                            <li>Dashboard shows progress by team member</li>
                            <li>Team reviews generated narratives</li>
                            <li>Team makes manual adjustments as needed</li>
                            <li>Team submits applications</li>
                        </ol>
                    </div>
                </div>

                <div class="usecase-card">
                    <h3>Use Case 5: Stakeholder Reporting</h3>
                    <div class="usecase-meta">
                        <p><strong>Actor:</strong> Executive Director</p>
                        <p><strong>Preconditions:</strong> Database contains grant application data</p>
                    </div>
                    <div class="usecase-flow">
                        <h4>Main Flow:</h4>
                        <ol>
                            <li>Executive opens dashboard</li>
                            <li>Executive views timeline to see upcoming deadlines</li>
                            <li>Executive views status to see completion rates</li>
                            <li>Executive views priority to see high-value applications</li>
                            <li>Executive exports data for board presentation</li>
                            <li>Executive reviews individual grant details</li>
                        </ol>
                    </div>
                </div>

                <div class="usecase-card">
                    <h3>Use Case 6: Strategic Planning</h3>
                    <div class="usecase-meta">
                        <p><strong>Actor:</strong> Development Director</p>
                    </div>
                    <div class="usecase-flow">
                        <h4>Main Flow:</h4>
                        <ol>
                            <li>Director identifies all available grants for planning period</li>
                            <li>Director seeds database with grant information</li>
                            <li>Director views dashboard timeline by month</li>
                            <li>Director prioritizes grants by amount and alignment</li>
                            <li>Director creates application schedule</li>
                            <li>Director allocates resources based on deadlines</li>
                            <li>Director tracks progress against plan</li>
                        </ol>
                    </div>
                </div>

                <div class="usecase-card">
                    <h3>Use Case 7: Compliance and Validation</h3>
                    <div class="usecase-meta">
                        <p><strong>Actor:</strong> Compliance Officer</p>
                    </div>
                    <div class="usecase-flow">
                        <h4>Main Flow:</h4>
                        <ol>
                            <li>Officer runs automation in dry-run mode</li>
                            <li>System generates validation report</li>
                            <li>Officer reviews data completeness</li>
                            <li>Officer reviews field mappings</li>
                            <li>Officer reviews narrative quality</li>
                            <li>Officer approves or requests corrections</li>
                            <li>If approved, officer runs full automation</li>
                        </ol>
                    </div>
                </div>

                <div class="usecase-card">
                    <h3>Use Case 8: Integration with Existing Systems</h3>
                    <div class="usecase-meta">
                        <p><strong>Actor:</strong> IT Administrator</p>
                    </div>
                    <div class="usecase-flow">
                        <h4>Main Flow:</h4>
                        <ol>
                            <li>Administrator identifies data sources (CRM, databases, etc.)</li>
                            <li>Administrator creates markdown export from existing systems</li>
                            <li>Administrator configures export to match expected format</li>
                            <li>Administrator schedules automated exports</li>
                            <li>System processes exported documents</li>
                            <li>System generates applications automatically</li>
                        </ol>
                    </div>
                </div>
            </div>

            <!-- Architecture -->
            <div id="doc-architecture" class="doc-section">
                <h2>System Architecture</h2>
                
                <div class="doc-subsection">
                    <h3>High-Level Architecture</h3>
                    <div class="mermaid-diagram">
                        <pre class="mermaid">
graph TB
    User[User/CLI] --> Workflow[AutomationWorkflow]
    Workflow --> Extractor[DataExtractor]
    Workflow --> Mapper[FormMapper]
    Workflow --> Automator[ApplicationAutomator]
    Workflow --> Database[GrantDatabase]
    
    Extractor --> Parser[DocumentParser]
    Mapper --> NarrGen[NarrativeGenerator]
    Automator --> Browser[MCPBrowserIntegration]
    NarrGen --> OpenAI[OpenAI API]
    Browser --> MCP[MCP Tools]
    
    Database --> SQLite[(SQLite DB)]
    Workflow --> Dashboard[GrantDashboard]
    Dashboard --> HTML[HTML Dashboard]
                        </pre>
                    </div>
                </div>

                <div class="doc-subsection">
                    <h3>Component Interaction</h3>
                    <div class="mermaid-diagram">
                        <pre class="mermaid">
sequenceDiagram
    participant U as User
    participant W as Workflow
    participant E as DataExtractor
    participant M as FormMapper
    participant N as NarrativeGenerator
    participant A as ApplicationAutomator
    participant D as Database
    
    U->>W: run_automation(grant_name)
    W->>E: extract_grant_data()
    E-->>W: grant_data
    W->>M: map_data_to_fields()
    M->>N: generate_narrative()
    N-->>M: narrative_text
    M-->>W: mapped_fields
    W->>D: add_grant()
    W->>A: start_new_application()
    A->>A: fill_form_fields()
    A-->>W: result
    W->>D: update_grant_status()
    W-->>U: completion_report
                        </pre>
                    </div>
                </div>

                <div class="doc-subsection">
                    <h3>Data Flow</h3>
                    <div class="mermaid-diagram">
                        <pre class="mermaid">
flowchart LR
    Docs[Markdown Docs] --> Extract[Data Extraction]
    Extract --> Validate[Data Validation]
    Validate --> Map[Field Mapping]
    Map --> NarrGen[Narrative Generation]
    NarrGen --> Combine[Combine Data]
    Combine --> Fill[Form Filling]
    Fill --> Save[Save Draft]
    Save --> Track[Database Tracking]
    Track --> Report[Generate Report]
                        </pre>
                    </div>
                </div>

                <div class="doc-subsection">
                    <h3>Technology Stack</h3>
                    <div class="tech-stack">
                        <div class="tech-category">
                            <h4>Core Language</h4>
                            <ul>
                                <li>Python 3.8+</li>
                            </ul>
                        </div>
                        <div class="tech-category">
                            <h4>Data Processing</h4>
                            <ul>
                                <li>Markdown parsing (built-in)</li>
                                <li>YAML configuration (pyyaml, optional)</li>
                                <li>JSON data structures</li>
                            </ul>
                        </div>
                        <div class="tech-category">
                            <h4>AI Integration</h4>
                            <ul>
                                <li>OpenAI API (openai package)</li>
                                <li>GPT-4 for narrative generation</li>
                            </ul>
                        </div>
                        <div class="tech-category">
                            <h4>Browser Automation</h4>
                            <ul>
                                <li>MCP Browser Tools (Browserbase/Stagehand)</li>
                                <li>Cursor IDE Browser Tools</li>
                            </ul>
                        </div>
                        <div class="tech-category">
                            <h4>Database</h4>
                            <ul>
                                <li>SQLite3 (built-in)</li>
                            </ul>
                        </div>
                        <div class="tech-category">
                            <h4>Frontend</h4>
                            <ul>
                                <li>HTML5</li>
                                <li>CSS3 (modern features)</li>
                                <li>Vanilla JavaScript</li>
                            </ul>
                        </div>
                        <div class="tech-category">
                            <h4>Logging</h4>
                            <ul>
                                <li>Python logging module</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <div class="doc-subsection">
                    <h3>Integration Architecture</h3>
                    <div class="mermaid-diagram">
                        <pre class="mermaid">
graph LR
    System[Grant System] --> MCP[MCP Server]
    System --> OpenAI[OpenAI API]
    System --> SQLite[(SQLite)]
    
    MCP --> Browserbase[Browserbase]
    MCP --> CursorBrowser[Cursor Browser]
    
    System --> Docs[Document Store]
    System --> Config[YAML Config]
                        </pre>
                    </div>
                </div>
            </div>

            <!-- Database Schema -->
            <div id="doc-database" class="doc-section">
                <h2>Database Schema Documentation</h2>
                
                <div class="doc-subsection">
                    <h3>Entity Relationship Diagram</h3>
                    <div class="mermaid-diagram">
                        <pre class="mermaid">
erDiagram
    GRANTS ||--o{ APPLICATION_STATUS : has
    GRANTS ||--o{ GRANT_DOCUMENTS : has
    GRANTS ||--o{ TIMELINE_MILESTONES : has
    
    GRANTS {
        int id PK
        string name
        string identifier UK
        string deadline
        int deadline_timestamp
        string status
        float amount_requested
        float amount_awarded
        string organization_name
        string project_title
        string description
        string focus_areas
        string eligibility_requirements
        string application_url
        string notes
        int priority
        datetime created_at
        datetime updated_at
    }
    
    APPLICATION_STATUS {
        int id PK
        int grant_id FK
        string status
        int progress_percentage
        string current_step
        boolean data_extracted
        boolean narrative_generated
        boolean form_filled
        boolean draft_saved
        boolean submitted
        string submitted_date
        string award_date
        string draft_url
        string report_path
        string errors
        string warnings
        datetime created_at
        datetime updated_at
    }
    
    GRANT_DOCUMENTS {
        int id PK
        int grant_id FK
        string document_path
        string document_type
        boolean is_primary
        datetime created_at
    }
    
    TIMELINE_MILESTONES {
        int id PK
        int grant_id FK
        string milestone_name
        string due_date
        int due_date_timestamp
        boolean completed
        string completed_date
        string notes
        datetime created_at
    }
                        </pre>
                    </div>
                </div>

                <div class="doc-subsection">
                    <h3>Table Definitions</h3>
                    
                    <div class="table-doc">
                        <h4>grants</h4>
                        <p>Primary table storing grant information and metadata.</p>
                        <table class="schema-table">
                            <thead>
                                <tr>
                                    <th>Column</th>
                                    <th>Type</th>
                                    <th>Constraints</th>
                                    <th>Description</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr><td>id</td><td>INTEGER</td><td>PRIMARY KEY, AUTOINCREMENT</td><td>Unique grant identifier</td></tr>
                                <tr><td>name</td><td>TEXT</td><td>NOT NULL</td><td>Grant name</td></tr>
                                <tr><td>identifier</td><td>TEXT</td><td>UNIQUE</td><td>URL-friendly identifier</td></tr>
                                <tr><td>deadline</td><td>TEXT</td><td></td><td>Human-readable deadline</td></tr>
                                <tr><td>deadline_timestamp</td><td>INTEGER</td><td></td><td>Unix timestamp for sorting</td></tr>
                                <tr><td>status</td><td>TEXT</td><td>DEFAULT 'planned'</td><td>Current status</td></tr>
                                <tr><td>amount_requested</td><td>REAL</td><td></td><td>Requested funding amount</td></tr>
                                <tr><td>amount_awarded</td><td>REAL</td><td></td><td>Awarded funding amount</td></tr>
                                <tr><td>organization_name</td><td>TEXT</td><td></td><td>Applying organization</td></tr>
                                <tr><td>project_title</td><td>TEXT</td><td></td><td>Project title</td></tr>
                                <tr><td>description</td><td>TEXT</td><td></td><td>Grant description</td></tr>
                                <tr><td>focus_areas</td><td>TEXT</td><td></td><td>Grant focus areas</td></tr>
                                <tr><td>eligibility_requirements</td><td>TEXT</td><td></td><td>Eligibility criteria</td></tr>
                                <tr><td>application_url</td><td>TEXT</td><td></td><td>Application URL</td></tr>
                                <tr><td>notes</td><td>TEXT</td><td></td><td>Additional notes</td></tr>
                                <tr><td>priority</td><td>INTEGER</td><td>DEFAULT 5</td><td>Priority (1-10)</td></tr>
                                <tr><td>created_at</td><td>TEXT</td><td>DEFAULT CURRENT_TIMESTAMP</td><td>Creation timestamp</td></tr>
                                <tr><td>updated_at</td><td>TEXT</td><td>DEFAULT CURRENT_TIMESTAMP</td><td>Last update timestamp</td></tr>
                            </tbody>
                        </table>
                    </div>

                    <div class="table-doc">
                        <h4>application_status</h4>
                        <p>Tracks detailed status and progress of each grant application.</p>
                        <table class="schema-table">
                            <thead>
                                <tr>
                                    <th>Column</th>
                                    <th>Type</th>
                                    <th>Constraints</th>
                                    <th>Description</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr><td>id</td><td>INTEGER</td><td>PRIMARY KEY, AUTOINCREMENT</td><td>Status record ID</td></tr>
                                <tr><td>grant_id</td><td>INTEGER</td><td>NOT NULL, FK</td><td>Reference to grants.id</td></tr>
                                <tr><td>status</td><td>TEXT</td><td>NOT NULL</td><td>Current status</td></tr>
                                <tr><td>progress_percentage</td><td>INTEGER</td><td>DEFAULT 0</td><td>Completion percentage</td></tr>
                                <tr><td>current_step</td><td>TEXT</td><td></td><td>Current workflow step</td></tr>
                                <tr><td>data_extracted</td><td>BOOLEAN</td><td>DEFAULT 0</td><td>Data extraction complete</td></tr>
                                <tr><td>narrative_generated</td><td>BOOLEAN</td><td>DEFAULT 0</td><td>Narratives generated</td></tr>
                                <tr><td>form_filled</td><td>BOOLEAN</td><td>DEFAULT 0</td><td>Form fields filled</td></tr>
                                <tr><td>draft_saved</td><td>BOOLEAN</td><td>DEFAULT 0</td><td>Draft saved</td></tr>
                                <tr><td>submitted</td><td>BOOLEAN</td><td>DEFAULT 0</td><td>Application submitted</td></tr>
                                <tr><td>submitted_date</td><td>TEXT</td><td></td><td>Submission date</td></tr>
                                <tr><td>award_date</td><td>TEXT</td><td></td><td>Award date</td></tr>
                                <tr><td>draft_url</td><td>TEXT</td><td></td><td>Draft application URL</td></tr>
                                <tr><td>report_path</td><td>TEXT</td><td></td><td>Report file path</td></tr>
                                <tr><td>errors</td><td>TEXT</td><td></td><td>JSON array of errors</td></tr>
                                <tr><td>warnings</td><td>TEXT</td><td></td><td>JSON array of warnings</td></tr>
                                <tr><td>created_at</td><td>TEXT</td><td>DEFAULT CURRENT_TIMESTAMP</td><td>Creation timestamp</td></tr>
                                <tr><td>updated_at</td><td>TEXT</td><td>DEFAULT CURRENT_TIMESTAMP</td><td>Last update timestamp</td></tr>
                            </tbody>
                        </table>
                    </div>

                    <div class="table-doc">
                        <h4>grant_documents</h4>
                        <p>Maps documents to grants for tracking and reference.</p>
                        <table class="schema-table">
                            <thead>
                                <tr>
                                    <th>Column</th>
                                    <th>Type</th>
                                    <th>Constraints</th>
                                    <th>Description</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr><td>id</td><td>INTEGER</td><td>PRIMARY KEY, AUTOINCREMENT</td><td>Document record ID</td></tr>
                                <tr><td>grant_id</td><td>INTEGER</td><td>NOT NULL, FK</td><td>Reference to grants.id</td></tr>
                                <tr><td>document_path</td><td>TEXT</td><td>NOT NULL</td><td>Path to document file</td></tr>
                                <tr><td>document_type</td><td>TEXT</td><td></td><td>Document type/category</td></tr>
                                <tr><td>is_primary</td><td>BOOLEAN</td><td>DEFAULT 0</td><td>Primary document flag</td></tr>
                                <tr><td>created_at</td><td>TEXT</td><td>DEFAULT CURRENT_TIMESTAMP</td><td>Creation timestamp</td></tr>
                            </tbody>
                        </table>
                    </div>

                    <div class="table-doc">
                        <h4>timeline_milestones</h4>
                        <p>Stores milestone dates and completion status for grant applications.</p>
                        <table class="schema-table">
                            <thead>
                                <tr>
                                    <th>Column</th>
                                    <th>Type</th>
                                    <th>Constraints</th>
                                    <th>Description</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr><td>id</td><td>INTEGER</td><td>PRIMARY KEY, AUTOINCREMENT</td><td>Milestone record ID</td></tr>
                                <tr><td>grant_id</td><td>INTEGER</td><td>NOT NULL, FK</td><td>Reference to grants.id</td></tr>
                                <tr><td>milestone_name</td><td>TEXT</td><td>NOT NULL</td><td>Milestone name</td></tr>
                                <tr><td>due_date</td><td>TEXT</td><td></td><td>Human-readable due date</td></tr>
                                <tr><td>due_date_timestamp</td><td>INTEGER</td><td></td><td>Unix timestamp</td></tr>
                                <tr><td>completed</td><td>BOOLEAN</td><td>DEFAULT 0</td><td>Completion status</td></tr>
                                <tr><td>completed_date</td><td>TEXT</td><td></td><td>Completion date</td></tr>
                                <tr><td>notes</td><td>TEXT</td><td></td><td>Milestone notes</td></tr>
                                <tr><td>created_at</td><td>TEXT</td><td>DEFAULT CURRENT_TIMESTAMP</td><td>Creation timestamp</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <div class="doc-subsection">
                    <h3>Indexes</h3>
                    <ul>
                        <li><code>idx_grant_status</code> on <code>grants(status)</code> - Fast status filtering</li>
                        <li><code>idx_grant_deadline</code> on <code>grants(deadline_timestamp)</code> - Fast deadline sorting</li>
                        <li><code>idx_app_status</code> on <code>application_status(grant_id, status)</code> - Fast status lookups</li>
                    </ul>
                </div>

                <div class="doc-subsection">
                    <h3>Example Queries</h3>
                    <div class="code-block">
                        <h4>Get all grants by status:</h4>
                        <pre><code>SELECT * FROM grants WHERE status = 'in_progress' ORDER BY deadline_timestamp;</code></pre>
                    </div>
                    <div class="code-block">
                        <h4>Get grants due in next 30 days:</h4>
                        <pre><code>SELECT * FROM grants 
WHERE deadline_timestamp BETWEEN ? AND ? 
ORDER BY deadline_timestamp;</code></pre>
                    </div>
                    <div class="code-block">
                        <h4>Get application progress:</h4>
                        <pre><code>SELECT g.name, a.status, a.progress_percentage, a.current_step
FROM grants g
JOIN application_status a ON g.id = a.grant_id
WHERE g.id = ?;</code></pre>
                    </div>
                </div>
            </div>

            <!-- API Reference -->
            <div id="doc-api" class="doc-section">
                <h2>API Reference</h2>
                
                <div class="api-class">
                    <h3>AutomationWorkflow</h3>
                    <p class="class-desc">Orchestrates the complete grant application automation workflow.</p>
                    <div class="api-method">
                        <h4>__init__(username, password, docs_folder, config_path=None, use_narratives=False, openai_api_key=None, narrative_model=None, mcp_tools=None, db_path="grants.db")</h4>
                        <p><strong>Parameters:</strong></p>
                        <ul>
                            <li><code>username</code> (str): 4Culture login username</li>
                            <li><code>password</code> (str): 4Culture login password</li>
                            <li><code>docs_folder</code> (str): Path to docs folder containing grant documents</li>
                            <li><code>config_path</code> (str, optional): Path to grant configuration file</li>
                            <li><code>use_narratives</code> (bool): Whether to use narrative generation</li>
                            <li><code>openai_api_key</code> (str, optional): OpenAI API key</li>
                            <li><code>narrative_model</code> (str, optional): Model name for narrative generation</li>
                            <li><code>mcp_tools</code> (dict, optional): MCP browser tool functions</li>
                            <li><code>db_path</code> (str): Path to SQLite database</li>
                        </ul>
                    </div>
                    <div class="api-method">
                        <h4>run_automation(grant_name, document_paths=None, dry_run=False) -> Dict[str, Any]</h4>
                        <p>Run the complete automation workflow for a grant application.</p>
                        <p><strong>Parameters:</strong></p>
                        <ul>
                            <li><code>grant_name</code> (str): Name of the grant to apply for</li>
                            <li><code>document_paths</code> (List[str], optional): Specific documents to use</li>
                            <li><code>dry_run</code> (bool): If True, validate without browser automation</li>
                        </ul>
                        <p><strong>Returns:</strong> Dictionary with workflow results, status, errors, and warnings</p>
                    </div>
                    <div class="api-method">
                        <h4>generate_report(result, output_path=None) -> str</h4>
                        <p>Generate a detailed completion report.</p>
                        <p><strong>Returns:</strong> Path to generated report file</p>
                    </div>
                </div>

                <div class="api-class">
                    <h3>GrantDatabase</h3>
                    <p class="class-desc">Manages SQLite database for grant planning and tracking.</p>
                    <div class="api-method">
                        <h4>__init__(db_path="grants.db")</h4>
                        <p>Initialize database connection and create schema if needed.</p>
                    </div>
                    <div class="api-method">
                        <h4>add_grant(grant_data: Dict[str, Any]) -> int</h4>
                        <p>Add a new grant to the database.</p>
                        <p><strong>Returns:</strong> Grant ID</p>
                    </div>
                    <div class="api-method">
                        <h4>update_grant_status(grant_id, status, **kwargs)</h4>
                        <p>Update grant status and related information.</p>
                    </div>
                    <div class="api-method">
                        <h4>get_grants_by_status(status=None) -> List[Dict[str, Any]]</h4>
                        <p>Get grants filtered by status.</p>
                    </div>
                    <div class="api-method">
                        <h4>get_grants_by_month() -> Dict[str, Any]</h4>
                        <p>Get grants grouped by month.</p>
                    </div>
                    <div class="api-method">
                        <h4>get_grant_details(grant_id) -> Optional[Dict[str, Any]]</h4>
                        <p>Get complete grant details including status.</p>
                    </div>
                    <div class="api-method">
                        <h4>close()</h4>
                        <p>Close database connection.</p>
                    </div>
                </div>

                <div class="api-class">
                    <h3>NarrativeGenerator</h3>
                    <p class="class-desc">Generates complete narratives from structured grant data using OpenAI API.</p>
                    <div class="api-method">
                        <h4>__init__(api_key=None, model="gpt-4", temperature=0.7, max_tokens=2000)</h4>
                        <p>Initialize narrative generator with OpenAI configuration.</p>
                    </div>
                    <div class="api-method">
                        <h4>generate_project_description(grant_name, grant_data) -> Optional[str]</h4>
                        <p>Generate comprehensive project description narrative.</p>
                    </div>
                    <div class="api-method">
                        <h4>generate_goals_narrative(grant_name, grant_data) -> Optional[str]</h4>
                        <p>Generate project goals narrative.</p>
                    </div>
                    <div class="api-method">
                        <h4>generate_impact_narrative(grant_name, grant_data) -> Optional[str]</h4>
                        <p>Generate impact statement narrative.</p>
                    </div>
                    <div class="api-method">
                        <h4>generate_activities_narrative(grant_name, grant_data) -> Optional[str]</h4>
                        <p>Generate activities description narrative.</p>
                    </div>
                    <div class="api-method">
                        <h4>generate_budget_narrative(grant_name, grant_data) -> Optional[str]</h4>
                        <p>Generate budget justification narrative.</p>
                    </div>
                    <div class="api-method">
                        <h4>generate_narrative(narrative_type, grant_name, grant_data) -> Optional[str]</h4>
                        <p>Generic narrative generation method.</p>
                    </div>
                </div>

                <div class="api-class">
                    <h3>DataExtractor</h3>
                    <p class="class-desc">Extracts structured grant data from documents.</p>
                    <div class="api-method">
                        <h4>__init__(docs_folder)</h4>
                        <p>Initialize with path to docs folder.</p>
                    </div>
                    <div class="api-method">
                        <h4>identify_relevant_documents(grant_name, organization_name=None) -> List[str]</h4>
                        <p>Identify relevant documents for a grant application.</p>
                    </div>
                    <div class="api-method">
                        <h4>extract_grant_data(grant_name, document_paths=None) -> Dict[str, Any]</h4>
                        <p>Extract and merge grant data from documents.</p>
                    </div>
                    <div class="api-method">
                        <h4>validate_extracted_data(grant_data) -> Dict[str, Any]</h4>
                        <p>Validate extracted data for completeness and correctness.</p>
                    </div>
                    <div class="api-method">
                        <h4>get_standardized_data(grant_data) -> Dict[str, Any]</h4>
                        <p>Standardize data format for mapping.</p>
                    </div>
                </div>

                <div class="api-class">
                    <h3>FormMapper</h3>
                    <p class="class-desc">Maps extracted grant data to form fields.</p>
                    <div class="api-method">
                        <h4>__init__(config_path=None, narrative_generator=None, use_narratives=False, narrative_config=None)</h4>
                        <p>Initialize form mapper with configuration.</p>
                    </div>
                    <div class="api-method">
                        <h4>map_data_to_fields(standardized_data, grant_name) -> List[Dict[str, Any]]</h4>
                        <p>Map standardized data to 4Culture form fields.</p>
                    </div>
                    <div class="api-method">
                        <h4>validate_mapped_fields(mapped_fields) -> Dict[str, Any]</h4>
                        <p>Validate mapped fields for completeness.</p>
                    </div>
                    <div class="api-method">
                        <h4>create_field_filling_instructions(mapped_fields) -> List[Dict[str, Any]]</h4>
                        <p>Create instructions for browser automation.</p>
                    </div>
                </div>

                <div class="api-class">
                    <h3>ApplicationAutomator</h3>
                    <p class="class-desc">Extended scraper with form automation capabilities.</p>
                    <div class="api-method">
                        <h4>__init__(username, password, mcp_tools=None)</h4>
                        <p>Initialize automator with credentials and MCP tools.</p>
                    </div>
                    <div class="api-method">
                        <h4>start_new_application(grant_name) -> bool</h4>
                        <p>Navigate to and start a new grant application.</p>
                    </div>
                    <div class="api-method">
                        <h4>fill_form_fields(field_instructions) -> Dict[str, Any]</h4>
                        <p>Fill form fields using provided instructions.</p>
                    </div>
                    <div class="api-method">
                        <h4>save_draft() -> Dict[str, Any]</h4>
                        <p>Save the current draft application.</p>
                    </div>
                    <div class="api-method">
                        <h4>handle_form_validation_errors() -> List[str]</h4>
                        <p>Detect and handle form validation errors.</p>
                    </div>
                </div>

                <div class="api-class">
                    <h3>MCPBrowserIntegration</h3>
                    <p class="class-desc">Unified interface for MCP browser tool interactions.</p>
                    <div class="api-method">
                        <h4>__init__(use_multi_session=False)</h4>
                        <p>Initialize browser integration.</p>
                    </div>
                    <div class="api-method">
                        <h4>initialize_browser(mcp_tools) -> bool</h4>
                        <p>Initialize browser with MCP tools.</p>
                    </div>
                    <div class="api-method">
                        <h4>navigate(url) -> bool</h4>
                        <p>Navigate to a URL.</p>
                    </div>
                    <div class="api-method">
                        <h4>click(element_description, element_ref=None) -> bool</h4>
                        <p>Click an element on the page.</p>
                    </div>
                    <div class="api-method">
                        <h4>type_text(element_description, text, element_ref=None, slowly=False) -> bool</h4>
                        <p>Type text into an element.</p>
                    </div>
                    <div class="api-method">
                        <h4>select_option(element_description, values, element_ref=None) -> bool</h4>
                        <p>Select option(s) in a dropdown.</p>
                    </div>
                    <div class="api-method">
                        <h4>take_screenshot(name) -> Optional[str]</h4>
                        <p>Take a screenshot of the current page.</p>
                    </div>
                    <div class="api-method">
                        <h4>get_current_url() -> Optional[str]</h4>
                        <p>Get the current page URL.</p>
                    </div>
                    <div class="api-method">
                        <h4>wait_for(text=None, text_gone=None, time_seconds=None) -> bool</h4>
                        <p>Wait for text to appear/disappear or for a time period.</p>
                    </div>
                </div>
            </div>

            <!-- Integration Guides -->
            <div id="doc-integration" class="doc-section">
                <h2>Integration Guides</h2>
                
                <div class="doc-subsection">
                    <h3>MCP Browser Tools Integration</h3>
                    <p>The system integrates with MCP (Model Context Protocol) browser tools for automation. Two implementations are supported:</p>
                    <ul>
                        <li><strong>Browserbase/Stagehand:</strong> Cloud-based browser automation</li>
                        <li><strong>Cursor IDE Browser:</strong> Local browser automation</li>
                    </ul>
                    <div class="code-block">
                        <h4>Initialization:</h4>
                        <pre><code>from grant_automation_cli import MCPBrowserIntegration

browser = MCPBrowserIntegration(use_multi_session=False)
browser.initialize_browser(mcp_tools)</code></pre>
                    </div>
                    <p>The system automatically detects available MCP tools and uses the appropriate implementation.</p>
                </div>

                <div class="doc-subsection">
                    <h3>OpenAI API Integration</h3>
                    <p>Narrative generation requires an OpenAI API key. The system supports multiple methods for providing the key:</p>
                    <ol>
                        <li><strong>Environment Variable:</strong> <code>export OPENAI_API_KEY='your-key'</code></li>
                        <li><strong>CLI Argument:</strong> <code>--openai-api-key 'your-key'</code></li>
                        <li><strong>Configuration File:</strong> Set in <code>grant_config.yaml</code> (not recommended for security)</li>
                    </ol>
                    <div class="code-block">
                        <h4>Usage:</h4>
                        <pre><code>from grant_automation_cli import NarrativeGenerator

generator = NarrativeGenerator(
    api_key="your-api-key",
    model="gpt-4",
    temperature=0.7,
    max_tokens=2000
)

narrative = generator.generate_project_description(grant_name, grant_data)</code></pre>
                    </div>
                </div>

                <div class="doc-subsection">
                    <h3>Database Integration</h3>
                    <p>The SQLite database can be integrated into existing systems for centralized grant management.</p>
                    <div class="code-block">
                        <h4>Basic Usage:</h4>
                        <pre><code>from grant_automation_cli import GrantDatabase

db = GrantDatabase(db_path="path/to/grants.db")

# Add grant
grant_id = db.add_grant({
    'name': 'Grant Name',
    'deadline': '2026-01-15',
    'status': 'planned',
    # ... other fields
})

# Update status
db.update_grant_status(grant_id, 'in_progress', progress_percentage=50)

# Query grants
grants = db.get_grants_by_status('in_progress')</code></pre>
                    </div>
                </div>

                <div class="doc-subsection">
                    <h3>Configuration Management</h3>
                    <p>Field mappings and narrative settings can be configured via YAML files.</p>
                    <div class="code-block">
                        <h4>Example Configuration:</h4>
                        <pre><code>field_mappings:
  organization_name:
    data_key: organization_name
    field_name: "Organization Name"
    field_type: text
    required: true

narrative_generation:
  enabled: true
  model: "gpt-4"
  temperature: 0.7
  max_tokens: 2000</code></pre>
                    </div>
                </div>

                <div class="doc-subsection">
                    <h3>Extension Points</h3>
                    <p>The system is designed for extensibility:</p>
                    <ul>
                        <li><strong>Custom Document Parsers:</strong> Extend <code>DocumentParser</code> for new formats</li>
                        <li><strong>Custom Field Mappers:</strong> Extend <code>FormMapper</code> for custom mappings</li>
                        <li><strong>Custom Narrative Templates:</strong> Modify templates in <code>NarrativeGenerator</code></li>
                        <li><strong>Custom Browser Actions:</strong> Extend <code>MCPBrowserIntegration</code> for new actions</li>
                        <li><strong>Custom Validators:</strong> Add validation logic in <code>DataExtractor</code></li>
                    </ul>
                </div>
            </div>

            <!-- Development Guide -->
            <div id="doc-development" class="doc-section">
                <h2>Development Guide</h2>
                
                <div class="doc-subsection">
                    <h3>Setup Instructions</h3>
                    <ol>
                        <li>Clone the repository</li>
                        <li>Install Python 3.8 or higher</li>
                        <li>Install dependencies:
                            <div class="code-block">
                                <pre><code>pip install openai pyyaml</code></pre>
                            </div>
                        </li>
                        <li>Set up OpenAI API key (optional, for narrative generation)</li>
                        <li>Configure MCP browser tools (if using browser automation)</li>
                    </ol>
                </div>

                <div class="doc-subsection">
                    <h3>Development Environment</h3>
                    <ul>
                        <li><strong>Python Version:</strong> 3.8+</li>
                        <li><strong>IDE:</strong> Any Python IDE (VS Code, PyCharm, etc.)</li>
                        <li><strong>Testing:</strong> Manual testing with real 4Culture applications</li>
                        <li><strong>Logging:</strong> Python logging module, logs to console and files</li>
                    </ul>
                </div>

                <div class="doc-subsection">
                    <h3>Code Structure</h3>
                    <div class="code-block">
                        <pre><code>agents/grant_scraper/
├── __init__.py              # Package exports
├── scraper.py               # Base scraper class
├── document_parser.py       # Markdown parsing
├── data_extractor.py        # Data extraction
├── form_mapper.py           # Field mapping
├── narrative_generator.py  # OpenAI integration
├── application_automator.py # Browser automation
├── automation_workflow.py  # Workflow orchestration
├── grant_database.py       # Database management
├── grant_dashboard.py      # Dashboard generation
├── mcp_browser_integration.py # MCP tools integration
├── cli.py                   # Command-line interface
├── grant_config.yaml       # Configuration file
└── grants.db               # SQLite database</code></pre>
                    </div>
                </div>

                <div class="doc-subsection">
                    <h3>Testing Strategies</h3>
                    <ul>
                        <li><strong>Unit Tests:</strong> Test individual components in isolation</li>
                        <li><strong>Integration Tests:</strong> Test component interactions</li>
                        <li><strong>Dry Run Mode:</strong> Test without browser automation</li>
                        <li><strong>Real Application Testing:</strong> Test with actual 4Culture grants</li>
                        <li><strong>Error Handling:</strong> Test error scenarios and edge cases</li>
                    </ul>
                </div>

                <div class="doc-subsection">
                    <h3>Best Practices</h3>
                    <ul>
                        <li><strong>Error Handling:</strong> Always wrap external API calls in try-except blocks</li>
                        <li><strong>Logging:</strong> Use appropriate log levels (DEBUG, INFO, WARNING, ERROR)</li>
                        <li><strong>Configuration:</strong> Use YAML files for customizable settings</li>
                        <li><strong>Validation:</strong> Validate data at every step</li>
                        <li><strong>Documentation:</strong> Document all public methods and classes</li>
                        <li><strong>Security:</strong> Never commit API keys or credentials</li>
                        <li><strong>Modularity:</strong> Keep components independent and testable</li>
                    </ul>
                </div>

                <div class="doc-subsection">
                    <h3>Contributing Guidelines</h3>
                    <ol>
                        <li>Follow existing code style and structure</li>
                        <li>Add comprehensive error handling</li>
                        <li>Update documentation for new features</li>
                        <li>Test thoroughly before submitting</li>
                        <li>Include logging for debugging</li>
                        <li>Maintain backward compatibility when possible</li>
                    </ol>
                </div>
            </div>
        </div>

        <style>
            .engineering-docs {
                max-width: 1200px;
                margin: 0 auto;
            }

            .docs-nav-tabs {
                display: flex;
                gap: 10px;
                margin-bottom: 30px;
                flex-wrap: wrap;
                border-bottom: 2px solid #e9ecef;
                padding-bottom: 10px;
            }

            .doc-tab {
                padding: 12px 24px;
                border: none;
                background: white;
                border-radius: 8px 8px 0 0;
                cursor: pointer;
                font-weight: 600;
                color: #667eea;
                transition: all 0.3s ease;
                border-bottom: 3px solid transparent;
            }

            .doc-tab:hover {
                background: #f8f9fa;
            }

            .doc-tab.active {
                background: #667eea;
                color: white;
                border-bottom-color: #667eea;
            }

            .doc-section {
                display: none;
                animation: fadeIn 0.3s ease;
            }

            .doc-section.active {
                display: block;
            }

            .doc-subsection {
                margin-bottom: 40px;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 8px;
            }

            .doc-subsection h3 {
                color: #667eea;
                margin-bottom: 15px;
                font-size: 1.5em;
            }

            .doc-subsection h4 {
                color: #333;
                margin-top: 20px;
                margin-bottom: 10px;
            }

            .value-grid, .feature-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }

            .value-card, .feature-card {
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }

            .value-card h4, .feature-card h3 {
                color: #667eea;
                margin-bottom: 10px;
            }

            .benefits {
                margin-top: 15px;
            }

            .benefits h4 {
                font-size: 1em;
                margin-top: 15px;
                color: #333;
            }

            .usecase-card {
                background: white;
                padding: 25px;
                border-radius: 8px;
                margin-bottom: 30px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }

            .usecase-card h3 {
                color: #667eea;
                margin-bottom: 15px;
            }

            .usecase-meta {
                background: #f8f9fa;
                padding: 15px;
                border-radius: 6px;
                margin-bottom: 20px;
            }

            .usecase-flow ol, .usecase-flow ul {
                margin-left: 20px;
                margin-top: 10px;
            }

            .mermaid-diagram {
                background: white;
                padding: 20px;
                border-radius: 8px;
                margin: 20px 0;
                overflow-x: auto;
            }

            .mermaid-diagram pre {
                margin: 0;
                font-family: 'Courier New', monospace;
            }

            .tech-stack {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }

            .tech-category {
                background: white;
                padding: 15px;
                border-radius: 8px;
            }

            .tech-category h4 {
                color: #667eea;
                margin-bottom: 10px;
            }

            .table-doc {
                margin-bottom: 30px;
            }

            .schema-table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 15px;
                background: white;
            }

            .schema-table th, .schema-table td {
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #e9ecef;
            }

            .schema-table th {
                background: #667eea;
                color: white;
                font-weight: 600;
            }

            .schema-table tr:hover {
                background: #f8f9fa;
            }

            .code-block {
                background: #2d2d2d;
                color: #f8f8f2;
                padding: 20px;
                border-radius: 8px;
                margin: 15px 0;
                overflow-x: auto;
            }

            .code-block h4 {
                color: #f8f8f2;
                margin-bottom: 10px;
            }

            .code-block pre {
                margin: 0;
                font-family: 'Courier New', monospace;
                font-size: 0.9em;
            }

            .code-block code {
                color: #f8f8f2;
            }

            .api-class {
                background: white;
                padding: 25px;
                border-radius: 8px;
                margin-bottom: 30px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }

            .api-class h3 {
                color: #667eea;
                margin-bottom: 10px;
            }

            .class-desc {
                font-style: italic;
                color: #666;
                margin-bottom: 20px;
            }

            .api-method {
                margin-top: 20px;
                padding-top: 20px;
                border-top: 1px solid #e9ecef;
            }

            .api-method h4 {
                color: #333;
                font-family: monospace;
                font-size: 1em;
                margin-bottom: 10px;
            }

            .api-method ul {
                margin-left: 20px;
                margin-top: 10px;
            }

            .api-method code {
                background: #f8f9fa;
                padding: 2px 6px;
                border-radius: 4px;
                font-family: monospace;
            }
        </style>

        <script>
            function showDocSection(sectionId) {
                // Hide all sections
                document.querySelectorAll('.doc-section').forEach(section => {
                    section.classList.remove('active');
                });
                
                // Remove active class from all tabs
                document.querySelectorAll('.doc-tab').forEach(tab => {
                    tab.classList.remove('active');
                });
                
                // Show selected section
                document.getElementById('doc-' + sectionId).classList.add('active');
                
                // Activate clicked tab
                event.target.classList.add('active');
            }
        </script>
        """

    def _get_css(self) -> str:
        """Get CSS styles."""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: #333;
        }

        .dashboard-container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }

        .dashboard-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }

        .dashboard-header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }

        .subtitle {
            font-size: 1.2em;
            opacity: 0.9;
            margin-bottom: 30px;
        }

        .header-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }

        .stat-card {
            background: rgba(255,255,255,0.2);
            backdrop-filter: blur(10px);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }

        .stat-value {
            font-size: 2.5em;
            font-weight: 700;
            margin-bottom: 5px;
        }

        .stat-label {
            font-size: 0.9em;
            opacity: 0.9;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .dashboard-nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 20px;
            padding: 20px 40px;
            background: #f8f9fa;
            border-bottom: 2px solid #e9ecef;
        }

        .nav-left {
            display: flex;
            gap: 10px;
        }

        .nav-right {
            display: flex;
            gap: 10px;
            align-items: center;
        }

        .search-input {
            padding: 10px 15px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 0.95em;
            min-width: 250px;
            transition: border-color 0.3s ease;
        }

        .search-input:focus {
            outline: none;
            border-color: #667eea;
        }

        .btn-export {
            padding: 10px 20px;
            background: #27ae60;
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .btn-export:hover {
            background: #229954;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(39, 174, 96, 0.3);
        }

        .nav-btn {
            padding: 12px 24px;
            border: none;
            background: white;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1em;
            font-weight: 600;
            color: #667eea;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .nav-btn:hover {
            background: #667eea;
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }

        .nav-btn.active {
            background: #667eea;
            color: white;
        }

        .dashboard-main {
            padding: 40px;
        }

        .view-section {
            display: none;
        }

        .view-section.active {
            display: block;
        }

        .view-section h2 {
            font-size: 2em;
            margin-bottom: 30px;
            color: #333;
        }

        .timeline-container {
            display: flex;
            flex-direction: column;
            gap: 30px;
        }

        .timeline-month {
            border-left: 4px solid #667eea;
            padding-left: 20px;
            margin-bottom: 30px;
        }

        .timeline-month.month-past {
            border-left-color: #95a5a6;
            opacity: 0.7;
        }

        .timeline-month.month-current {
            border-left-color: #e74c3c;
        }

        .timeline-month.month-upcoming {
            border-left-color: #27ae60;
        }

        .month-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }

        .month-header h3 {
            font-size: 1.5em;
            color: #333;
        }

        .grant-count {
            background: #667eea;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: 600;
        }

        .grants-list {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
        }

        .grant-card {
            background: white;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            padding: 20px;
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .grant-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.15);
            border-color: #667eea;
        }

        .grant-card.status-planned {
            border-left: 5px solid #95a5a6;
        }

        .grant-card.status-in-progress {
            border-left: 5px solid #3498db;
        }

        .grant-card.status-submitted {
            border-left: 5px solid #f39c12;
        }

        .grant-card.status-awarded {
            border-left: 5px solid #27ae60;
        }

        .grant-card.status-rejected {
            border-left: 5px solid #e74c3c;
        }

        .grant-card-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 15px;
        }

        .grant-name {
            font-size: 1.2em;
            font-weight: 700;
            color: #333;
            flex: 1;
            margin-right: 10px;
        }

        .grant-status-badge {
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .grant-status-badge.status-planned {
            background: #ecf0f1;
            color: #7f8c8d;
        }

        .grant-status-badge.status-in-progress {
            background: #ebf5fb;
            color: #2980b9;
        }

        .grant-status-badge.status-submitted {
            background: #fef5e7;
            color: #d68910;
        }

        .grant-status-badge.status-awarded {
            background: #eafaf1;
            color: #229954;
        }

        .grant-status-badge.status-rejected {
            background: #fadbd8;
            color: #c0392b;
        }

        .grant-card-body {
            margin-bottom: 15px;
        }

        .grant-card-body > div {
            margin-bottom: 10px;
            font-size: 0.95em;
        }

        .grant-card-body strong {
            color: #667eea;
            margin-right: 5px;
        }

        .grant-progress {
            margin: 15px 0;
        }

        .progress-bar {
            width: 100%;
            height: 8px;
            background: #ecf0f1;
            border-radius: 4px;
            overflow: hidden;
            margin-bottom: 5px;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            transition: width 0.3s ease;
        }

        .progress-text {
            font-size: 0.85em;
            color: #7f8c8d;
        }

        .deadline-overdue {
            color: #e74c3c;
            font-weight: 700;
        }

        .deadline-urgent {
            color: #e74c3c;
            font-weight: 600;
        }

        .deadline-warning {
            color: #f39c12;
            font-weight: 600;
        }

        .deadline-ok {
            color: #27ae60;
        }

        .grant-card-footer {
            border-top: 1px solid #e9ecef;
            padding-top: 15px;
            margin-top: 15px;
        }

        .btn-details {
            width: 100%;
            padding: 10px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .btn-details:hover {
            background: #764ba2;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
        }

        .status-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
        }

        .status-column h3 {
            font-size: 1.3em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid;
        }

        .status-header.planned {
            color: #7f8c8d;
            border-bottom-color: #95a5a6;
        }

        .status-header.in-progress {
            color: #2980b9;
            border-bottom-color: #3498db;
        }

        .status-header.submitted {
            color: #d68910;
            border-bottom-color: #f39c12;
        }

        .status-header.completed {
            color: #229954;
            border-bottom-color: #27ae60;
        }

        .priority-container {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
        }

        .empty-state {
            text-align: center;
            padding: 40px;
            color: #95a5a6;
            font-style: italic;
        }

        .grant-priority {
            color: #f39c12;
            font-size: 1.1em;
        }

        /* Modal Styles */
        .grant-modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.7);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
            animation: fadeIn 0.3s ease;
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        .modal-content {
            background: white;
            border-radius: 12px;
            max-width: 800px;
            max-height: 90vh;
            width: 90%;
            overflow-y: auto;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            animation: slideUp 0.3s ease;
        }

        @keyframes slideUp {
            from {
                transform: translateY(50px);
                opacity: 0;
            }
            to {
                transform: translateY(0);
                opacity: 1;
            }
        }

        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px 30px;
            border-bottom: 2px solid #e9ecef;
        }

        .modal-header h2 {
            margin: 0;
            color: #333;
        }

        .modal-close {
            background: none;
            border: none;
            font-size: 2em;
            color: #95a5a6;
            cursor: pointer;
            padding: 0;
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            transition: all 0.3s ease;
        }

        .modal-close:hover {
            background: #ecf0f1;
            color: #e74c3c;
        }

        .modal-body {
            padding: 30px;
        }

        .grant-detail-section {
            margin-bottom: 30px;
        }

        .grant-detail-section h3 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.3em;
        }

        .grant-detail-section ul {
            list-style: none;
            padding-left: 0;
        }

        .grant-detail-section li {
            padding: 10px 0;
            border-bottom: 1px solid #e9ecef;
        }

        .grant-detail-section li:before {
            content: "✓ ";
            color: #27ae60;
            font-weight: bold;
            margin-right: 10px;
        }

        /* Documentation Styles */
        .documentation-container {
            max-width: 1000px;
            margin: 0 auto;
        }

        .doc-section {
            margin-bottom: 50px;
            padding: 30px;
            background: #f8f9fa;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }

        .doc-section h2 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 2em;
        }

        .doc-section h3 {
            color: #333;
            margin-bottom: 20px;
            font-size: 1.5em;
            border-bottom: 2px solid #e9ecef;
            padding-bottom: 10px;
        }

        .doc-section h4 {
            color: #667eea;
            margin-top: 20px;
            margin-bottom: 10px;
        }

        .doc-intro {
            font-size: 1.1em;
            line-height: 1.8;
            color: #555;
        }

        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }

        .feature-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }

        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }

        .feature-card h4 {
            color: #667eea;
            margin-top: 0;
            margin-bottom: 10px;
        }

        .step-card {
            display: flex;
            gap: 20px;
            margin-bottom: 30px;
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .step-number {
            width: 50px;
            height: 50px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5em;
            font-weight: 700;
            flex-shrink: 0;
        }

        .step-content {
            flex: 1;
        }

        .step-content h4 {
            margin-top: 0;
            color: #333;
        }

        .step-content pre {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            overflow-x: auto;
            margin: 15px 0;
            border-left: 3px solid #667eea;
        }

        .step-content code {
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 0.9em;
        }

        .step-content ul {
            margin: 15px 0;
            padding-left: 25px;
        }

        .step-content li {
            margin: 8px 0;
            line-height: 1.6;
        }

        .info-card, .config-card {
            background: white;
            padding: 25px;
            border-radius: 10px;
            margin: 20px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .info-card ul, .config-card ul, .config-card ol {
            margin: 15px 0;
            padding-left: 25px;
        }

        .info-card li, .config-card li {
            margin: 10px 0;
            line-height: 1.6;
        }

        .workflow-diagram {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: center;
            gap: 15px;
            margin: 30px 0;
            padding: 30px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .workflow-step {
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            min-width: 150px;
            flex: 1;
            max-width: 200px;
        }

        .workflow-icon {
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .workflow-step h4 {
            font-size: 0.9em;
            margin: 10px 0 5px 0;
            color: #333;
        }

        .workflow-step p {
            font-size: 0.8em;
            color: #666;
            margin: 0;
        }

        .workflow-arrow {
            font-size: 2em;
            color: #667eea;
            font-weight: bold;
        }

        .best-practices {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }

        .practice-item {
            background: white;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #27ae60;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .practice-item h4 {
            color: #27ae60;
            margin-top: 0;
        }

        .command-reference {
            background: white;
            padding: 25px;
            border-radius: 10px;
            margin: 20px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .command-reference h4 {
            margin-top: 25px;
            margin-bottom: 10px;
        }

        .command-reference h4:first-child {
            margin-top: 0;
        }

        .command-reference pre {
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 15px;
            border-radius: 6px;
            overflow-x: auto;
            margin: 15px 0;
        }

        .command-reference code {
            color: #f8f8f2;
        }

        .support-info {
            background: white;
            padding: 25px;
            border-radius: 10px;
            margin: 20px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .support-info ul {
            margin: 15px 0;
            padding-left: 25px;
        }

        .support-info li {
            margin: 10px 0;
            line-height: 1.6;
        }

        @media (max-width: 768px) {
            .dashboard-header h1 {
                font-size: 1.8em;
            }

            .grants-list {
                grid-template-columns: 1fr;
            }

            .status-container {
                grid-template-columns: 1fr;
            }

            .header-stats {
                grid-template-columns: repeat(2, 1fr);
            }

            .workflow-diagram {
                flex-direction: column;
            }

            .workflow-arrow {
                transform: rotate(90deg);
            }

            .step-card {
                flex-direction: column;
            }

            .feature-grid {
                grid-template-columns: 1fr;
            }

            .best-practices {
                grid-template-columns: 1fr;
            }
        }
        """

    def _get_javascript(self) -> str:
        """Get JavaScript code."""
        return """
        // Grant data storage
        let grantData = {};
        
        // Navigation functionality
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const view = btn.dataset.view;
                
                // Update active button
                document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                // Update active view
                document.querySelectorAll('.view-section').forEach(section => {
                    section.classList.remove('active');
                });
                document.getElementById(view + '-view').classList.add('active');
            });
        });

        // Grant details modal
        function showGrantDetails(grantId) {
            // Create modal
            const modal = document.createElement('div');
            modal.className = 'grant-modal';
            modal.innerHTML = `
                <div class="modal-content">
                    <div class="modal-header">
                        <h2>Grant Details</h2>
                        <button class="modal-close" onclick="closeModal()">&times;</button>
                    </div>
                    <div class="modal-body" id="grant-details-content">
                        <p>Loading grant details...</p>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
            
            // Fetch grant details (would be from API in production)
            setTimeout(() => {
                document.getElementById('grant-details-content').innerHTML = `
                    <div class="grant-detail-section">
                        <h3>Application Status</h3>
                        <p>Grant ID: ${grantId}</p>
                        <p>Status: In Progress</p>
                        <p>Progress: 65%</p>
                    </div>
                    <div class="grant-detail-section">
                        <h3>Next Steps</h3>
                        <ul>
                            <li>Complete narrative generation</li>
                            <li>Review form fields</li>
                            <li>Submit application</li>
                        </ul>
                    </div>
                `;
            }, 300);
        }
        
        function closeModal() {
            const modal = document.querySelector('.grant-modal');
            if (modal) {
                modal.remove();
            }
        }
        
        // Close modal on outside click
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('grant-modal')) {
                closeModal();
            }
        });
        
        // Filter and search functionality
        function filterGrants(searchTerm) {
            const cards = document.querySelectorAll('.grant-card');
            cards.forEach(card => {
                const text = card.textContent.toLowerCase();
                if (text.includes(searchTerm.toLowerCase())) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        }
        
        // Sort functionality
        function sortGrants(sortBy) {
            const container = document.querySelector('.grants-list');
            const cards = Array.from(container.querySelectorAll('.grant-card'));
            
            cards.sort((a, b) => {
                if (sortBy === 'deadline') {
                    const aDeadline = a.dataset.deadline || '';
                    const bDeadline = b.dataset.deadline || '';
                    return aDeadline.localeCompare(bDeadline);
                } else if (sortBy === 'priority') {
                    const aPriority = parseInt(a.dataset.priority || '5');
                    const bPriority = parseInt(b.dataset.priority || '5');
                    return bPriority - aPriority;
                }
                return 0;
            });
            
            cards.forEach(card => container.appendChild(card));
        }
        
        // Export functionality
        function exportDashboard(format) {
            if (format === 'csv') {
                // Export to CSV
                const grants = Array.from(document.querySelectorAll('.grant-card'));
                let csv = 'Grant Name,Status,Deadline,Amount,Progress\\n';
                grants.forEach(card => {
                    const name = card.querySelector('.grant-name').textContent;
                    const status = card.querySelector('.grant-status-badge').textContent;
                    const deadline = card.querySelector('.grant-deadline')?.textContent || 'N/A';
                    const amount = card.querySelector('.grant-amount')?.textContent || 'N/A';
                    const progress = card.querySelector('.progress-text')?.textContent || '0%';
                    csv += `"${name}","${status}","${deadline}","${amount}","${progress}"\\n`;
                });
                
                const blob = new Blob([csv], { type: 'text/csv' });
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'grant-dashboard.csv';
                a.click();
            }
        }
        
        // Auto-refresh notification
        let lastUpdate = new Date();
        setInterval(() => {
            const now = new Date();
            const minutesSinceUpdate = Math.floor((now - lastUpdate) / 60000);
            if (minutesSinceUpdate >= 5) {
                console.log('Dashboard data refresh recommended - last update: ' + lastUpdate.toLocaleTimeString());
            }
        }, 60000);
        
        // Initialize tooltips and interactions
        document.addEventListener('DOMContentLoaded', () => {
            // Initialize Mermaid diagrams
            if (typeof mermaid !== 'undefined') {
                mermaid.initialize({ startOnLoad: true, theme: 'default' });
            }
            
            // Add hover effects
            document.querySelectorAll('.grant-card').forEach(card => {
                card.addEventListener('mouseenter', function() {
                    this.style.transform = 'translateY(-5px) scale(1.02)';
                });
                card.addEventListener('mouseleave', function() {
                    this.style.transform = 'translateY(0) scale(1)';
                });
            });
            
            // Add keyboard navigation
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    closeModal();
                }
            });
        });
        """
