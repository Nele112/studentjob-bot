def search_linkedin(page, job_title="(Junior OR Trainee OR Internship) AND (Software OR Developer OR IT)", location="Finland"):
    """
    Performs a job search on LinkedIn using Boolean operators and location.
    
    Args:
        page: The active Playwright page object.
        job_title (str): The search query for job titles.
        location (str): The geographic area for the search.
    """
    
    # Language-independent technical selectors (name attributes)
    job_input_selector = "input[name='keywords']" 
    location_input_selector = "input[name='location']"

    print(f"Searching for: {job_title} in {location}")

    try:
        # Wait for the search inputs to be ready
        page.wait_for_selector(job_input_selector, timeout=10000)
        
        # Fill search criteria
        page.fill(job_input_selector, job_title)
        page.fill(location_input_selector, location)
        
        # Execute search by pressing Enter in the location field
        page.press(location_input_selector, "Enter")
        
        # Wait for the result listing to load
        page.wait_for_load_state("networkidle")
        print("Search initialized and results loaded.")
        
    except Exception as e:
        print(f"Error during search execution: {e}")