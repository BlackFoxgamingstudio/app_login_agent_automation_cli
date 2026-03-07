"""
Instagram CLI

DEVELOPER GUIDELINE: CLI Architecture
Handles command-line arguments for Instagram automation. Keep command 
handlers thin by delegating business logic to the automator and generator 
modules to maintain separation of concerns.
"""

import logging
import sys

from grant_automation_cli.instagram.ai_generator import InstagramAIGenerator
from grant_automation_cli.instagram.automator import run_instagram_automator
from grant_automation_cli.instagram.database import init_db

logger = logging.getLogger(__name__)

def register_parser(subparsers):
    """Registers the 'instagram' command group."""
    ig_parser = subparsers.add_parser("instagram", help="Instagram Automation Commands")
    ig_sub = ig_parser.add_subparsers(dest="ig_command", required=True)

    # Init DB command
    ig_sub.add_parser("init-db", help="Initialize the internal Instagram database")

    # Run automator command
    run_parser = ig_sub.add_parser("run", help="Run the Instagram scheduled tasks automator")
    
    # Generate caption command
    gen_parser = ig_sub.add_parser("ai-caption", help="Generate an AI Instagram caption")
    gen_parser.add_argument("--topic", required=True, help="Topic for the post")
    gen_parser.add_argument("--tone", default="luxury", help="Tone of the caption (e.g. funny, luxury)")

def handle_command(args):
    """Handles commands for the 'instagram' group."""
    if args.ig_command == "init-db":
        print("Initializing Instagram Database...")
        init_db()
        print("Done.")

    elif args.ig_command == "run":
        print("Starting Instagram Automator...")
        try:
            run_instagram_automator()
        except RuntimeError as e:
            logger.error(f"Automator failed: {e}")
            print(f"Error: {e}")

    elif args.ig_command == "ai-caption":
        print(f"Generating caption for '{args.topic}' with tone '{args.tone}'...")
        gen = InstagramAIGenerator()
        caption = gen.generate_caption(args.topic, args.tone)
        print("\n--- Generated Caption ---")
        print(caption)
        
        print("\n--- Suggested Image Prompt ---")
        prompt = gen.suggest_image_prompt(caption)
        print(prompt)

    else:
        print(f"Unknown instagram command: {args.ig_command}")
        sys.exit(1)
