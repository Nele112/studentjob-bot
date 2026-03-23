import os
from robocorp.tasks import task
from robocorp import browser
from RPA.Excel.Files import Files

@task
def student_job_robot():
    browser.configure(
        slowmo = 100,
    )
    search_linkedin()
    jobs = extract_jobs() # Extract job listings from the current page and store them in a list
    compare_data(jobs)    # Pass the extracted jobs to the next step for comparison with existing data

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
    """ -opens current page, -finds all job listings, -iterates through each job, -extracts job links from the current linkedin results page
        -stores them in a list, -returns the list """
    page = browser.page()
    job_elements = page.locator("a.base-card__full-link")
    count = job_elements.count()
    jobs = []
    for i in range(count):
        job = job_elements.nth(i)
        link = job.get_attribute ("href")
        jobs.append( {
            "Link" : link
        })

    return jobs

def compare_data():
    create_data_excel()
    compare_jobs()
    write_new_jobs()
    notify_user_by_email()
    
def create_data_excel():
    """Creates an excel workbook if one is not already in place"""
    lib = Files()
    file_path = './data.xlsx'
    headers = [{"Company": "", "Title": "", "Location": "", "Deadline": "", "Link": ""}]
    jobs_list = get_jobs()
    if os.path.exists(file_path):
        print("Data excel exists, proceeding to open.")
        lib.open_workbook(path="data.xlsx")
        lib.save_workbook()
    else:
        print("Data excel does not exist, creating a new one.")
        lib.create_workbook(path="./data.xlsx", fmt="xlsx")
        lib.create_worksheet(name="Jobs",content=headers, header=True)
        lib.save_workbook()

def compare_jobs():
    """Read from excel and compare with new data, store new jobs to the main file"""
    lib = Files()
    lib.open_workbook("data.xlsx")
    rows = lib.read_worksheet_as_table(header=True)
    existing_links = [row["Link"].strip()
                      for row in rows if row["Link"]]
    print(existing_links)