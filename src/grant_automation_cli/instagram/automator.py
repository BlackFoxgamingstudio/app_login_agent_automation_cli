"""
Instagram Automation Module

DEVELOPER GUIDELINE:
This module automates Instagram via headless browser control (Playwright).
Web automation is inherently fragile due to frequent DOM changes by the platform.
Therefore, robust error handling, wait states, and graceful degradations are vital here.
"""

import logging
import os
import time

from grant_automation_cli.instagram.database import get_scheduled_posts, update_post_status

# DEVELOPER GUIDELINE: Optional Dependency Handling
# Playwright is a heavy dependency. It's wrapped in a try/except to allow the rest
# of the application to run smoothly if Instagram orchestration isn't explicitly required 
# by the end-user environment.
try:
    from playwright.sync_api import TimeoutError, sync_playwright  # type: ignore
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False

# Configure simple logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class InstagramAutomator:
    def __init__(self, use_headless: bool = False):
        """
        Initializes the Instagram Automator using Playwright.
        """
        self.use_headless = use_headless
        self.is_logged_in = False
        self.playwright = None
        self.browser = None
        self.page = None
        logger.info("Instagram Automator Initialized.")

    def login(self) -> bool:
        """
        Logs into Instagram using Playwright.
        """
        if not HAS_PLAYWRIGHT:
            logger.error("Playwright is not installed. Run 'pip install playwright' and 'playwright install'.")
            return False

        username = os.environ.get("INSTAGRAM_USERNAME")
        password = os.environ.get("INSTAGRAM_PASSWORD")
        
        if not username or not password:
            logger.warning("INSTAGRAM_USERNAME or INSTAGRAM_PASSWORD not found in environment. Proceeding unauthenticated (will likely fail).")

        try:
            logger.info("Starting Playwright to log into Instagram...")
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(headless=self.use_headless)  # type: ignore
            self.page = self.browser.new_page()  # type: ignore
            
            logger.info("Navigating to Instagram...")
            self.page.goto("https://www.instagram.com/", wait_until="networkidle")  # type: ignore
            time.sleep(2)  # Give the page a moment to fully render
            
            if username and password:
                logger.info("Filling in credentials...")
                self.page.fill("input[name='username']", username)
                self.page.fill("input[name='password']", password)
                self.page.click("button[type='submit']")  # type: ignore
                
                # Wait for navigation or error message
                try:
                    self.page.wait_for_selector("div[role='dialog']", timeout=5000)  # Save login info dialog
                    logger.info("Dismissing 'Save Your Login Info' dialog...")
                    self.page.click("button:has-text('Not Now')")  # type: ignore
                except TimeoutError:
                    pass
                
                try:
                    self.page.wait_for_selector("button:has-text('Not Now')", timeout=5000)  # Notifications dialog
                    logger.info("Dismissing 'Turn on Notifications' dialog...")
                    self.page.click("button:has-text('Not Now')")  # type: ignore
                except TimeoutError:
                    pass
                
            self.is_logged_in = True
            logger.info("Successfully logged into Instagram (or attempted).")
            return True
        except RuntimeError as e:
            logger.error(f"Failed to log in via Playwright: {e}")
            self.close()
            return False

    def _upload_post(self, image_path: str, caption: str) -> bool:
        """
        Uploads an image post to Instagram using Playwright.
        """
        if not HAS_PLAYWRIGHT or not self.page:
            logger.error("Playwright page not initialized. Cannot upload.")
            return False

        if not os.path.exists(image_path):
            logger.error(f"Image not found at path: {image_path}")
            return False

        logger.info(f"Uploading image: {image_path}")
        try:
            # DEVELOPER GUIDELINE: Fragile Selectors.
            # DOM selectors for IG change frequently; these are approximations.
            # Avoid using complex React auto-generated class names like `.xk12d`. 
            # Prefer ARIA tags or role attributes when possible for better resilience.
            logger.info("Clicking 'Create' button...")
            self.page.click("svg[aria-label='New post']")  # type: ignore
            
            logger.info("Waiting for file chooser...")
            with self.page.expect_file_chooser() as fc_info:
                self.page.click("button:has-text('Select from computer')")  # type: ignore
            file_chooser = fc_info.value
            file_chooser.set_files(image_path)
            
            logger.info("Image selected. Proceeding through crop/filter dialogs...")
            time.sleep(1)
            self.page.click("div[role='button']:has-text('Next')")  # type: ignore
            time.sleep(1)
            self.page.click("div[role='button']:has-text('Next')")  # type: ignore
            
            logger.info(f"Adding caption: '{str(caption)[:30]}...'")
            time.sleep(1)
            # Find the contenteditable div for the caption
            self.page.fill("div[aria-label='Write a caption...']", str(caption))
            
            logger.info("Publishing post...")
            self.page.click("div[role='button']:has-text('Share')")  # type: ignore
            
            # Wait for upload to complete
            self.page.wait_for_selector("text='Your post has been shared.'", timeout=30000)
            logger.info("Post published successfully.")
            
            # Close the success dialog
            self.page.click("svg[aria-label='Close']")  # type: ignore
            return True
        except RuntimeError as e:
            logger.error(f"Error during upload process: {e}")
            return False

    def process_scheduled_posts(self):
        """
        Retrieves scheduled posts from the database that are due to be published,
        and attempts to upload them.
        """
        posts = get_scheduled_posts()
        if not posts:
            logger.info("No scheduled posts to process at this time.")
            return

        logger.info(f"Found {len(posts)} scheduled posts. Processing...")
        
        if not self.is_logged_in:
            if not self.login():
                logger.error("Failed to log in. Cannot process posts.")
                return

        for post in posts:
            post_id = post['id']
            image_path = post['image_path']
            caption = post['caption']
            
            logger.info(f"Processing Post ID: {post_id}")
            success = self._upload_post(image_path, caption)
            
            if success:
                update_post_status(post_id, 'POSTED')
                logger.info(f"Post {post_id} published successfully.")
            else:
                update_post_status(post_id, 'FAILED')
                logger.error(f"Failed to publish Post {post_id}.")

        logger.info("Finished processing scheduled posts.")
        self.close()

    def close(self):
        """
        Cleans up Playwright resources.
        """
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        self.browser = None
        self.playwright = None
        self.page = None
        self.is_logged_in = False


def run_instagram_automator():
    """
    Entry point for running the automator, typically triggered by a cron job or scheduler.
    """
    automator = InstagramAutomator()
    automator.process_scheduled_posts()

if __name__ == "__main__":
    run_instagram_automator()
