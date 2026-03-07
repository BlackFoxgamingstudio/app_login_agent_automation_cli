"""
Instagram Database

DEVELOPER GUIDELINE: DB Initialization & Safety
Manages the internal SQLite database for Instagram campaigns and posts. 
Ensure all SQL queries use parameterized inputs to prevent injection attacks 
and handle datetime serialization consistently (e.g., ISO 8601).
"""

import datetime
import os
import sqlite3
from typing import Any, Dict, List, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'instagram.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Table to store main campaigns
    c.execute('''
        CREATE TABLE IF NOT EXISTS instagram_campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            start_date TEXT,
            end_date TEXT,
            description TEXT
        )
    ''')
    
    # Table to store individual posts
    c.execute('''
        CREATE TABLE IF NOT EXISTS instagram_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            campaign_id INTEGER,
            image_path TEXT,
            caption TEXT,
            status TEXT DEFAULT 'DRAFT', -- DRAFT, SCHEDULED, POSTED, FAILED
            scheduled_date TEXT,
            posted_date TEXT,
            platform TEXT DEFAULT 'instagram',
            FOREIGN KEY(campaign_id) REFERENCES instagram_campaigns(id)
        )
    ''')
    conn.commit()
    conn.close()

def save_campaign(name: str, start_date: str, end_date: str, description: str = "") -> Optional[int]:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT OR REPLACE INTO instagram_campaigns (name, start_date, end_date, description) VALUES (?, ?, ?, ?)",
        (name, start_date, end_date, description)
    )
    conn.commit()
    campaign_id = c.lastrowid
    conn.close()
    return campaign_id

def save_post(campaign_id: Optional[int], image_path: str, caption: str, scheduled_date: str) -> Optional[int]:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT OR REPLACE INTO instagram_posts (campaign_id, image_path, caption, status, scheduled_date) VALUES (?, ?, ?, 'SCHEDULED', ?)",
        (campaign_id, image_path, caption, scheduled_date)
    )
    conn.commit()
    post_id = c.lastrowid
    conn.close()
    return post_id

def get_scheduled_posts() -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    now = datetime.datetime.now().isoformat()
    c.execute(
        "SELECT * FROM instagram_posts WHERE status = 'SCHEDULED' AND scheduled_date <= ?",
        (now,)
    )
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_post_status(post_id: int, status: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.datetime.now().isoformat()
    
    if status == 'POSTED':
        c.execute("UPDATE instagram_posts SET status = ?, posted_date = ? WHERE id = ?", (status, now, post_id))
    else:
        c.execute("UPDATE instagram_posts SET status = ? WHERE id = ?", (status, post_id))
        
    conn.commit()
    conn.close()

def get_all_posts() -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM instagram_posts ORDER BY scheduled_date ASC")
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

if __name__ == '__main__':
    init_db()
