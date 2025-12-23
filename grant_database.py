"""
Grant Planning Database
Stores grant information, application status, and planning data.
"""

import sqlite3
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class GrantDatabase:
    """Database for managing grant applications and planning."""
    
    def __init__(self, db_path: str = "agents/grant_scraper/grants.db"):
        """
        Initialize the grant database.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema."""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        
        cursor = self.conn.cursor()
        
        # Grants table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS grants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                identifier TEXT UNIQUE,
                deadline TEXT,
                deadline_timestamp INTEGER,
                status TEXT DEFAULT 'planned',
                amount_requested REAL,
                amount_awarded REAL,
                organization_name TEXT,
                project_title TEXT,
                description TEXT,
                focus_areas TEXT,
                eligibility_requirements TEXT,
                application_url TEXT,
                notes TEXT,
                priority INTEGER DEFAULT 5,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Application status tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS application_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                grant_id INTEGER NOT NULL,
                status TEXT NOT NULL,
                progress_percentage INTEGER DEFAULT 0,
                current_step TEXT,
                data_extracted BOOLEAN DEFAULT 0,
                narrative_generated BOOLEAN DEFAULT 0,
                form_filled BOOLEAN DEFAULT 0,
                draft_saved BOOLEAN DEFAULT 0,
                submitted BOOLEAN DEFAULT 0,
                submitted_date TEXT,
                award_date TEXT,
                draft_url TEXT,
                report_path TEXT,
                errors TEXT,
                warnings TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (grant_id) REFERENCES grants(id)
            )
        """)
        
        # Documents mapping
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS grant_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                grant_id INTEGER NOT NULL,
                document_path TEXT NOT NULL,
                document_type TEXT,
                is_primary BOOLEAN DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (grant_id) REFERENCES grants(id)
            )
        """)
        
        # Timeline milestones
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS timeline_milestones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                grant_id INTEGER NOT NULL,
                milestone_name TEXT NOT NULL,
                due_date TEXT,
                due_date_timestamp INTEGER,
                completed BOOLEAN DEFAULT 0,
                completed_date TEXT,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (grant_id) REFERENCES grants(id)
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_grant_status ON grants(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_grant_deadline ON grants(deadline_timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_app_status ON application_status(grant_id, status)")
        
        self.conn.commit()
        logger.info(f"Database initialized at {self.db_path}")
    
    def add_grant(self, grant_data: Dict[str, Any]) -> int:
        """
        Add a new grant to the database.
        
        Args:
            grant_data: Dictionary containing grant information
            
        Returns:
            Grant ID
        """
        cursor = self.conn.cursor()
        
        # Parse deadline to timestamp
        deadline_ts = None
        if grant_data.get('deadline'):
            try:
                deadline_ts = int(datetime.strptime(grant_data['deadline'], '%Y-%m-%d').timestamp())
            except:
                try:
                    deadline_ts = int(datetime.strptime(grant_data['deadline'], '%B %d, %Y').timestamp())
                except:
                    pass
        
        cursor.execute("""
            INSERT INTO grants (
                name, identifier, deadline, deadline_timestamp, status,
                amount_requested, organization_name, project_title,
                description, focus_areas, eligibility_requirements,
                application_url, notes, priority
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            grant_data.get('name'),
            grant_data.get('identifier'),
            grant_data.get('deadline'),
            deadline_ts,
            grant_data.get('status', 'planned'),
            grant_data.get('amount_requested'),
            grant_data.get('organization_name'),
            grant_data.get('project_title'),
            grant_data.get('description'),
            grant_data.get('focus_areas'),
            grant_data.get('eligibility_requirements'),
            grant_data.get('application_url'),
            grant_data.get('notes'),
            grant_data.get('priority', 5)
        ))
        
        grant_id = cursor.lastrowid
        self.conn.commit()
        logger.info(f"Added grant: {grant_data.get('name')} (ID: {grant_id})")
        return grant_id
    
    def update_grant_status(self, grant_id: int, status: str, **kwargs):
        """
        Update grant application status.
        
        Args:
            grant_id: Grant ID
            status: New status (planned, in_progress, submitted, awarded, rejected)
            **kwargs: Additional status fields
        """
        cursor = self.conn.cursor()
        
        # Update grant status
        cursor.execute("""
            UPDATE grants SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (status, grant_id))
        
        # Update or create application status
        cursor.execute("""
            SELECT id FROM application_status WHERE grant_id = ?
        """, (grant_id,))
        
        existing = cursor.fetchone()
        
        if existing:
            # Update existing status
            updates = ['status = ?', 'updated_at = CURRENT_TIMESTAMP']
            values = [status]
            
            for key, value in kwargs.items():
                if key in ['progress_percentage', 'current_step', 'data_extracted',
                          'narrative_generated', 'form_filled', 'draft_saved',
                          'submitted', 'submitted_date', 'award_date', 'draft_url',
                          'report_path', 'errors', 'warnings']:
                    updates.append(f"{key} = ?")
                    values.append(value)
            
            values.append(grant_id)
            cursor.execute(f"""
                UPDATE application_status SET {', '.join(updates)}
                WHERE grant_id = ?
            """, values)
        else:
            # Create new status record
            cursor.execute("""
                INSERT INTO application_status (
                    grant_id, status, progress_percentage, current_step,
                    data_extracted, narrative_generated, form_filled,
                    draft_saved, submitted, submitted_date, award_date,
                    draft_url, report_path, errors, warnings
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                grant_id, status,
                kwargs.get('progress_percentage', 0),
                kwargs.get('current_step'),
                kwargs.get('data_extracted', False),
                kwargs.get('narrative_generated', False),
                kwargs.get('form_filled', False),
                kwargs.get('draft_saved', False),
                kwargs.get('submitted', False),
                kwargs.get('submitted_date'),
                kwargs.get('award_date'),
                kwargs.get('draft_url'),
                kwargs.get('report_path'),
                json.dumps(kwargs.get('errors', [])) if kwargs.get('errors') else None,
                json.dumps(kwargs.get('warnings', [])) if kwargs.get('warnings') else None
            ))
        
        self.conn.commit()
        logger.info(f"Updated grant {grant_id} status to {status}")
    
    def get_grants_by_status(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get grants filtered by status.
        
        Args:
            status: Status to filter by (None for all)
            
        Returns:
            List of grant dictionaries
        """
        cursor = self.conn.cursor()
        
        if status:
            cursor.execute("""
                SELECT g.*, 
                       a.status as app_status,
                       a.progress_percentage,
                       a.current_step,
                       a.submitted_date,
                       a.draft_url
                FROM grants g
                LEFT JOIN application_status a ON g.id = a.grant_id
                WHERE g.status = ?
                ORDER BY g.deadline_timestamp ASC, g.priority DESC
            """, (status,))
        else:
            cursor.execute("""
                SELECT g.*, 
                       a.status as app_status,
                       a.progress_percentage,
                       a.current_step,
                       a.submitted_date,
                       a.draft_url
                FROM grants g
                LEFT JOIN application_status a ON g.id = a.grant_id
                ORDER BY g.deadline_timestamp ASC, g.priority DESC
            """)
        
        grants = []
        for row in cursor.fetchall():
            grant = dict(row)
            grants.append(grant)
        
        return grants
    
    def get_grants_by_month(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get grants organized by month (based on deadline).
        
        Returns:
            Dictionary mapping month strings to lists of grants
        """
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT g.*, 
                   a.status as app_status,
                   a.progress_percentage,
                   a.current_step,
                   a.submitted_date,
                   a.draft_url
            FROM grants g
            LEFT JOIN application_status a ON g.id = a.grant_id
            WHERE g.deadline_timestamp IS NOT NULL
            ORDER BY g.deadline_timestamp ASC
        """)
        
        grants_by_month = {}
        
        for row in cursor.fetchall():
            grant = dict(row)
            deadline_ts = grant.get('deadline_timestamp')
            
            if deadline_ts:
                deadline_date = datetime.fromtimestamp(deadline_ts)
                month_key = deadline_date.strftime('%Y-%m')
                month_name = deadline_date.strftime('%B %Y')
                
                if month_key not in grants_by_month:
                    grants_by_month[month_key] = {
                        'month_name': month_name,
                        'grants': []
                    }
                
                grants_by_month[month_key]['grants'].append(grant)
        
        return grants_by_month
    
    def get_grant_details(self, grant_id: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific grant.
        
        Args:
            grant_id: Grant ID
            
        Returns:
            Grant dictionary with all details
        """
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT g.*, 
                   a.status as app_status,
                   a.progress_percentage,
                   a.current_step,
                   a.data_extracted,
                   a.narrative_generated,
                   a.form_filled,
                   a.draft_saved,
                   a.submitted,
                   a.submitted_date,
                   a.award_date,
                   a.draft_url,
                   a.report_path,
                   a.errors,
                   a.warnings
            FROM grants g
            LEFT JOIN application_status a ON g.id = a.grant_id
            WHERE g.id = ?
        """, (grant_id,))
        
        row = cursor.fetchone()
        if row:
            grant = dict(row)
            
            # Get documents
            cursor.execute("""
                SELECT document_path, document_type, is_primary
                FROM grant_documents
                WHERE grant_id = ?
            """, (grant_id,))
            
            grant['documents'] = [dict(row) for row in cursor.fetchall()]
            
            # Get milestones
            cursor.execute("""
                SELECT milestone_name, due_date, completed, completed_date, notes
                FROM timeline_milestones
                WHERE grant_id = ?
                ORDER BY due_date_timestamp ASC
            """, (grant_id,))
            
            grant['milestones'] = [dict(row) for row in cursor.fetchall()]
            
            return grant
        
        return None
    
    def add_document(self, grant_id: int, document_path: str, 
                    document_type: Optional[str] = None, is_primary: bool = False):
        """Add a document mapping to a grant."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO grant_documents (grant_id, document_path, document_type, is_primary)
            VALUES (?, ?, ?, ?)
        """, (grant_id, document_path, document_type, is_primary))
        self.conn.commit()
    
    def add_milestone(self, grant_id: int, milestone_name: str, due_date: str,
                     notes: Optional[str] = None):
        """Add a timeline milestone to a grant."""
        cursor = self.conn.cursor()
        
        try:
            due_date_ts = int(datetime.strptime(due_date, '%Y-%m-%d').timestamp())
        except:
            due_date_ts = None
        
        cursor.execute("""
            INSERT INTO timeline_milestones (grant_id, milestone_name, due_date, due_date_timestamp, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (grant_id, milestone_name, due_date, due_date_ts, notes))
        self.conn.commit()
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()

