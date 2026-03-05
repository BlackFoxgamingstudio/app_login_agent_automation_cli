import time
import os
import re
from playwright.sync_api import sync_playwright

USER_DATA_DIR = os.path.join(os.path.expanduser("~"), ".grant_cli_google_session")

def authenticate_google():
    """
    Opens a headed browser for the user to login manually.
    Stores the session persistently so future scripts can run headless.
    """
    print(f"Opening browser for Google Authentication. Please log in.")
    print(f"Session will be saved locally to {USER_DATA_DIR}")
    
    with sync_playwright() as p:
        # Launch persistent context
        browser = p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False,
            channel="chrome", # Often Google auth works better with standard Chrome
            ignore_default_args=['--enable-automation'],
            args=['--disable-blink-features=AutomationControlled']
        )
        
        page = browser.new_page()
        page.goto("https://accounts.google.com/signin")
        
        print("\n--- ACTION REQUIRED ---")
        print("1. Log in to your Google Account in the browser window.")
        print("2. Once you are successfully logged in and redirected, press Enter here.")
        input("Press Enter to save session and close browser...")
        
        browser.close()
        print("Session saved. You can now run the build command.")

def build_google_site(business_profile: dict, design_prefs: dict, pages: list):
    """
    Uses the persistent session to log into Google Sites and automate creation.
    """
    print("Starting automated Google Site build...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False, # Set to False initially for observation, can be True later
            channel="chrome",
            ignore_default_args=['--enable-automation'],
            args=['--disable-blink-features=AutomationControlled']
        )
        
        page = browser.new_page()
        
        # 1. Navigate to Google Sites
        print("Navigating to Google Sites...")
        page.goto("https://sites.google.com/")
        
        # 2. Click "Blank" to create a new site
        try:
            print("Creating blank site...")
            # Wait for the template gallery to load and click "Blank site"
            print("Trying to find the 'Blank site' button...")
            # Use a robust locator: The entire template card
            blank_button = page.locator("div[role='option']").filter(has_text="Blank").first
            blank_button.click(timeout=15000)
            
            print("Waiting for site editor canvas to load...")
            # Wait for url to change indicating we left the gallery
            try:
                page.wait_for_url(re.compile(r".*/site/.*|.*/edit.*|.*/d/.*"), timeout=15000)
            except Exception:
                print("Navigation wait timed out, proceeding anyway...")
            
            # Additional sleep just to let the heavy JS canvas initialize
            time.sleep(5)
            
            # 3. Apply Name
            site_name = business_profile.get('name', 'My Business')
            print(f"Setting site document name to: {site_name}")
            try:
                # The container has aria-label="Site document name: Untitled site"
                doc_name_container = page.locator("div[aria-label^='Site document name']").first
                
                # We need to click the container to make the input active/visible
                doc_name_container.click(timeout=15000)
                
                # Now target the actual input inside the container
                doc_name_input = doc_name_container.locator("input").first
                doc_name_input.click(timeout=5000)
                doc_name_input.fill(site_name)
                doc_name_input.press("Enter")
                print(f"Set site name to {site_name}")
            except Exception as e:
                print(f"Failed to set site name: {e}")
                
            time.sleep(2)
            
            # 4. Apply title
            print("Applying page title...")
            try:
                # Often it's an element containing the specific placeholder text
                # We can try to locate it using the placeholder text
                title_box = page.locator("text=Your page title").first
                
                # If not visible, try inside all frames
                if not title_box.is_visible(timeout=5000):
                    print("Title box not immediately visible in main frame. Trying frame locators...")
                    for iframe in page.main_frame.child_frames:
                        title_box = iframe.locator("text=Your page title").first
                        if title_box.is_visible(timeout=1000):
                            print(f"Found title in iframe: {iframe.name}")
                            break

                title_box.click(timeout=10000)
                title_val = pages[0].get('title', 'Welcome') if pages else 'Welcome'
                # Clear existing text and type new text
                page.keyboard.press("Control+A")
                page.keyboard.press("Meta+A") # mac
                page.keyboard.press("Backspace")
                page.keyboard.type(title_val)
                print(f"Set page title to {title_val}")
            except Exception as e:
                print(f"Failed to set page title: {e}")
            
            # 5. Switch to Themes tab and apply theme
            print("Applying theme...")
            try:
                # Use simple text matching which pierces shadow DOM
                page.locator("text=Themes").last.click(timeout=8000, force=True)
                time.sleep(2)
                
                theme_name = design_prefs.get('theme', 'simple').capitalize()
                # Text match is most reliable for shadow DOM pierce
                page.locator(f"text={theme_name}").last.click(timeout=5000, force=True)
                print(f"Applied theme {theme_name}")
            except Exception as e:
                print(f"Failed to set theme: {e}")
                
            time.sleep(1)
            
            # 6. Add Pages
            print(f"\\nAdding {len(pages)} pages...")
            try:
                page.locator("text=Pages").last.click(timeout=8000)
                time.sleep(2)
                
                for idx, p in enumerate(pages):
                    title = p.get('title', f"Page {idx}")
                    # Skip the first page (assumed Home)
                    if idx == 0:
                        print(f"Skipping creation for first page (assumed Home): {title}")
                        continue
                    
                    print(f"Creating new page: {title}")
                    
                    # Hover over the + button. 
                    add_btn_group = page.locator("[aria-label='Create'], [aria-label='New page']").last
                    if add_btn_group.is_visible():
                         add_btn_group.hover()
                         time.sleep(1)
                    
                    new_page_btn = page.locator("text=New page").first
                    if new_page_btn.is_visible():
                        new_page_btn.click(timeout=5000, force=True)
                    else:
                        add_btn_group.click(timeout=5000, force=True)
                    
                    time.sleep(1)
                    # Google sites automatically focuses the new page name input
                    page.keyboard.type(title)
                    time.sleep(1)
                    page.keyboard.press("Enter")
                    time.sleep(3)
            except Exception as e:
                print(f"Failed to add pages: {e}")
                
            # 7. Add Content blocks
            print("\nAdding content blocks...")
            try:
                page.locator("text=Insert").last.click(timeout=8000, force=True)
                time.sleep(1)
                
                for p in pages:
                    # In a real scenario, you'd navigate back to the specific page first here.
                    # Currently we just add to the active page (the last created).
                    if 'text_block' in p:
                        print(f"Adding text block: {p['text_block'][:30]}...")
                        # Click "Text box" - simple text matching
                        page.locator("text=Text box").last.click(timeout=5000, force=True)
                        time.sleep(1)
                        # Type text (Google sites automatically focuses the new text box)
                        page.keyboard.type(p['text_block'])
                        time.sleep(1)
            except Exception as e:
                print(f"Failed to add content blocks: {e}")
            
            print("Simulated Build Complete! Google's canvas UI requires intensive selector mapping.")
            print("For full implementation, each canvas component needs precise XPath/aria tracking.")
            
            # Keep browser open a bit to let the user see the result
            time.sleep(10)
            
        except Exception as e:
            print(f"Error during automation: {e}")
            print("UI may have updated or login session is expired/invalid.")
            
        finally:
            browser.close()
            print("Browser closed.")
