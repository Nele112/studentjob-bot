import os
from robocorp.tasks import task
from robocorp import browser
from RPA.Excel.Files import Files
from RPA.Tables import Tables

@task
def student_job_robot():
    browser.configure(
        slowmo = 100,
    )
    search_linkedin()
    jobs = extract_jobs() # Extract job listings from the current page and store them in a list
    create_data_excel()
    compare_jobs(jobs)    # Pass the extracted jobs to the next step for comparison with existing data
    new_jobs_table = compare_jobs()
    write_new_jobs(new_jobs_table)

def search_linkedin():
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
        for row in tables.iterate_table_rows(existing_table)
        if row.get("Link")
    }
    """Read excel and get old job links as a table"""
    
    new_job_rows = []
    for row in tables.iterate_table_rows(new_links):
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