def search_linkedin(page, job_title="(Junior OR Trainee OR Internship) AND (Software OR Developer OR IT)", location="Finland"):
    """Suorittaa haun annetulla sivulla."""
    
    job_input_selector = "input[name='keywords']" 
    location_input_selector = "input[name='location']"

    print(f"Searching for: {job_title} in {location}")

    try:
        page.wait_for_selector(job_input_selector, timeout=10000)
        
        # Täytetään haku
        page.fill(job_input_selector, job_title)
        page.fill(location_input_selector, location)
        
        # Painetaan Enter
        page.press(location_input_selector, "Enter")
        
        page.wait_for_load_state("networkidle")
        print("Search initialized and results loaded.")
        
    except Exception as e:
        print(f"Error during search execution in Mod 2: {e}")