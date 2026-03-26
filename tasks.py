from robocorp.tasks import task
from robocorp import browser
# Import your custom modules (ensure filenames match exactly)
from linkedin_scraper_1 import scrape_linkedin_task
from linkedin_search_2 import search_linkedin

@task
def main_linkedin_flow():
    """
    Main robot orchestrator:
    1. Initializes browser and handles entry (Module 1)
    2. Performs the job search (Module 2)
    """
    
    # Step 1: Navigation and bypass popups
    # This returns the 'page' object which is passed to the next step
    page = scrape_linkedin_task()
    
    if page:
        # Step 2: Search for jobs
        # Using default Boolean query and location defined in the module
        search_linkedin(page)
        
        print("Robot successfully navigated and performed the search.")
    else:
        print("Robot failed to initialize or bypass LinkedIn entry barriers.")

# The '@task' decorator above tells Robocorp that this is the entry point