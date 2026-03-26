from robocorp import browser

def scrape_linkedin_task():
    """
    Initializes the browser and navigates to the LinkedIn Job search page.
    Handles entry barriers including cookie banners and login modals.
    
    Returns:
        page: The active browser page object if successful, None otherwise.
    """
    # Configure browser for visibility during development
    browser.configure(headless=False, slowmo=1000)
    
    try:
        # Navigate to the initial job search URL
        page = browser.goto("https://fi.linkedin.com/jobs/jobs-in-finland?position=1&pageNum=0")
        
        # Selectors for interaction
        close_x_button = "button[aria-label='Dismiss'], button[aria-label='Sulje']"
        accept_btn = "button:has-text('Hyväksy'), button:has-text('Accept')"
        
        print("Waiting for potential pop-ups...")
        # Static wait to allow the login modal to fully initialize
        page.wait_for_timeout(3000) 
        
        # 1. Dismiss the 'Sign in' modal if it appears
        if page.is_visible(close_x_button):
            page.click(close_x_button)
            print("Login popup dismissed.")
            page.wait_for_timeout(1000) # Short pause for the overlay to vanish
        
        # 2. Accept cookies to clear the view
        if page.is_visible(accept_btn):
            # Using force=True to bypass any remaining transparent overlays
            page.click(accept_btn, force=True)
            print("Cookies accepted.")

        return page
            
    except Exception as e:
        print(f"Error during navigation and entry: {e}")
        return None