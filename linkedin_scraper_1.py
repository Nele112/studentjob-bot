from robocorp import browser
from robocorp.tasks import task

@task
def scrape_linkedin_task():
    """1. Opens web browser, 2. Opens LinkedIn, 3. Handles cookies 4. Handles Sign in pop up"""
    
    # Configures the browser visibility (dev mode)
    browser.configure(
        headless=False,
        slowmo=1000
    )
    
    try:
        # 1&2. Opens browser/website
        page = browser.goto("https://fi.linkedin.com/jobs/jobs-in-finland?position=1&pageNum=0")
        
        # 3. Handles popups (Cookies)
        accept_button = "button:has-text('Accept')"

        # 4. Handles the "Sign in" popup 
        close_popup_button = "button[aria-label='Dismiss']" # LinkedInin yleinen sulkunappi
        
        # Waits for the "Sign in" popup
        page.wait_for_timeout(2000) 
        
        if page.is_visible(close_popup_button):
            page.click(close_popup_button)
            print("Login popup dismissed.")
        
        # Waits for the button to appear
        page.wait_for_selector(accept_button, timeout=10000)
        
        if page.is_visible(accept_button):
            page.click(accept_button)
            print("Cookie banner accepted.")
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
        scrape_linkedin_task()
