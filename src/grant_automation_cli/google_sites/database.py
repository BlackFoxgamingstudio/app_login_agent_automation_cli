"""
Google Sites Database

DEVELOPER GUIDELINE: DB Initialization & Migrations
Manages the SQLite database for Google Sites templates. When modifying 
schemas, ensure backward compatibility or provide a migration strategy. 
Use parameterized queries to prevent SQL injection.
"""

import sqlite3

DB_FILE = "google_sites.db"

def get_connection():
    """Returns a connection to the Google Sites SQLite database."""
    # Place it in root of project where command runs, or user dir
    return sqlite3.connect(DB_FILE)

def init_db():
    """Initializes the database schema and seeds it with default templates if empty."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Templates Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS templates (
            name TEXT PRIMARY KEY,
            content TEXT
        )
    """)
    
    # 2. Design Patterns Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS design_patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            theme_choice TEXT,
            primary_color TEXT,
            nav_layout TEXT
        )
    """)
    
    # 3. Creation Steps
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS creation_steps (
            step_order INTEGER PRIMARY KEY,
            title TEXT,
            description TEXT
        )
    """)
    
    conn.commit()
    _seed_default_templates(conn)
    _seed_default_patterns(conn)
    _seed_creation_steps(conn)
    
    conn.close()
    
def _seed_default_templates(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM templates")
    if cursor.fetchone()[0] == 0:
        # Business Profile
        business_content = (
            "# Business Profile\\n\\n"
            "**Business Name:** [Enter your business name]\\n"
            "**Tagline:** [Enter a short, catchy slogan]\\n"
            "**Description:** [Enter a detailed description of your services]\\n\\n"
            "## Assets\\n"
            "**Logo URL:** [URL to logo image]\\n"
            "**Favicon URL:** [URL to favicon image]\\n"
        )
        
        # Design Preferences
        design_content = (
            "# Design Preferences\\n\\n"
            "Theme:\\n"
            "- [x] Simple\\n"
            "- [ ] Aristotle\\n"
            "- [ ] Diplomat\\n\\n"
            "**Primary Brand Color (Hex Code):** [#000000]\\n\\n"
            "Choose where the navigation menu should appear:\\n"
            "- [x] Top\\n"
            "- [ ] Side\\n"
        )
        
        # Page Content
        page_content = (
            "# Pages\\n\\n"
            "## Page: Home\\n"
            "**Title:** Welcome\\n"
            "**Header Type:** [Banner]\\n\\n"
            "---\\n"
            "## Page: About Us\\n"
            "**Title:** Our Story\\n"
            "**Header Type:** [Title Only]\\n"
            "**Text Block:** [Write about the company history]\\n"
        )
        
        cursor.executemany("INSERT INTO templates (name, content) VALUES (?, ?)", [
            ("business_profile.md", business_content),
            ("design_preferences.md", design_content),
            ("page_content.md", page_content)
        ])
        conn.commit()

def _seed_default_patterns(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM design_patterns")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO design_patterns (name, theme_choice, primary_color, nav_layout) VALUES (?, ?, ?, ?)", [
            ("Corporate Default", "Diplomat", "#003366", "top"),
            ("Creative Starter", "Aristotle", "#FF5733", "side"),
            ("Minimalist", "Simple", "#000000", "top"),
        ])
        conn.commit()

def _seed_creation_steps(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM creation_steps")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO creation_steps (step_order, title, description) VALUES (?, ?, ?)", [
            (1, "Initialize Templates", "Run `gsite init` to generate Markdown files from the database."),
            (2, "Fill Content", "Client or team fills out the generated .md files with business specifics."),
            (3, "Google Auth", "Run `gsite auth` ONCE to save a persistent, un-detected Playwright session."),
            (4, "Build Site", "Run `gsite build` to have Playwright automatically create the site structure.")
        ])
        conn.commit()

def get_template(name: str) -> str:
    """Fetches a specific template content by name."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT content FROM templates WHERE name = ?", (name,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else ""
