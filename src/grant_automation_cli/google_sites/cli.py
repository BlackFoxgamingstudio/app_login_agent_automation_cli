"""
Google Sites CLI

DEVELOPER GUIDELINE: CLI Architecture
Handles command-line arguments for Google Sites operations. Keep command 
handlers thin by delegating business logic to specific modules (extractor, 
automator, database).
"""

import os

from src.grant_automation_cli.google_sites import automator, database, extractor


def register_parser(subparsers):
    """Register Google Sites commands."""
    gsite_parser = subparsers.add_parser('gsite', help="Google Sites automation commands")
    gsite_subparsers = gsite_parser.add_subparsers(dest="gsite_command", required=True)
    
    # Init command
    init_parser = gsite_subparsers.add_parser('init', help="Initialize markdown templates in current directory")
    init_parser.add_argument('--dir', type=str, default='.', help="Directory to save templates (default: current)")
    
    # Auth command
    auth_parser = gsite_subparsers.add_parser('auth', help="Log into Google manually to save persistent session for later steps")
    
    # Build command
    build_parser = gsite_subparsers.add_parser('build', help="Build Google Site using filled templates")
    build_parser.add_argument('--dir', type=str, default='.', help="Directory containing filled templates (default: current)")
    
    # DB Init command
    db_init_parser = gsite_subparsers.add_parser('db-init', help="Force initialization of the google_sites.db with default templates")

def handle_command(args):
    """Handle Google Sites commands."""
    if args.gsite_command == 'init':
        _handle_init(args)
    elif args.gsite_command == 'auth':
        _handle_auth(args)
    elif args.gsite_command == 'build':
        _handle_build(args)
    elif args.gsite_command == 'db-init':
        database.init_db()
        print("Initialized google_sites.db successfully.")

def _handle_init(args):
    target_dir = args.dir
    os.makedirs(target_dir, exist_ok=True)
    
    print(f"Initializing Google Sites templates in {target_dir} via database...")
    
    # Ensure DB is ready
    database.init_db()
    
    templates_to_create = ["business_profile.md", "design_preferences.md", "page_content.md"]
    
    for filename in templates_to_create:
        content = database.get_template(filename)
        if content:
            file_path = os.path.join(target_dir, filename)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Created/Updated: {filename}")
        else:
            print(f"Error: Template {filename} not found in database.")
            
    print("\nTemplates successfully fetched from database. Please fill them out before running 'build'.")

def _handle_auth(args):
    try:
        automator.authenticate_google()
    except RuntimeError as e:
        print(f"Authentication failed: {e}")

def _handle_build(args):
    target_dir = args.dir
    print(f"Extracting data from templates in {target_dir}...")
    
    # Extract data
    profile = extractor.extract_business_profile(os.path.join(target_dir, 'business_profile.md'))
    design = extractor.extract_design_preferences(os.path.join(target_dir, 'design_preferences.md'))
    pages = extractor.extract_page_content(os.path.join(target_dir, 'page_content.md'))
    
    # Verify we got something
    if not profile or not profile.get('name'):
        print("Warning: Could not parse basic business profile info. Make sure business_profile.md is correctly filled out.")
        
    print("\nExtraction Summary:")
    print(f"Business Profile Info Found: {list(profile.keys())}")
    print(f"Pages Found: {len(pages)}")
    
    # Pass to automator
    automator.build_google_site(profile, design, pages)
