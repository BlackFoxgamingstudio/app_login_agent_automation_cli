"""
CLI for managing grant database and generating dashboard.
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import Optional

from .grant_database import GrantDatabase
from .grant_dashboard import GrantDashboard

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def add_grant_command(args):
    """Add a new grant to the database."""
    db = GrantDatabase(args.db)
    
    grant_data = {
        'name': args.name,
        'identifier': args.identifier,
        'deadline': args.deadline,
        'status': args.status or 'planned',
        'amount_requested': args.amount,
        'organization_name': args.org,
        'project_title': args.project,
        'description': args.description,
        'focus_areas': args.focus,
        'eligibility_requirements': args.eligibility,
        'application_url': args.url,
        'notes': args.notes,
        'priority': args.priority or 5
    }
    
    grant_id = db.add_grant(grant_data)
    
    if args.documents:
        for doc in args.documents:
            db.add_document(grant_id, doc)
    
    print(f"✅ Grant added with ID: {grant_id}")
    db.close()


def update_status_command(args):
    """Update grant application status."""
    db = GrantDatabase(args.db)
    
    kwargs = {}
    if args.progress is not None:
        kwargs['progress_percentage'] = args.progress
    if args.step:
        kwargs['current_step'] = args.step
    if args.draft_url:
        kwargs['draft_url'] = args.draft_url
    
    db.update_grant_status(args.grant_id, args.status, **kwargs)
    print(f"✅ Grant {args.grant_id} status updated to {args.status}")
    db.close()


def generate_dashboard_command(args):
    """Generate HTML dashboard."""
    dashboard = GrantDashboard(args.db)
    output_path = dashboard.generate_dashboard()
    print(f"✅ Dashboard generated at: {output_path}")
    print(f"   Open in browser: file://{Path(output_path).absolute()}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description='Grant Planning Database CLI')
    parser.add_argument('--db', default='agents/grant_scraper/grants.db',
                       help='Path to database file')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Add grant command
    add_parser = subparsers.add_parser('add', help='Add a new grant')
    add_parser.add_argument('--name', required=True, help='Grant name')
    add_parser.add_argument('--identifier', help='Grant identifier')
    add_parser.add_argument('--deadline', help='Deadline (YYYY-MM-DD or "Month DD, YYYY")')
    add_parser.add_argument('--status', choices=['planned', 'in_progress', 'submitted', 'awarded', 'rejected'],
                           help='Status')
    add_parser.add_argument('--amount', type=float, help='Amount requested')
    add_parser.add_argument('--org', help='Organization name')
    add_parser.add_argument('--project', help='Project title')
    add_parser.add_argument('--description', help='Description')
    add_parser.add_argument('--focus', help='Focus areas')
    add_parser.add_argument('--eligibility', help='Eligibility requirements')
    add_parser.add_argument('--url', help='Application URL')
    add_parser.add_argument('--notes', help='Notes')
    add_parser.add_argument('--priority', type=int, choices=range(1, 11),
                           help='Priority (1-10)')
    add_parser.add_argument('--documents', nargs='+', help='Document paths')
    
    # Update status command
    update_parser = subparsers.add_parser('update', help='Update grant status')
    update_parser.add_argument('--grant-id', type=int, required=True, help='Grant ID')
    update_parser.add_argument('--status', required=True,
                              choices=['planned', 'in_progress', 'submitted', 'awarded', 'rejected'],
                              help='New status')
    update_parser.add_argument('--progress', type=int, help='Progress percentage (0-100)')
    update_parser.add_argument('--step', help='Current step')
    update_parser.add_argument('--draft-url', help='Draft URL')
    
    # Generate dashboard command
    dashboard_parser = subparsers.add_parser('dashboard', help='Generate HTML dashboard')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == 'add':
        add_grant_command(args)
    elif args.command == 'update':
        update_status_command(args)
    elif args.command == 'dashboard':
        generate_dashboard_command(args)


if __name__ == '__main__':
    main()

