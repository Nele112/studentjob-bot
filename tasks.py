import os
from robocorp.tasks import task
from robocorp import browser
from RPA.Excel.Files import Files
from RPA.Tables import Tables
from RPA.Outlook.Application import Application

@task
def student_job_robot():
    browser.configure(
        slowmo = 100,
    )
    scrape_linkedin_task()
    jobs = extract_jobs() # Extract job listings from the current page and store them in a list
    create_data_excel()
    compare_jobs(jobs)    # Pass the extracted jobs to the next step for comparison with existing data
    new_jobs_table = compare_jobs(jobs)
    write_new_jobs(new_jobs_table)
    send_notif_email()

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

def extract_jobs():
    """ Extracts job data from the current LinkedIn results page. """
    page = browser.page()

    #Locate all job cards on the page
    job_cards = page.locator("div.base-search-card")
    count =job_cards.count()
    jobs = []

    #Loop though each job card and extract data
    for i in range(count):
        card = job_cards.nth(i)

        #Extract job title
        title_element = card.locator("h3.base-search-card__title")
        if title_element.count() > 0:
            title = title_element.first.inner_text().strip()
        else:
            title = ""

        #Extract company name
        company_element = card.locator("h4.base-search-card__subtitle")
        if company_element.count() > 0:
            company = company_element.first.inner_text().strip()
        else:
            company = ""

        #Extract location
        location_element = card.locator("span.job-search-card__location")
        if location_element.count() > 0:
            location = location_element.first.inner_text().strip()
        else:
            location = ""
        
        #Extract link (used as unique identifier)
        link_element = card.locator("a.base-card__full-link")
        if link_element.count() > 0:
            href = link_element.first.get_attribute("href")

            if href:
                link = href.strip()
            else:
                link = ""
        else:
            link = ""

        #Skip job if link is missing
        if not link:
            continue 
        
        #Add extracted data to jobs list
        jobs.append({
            "Company": company,
            "Title": title,
            "Location": location,
            "Deadline": "",
            "Link": link
    })    

    return jobs
   

    
def create_data_excel():
    """Creates an excel workbook if one is not already in place"""
    lib = Files()
    file_path = './data.xlsx'
    headers = [{"Company": "", "Title": "", "Location": "", "Deadline": "", "Link": ""}]
    if os.path.exists(file_path):
        print("Data excel exists, proceeding to open.")
        lib.open_workbook(path="data.xlsx")
        lib.save_workbook()
    else:
        print("Data excel does not exist, creating a new one.")
        lib.create_workbook(path="./data.xlsx", fmt="xlsx")
        lib.create_worksheet(name="Jobs",content=headers, header=True)
        lib.save_workbook()


def compare_jobs(jobs):
    """Read from excel and compare with new data, store new jobs to the main file"""
    
    lib = Files()
    tables = Tables()
    
    def normalize(link):
        return link.strip().rstrip("/").split("?")[0]

    new_links = tables.create_table(jobs)
    """Transform the new jobs list in to a table"""
    
    lib.open_workbook("data.xlsx")
    existing_table = lib.read_worksheet_as_table(header=True)
    existing_links = {
        normalize(row["Link"])
        for row in existing_table
        if row.get("Link")
    }
    """Read excel and get old job links as a table"""
    
    new_job_rows = []
    for row in new_links:
        link = row.get("Link")
        if link and normalize(link) not in existing_links:
            new_job_rows.append(row)
    """See if links matches between tables"""

    new_jobs_table = tables.create_table(new_job_rows)
    return new_jobs_table
    

def write_new_jobs(new_jobs_table):
    """Write the new jobs in to the existing excel"""
    lib = Files()
    tables = Tables()

    rows = tables.export_table(new_jobs_table)
    """Table in to a list"""

    if not rows:
        print("Now new jobs found")
        return
    
    lib.open_workbook("data.xlsx")
    lib.append_rows_to_worksheet(
        rows,
        header=False
    )

    lib.save_workbook("data.xlsx")
    print(f"Added {len(rows)} new jobs.")

def send_notif_email():
    """Send notification by email to user, if new jobs has been found"""
    app = Application()
    app.open_application()
    app.send_email(
        recipients='EMAIL_1, EMAIL_2',
        subject='New job listings found!',
        body='StudentJob Robot has found new job listings. Check them out!',
        attachments=os.path.join(os.path.curdir, "data.xlsx")
    )