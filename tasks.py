import os
import random
from robocorp.tasks import task, teardown
from robocorp import browser
from RPA.Excel.Files import Files
from RPA.Tables import Tables
from RPA.Outlook.Application import Application

SEARCH_KEYWORDS = [
    "it trainee",
    "it harjoittelija",
    "it intern",
    "it internship"
]

@task
def student_job_robot():
    """
    Main task that orchestrates the LinkedIn scraping and job processing flow.
    """
    # 1. Start Navigation (Module 1)
    active_page = scrape_linkedin_task()
    
    if active_page:
        # 2. Start Search (Module 2)
        all_jobs = []

        for keyword in SEARCH_KEYWORDS:
            search_linkedin(active_page, keyword)
            jobs = extract_jobs()
            all_jobs.extend(jobs)
            active_page.wait_for_timeout(random.randint(4000, 9000))
        
        # 3. Continue to data extraction and Excel processing
        # Note: These functions must exist later in your tasks.py file
        print("Navigation and search successful. Starting extraction...")
        
        create_data_excel()
        new_jobs_table = compare_jobs(all_jobs)
        write_new_jobs(new_jobs_table)
        send_notif_email()
    else:
        print("Robot execution stopped: Could not initialize the LinkedIn page.")

def scrape_linkedin_task():
    """
    Initializes the browser and navigates to LinkedIn Jobs.
    Handles cookie banners and sign-in modals.
    Returns: The active page object.
    """
    # Configure browser visibility and speed
    browser.configure(headless=False, slowmo=500)
    
    try:
        print("Step 1: Navigating to LinkedIn...")
        page = browser.goto("https://fi.linkedin.com/jobs/jobs-in-finland?position=1&pageNum=0")
        
        # Selectors for modals and banners
        close_x_button = "button[aria-label='Dismiss'], button[aria-label='Sulje']"
        accept_btn = "button:has-text('Hyväksy'), button:has-text('Accept')"
        
        page.wait_for_timeout(3000) 
        
        # Dismiss sign-in popup
        if page.is_visible(close_x_button):
            page.click(close_x_button)
            print("Status: Login popup dismissed.")
        
        # Accept cookies
        if page.is_visible(accept_btn):
            page.click(accept_btn, force=True)
            print("Status: Cookies accepted.")
            
        return page
            
    except Exception as e:
        print(f"Error in scrape_linkedin_task: {e}")
        return None

def search_linkedin(page, job_title, location="Finland"):
    """
    Performs a job search on the provided page object.
    """
    page.goto("https://fi.linkedin.com/jobs/jobs-in-finland?position=1&pageNum=0")
    page.wait_for_timeout(5000)

    if "authwall" in page.url:
        print("Authwall detected. Skipping this keyword.")
        return False
    
    job_input_selector = "input[name='keywords']" 
    location_input_selector = "input[name='location']"

    try:
        print(f"Step 2: Searching for '{job_title}' in '{location}'...")
        page.wait_for_selector(job_input_selector, timeout=10000)
        
        # Fill search criteria
        page.fill(job_input_selector, job_title)
        page.fill(location_input_selector, location)
        
        # Execute search
        page.press(location_input_selector, "Enter")
        
        # Wait for the result listing to load
        page.wait_for_load_state("networkidle")
        print("Status: Search results loaded.")

        return True
        
    except Exception as e:
        print(f"Error in search_linkedin: {e}")
        return False

@teardown
def cleanup(task):
    """Closes all browser instances after the task finishes."""
    browser.close_all()

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
        print("No new jobs found")
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