import os
import random

from robocorp.tasks import task, teardown
from robocorp import browser
from RPA.Excel.Files import Files
from RPA.Tables import Tables
from RPA.Email.ImapSmtp import ImapSmtp 

# Predefined job search keywords agreed by the team.
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
    try:
        # 1. Start Navigation (Module 1)
        active_page = scrape_linkedin_task()

        #If LinkedIn page could not be opened, trat it as a real error.
        if not active_page:
            raise Exception("Could not initialize LinkedIn page.")
    
        # 2. Start Search (Module 2)
        all_jobs = []

        for keyword in SEARCH_KEYWORDS:
            success = search_linkedin(active_page, keyword)

            if success:
                jobs = extract_jobs()
                all_jobs.extend(jobs)
        
                # Small delay to mimic human behavior and reduce blocking risk
                active_page.wait_for_timeout(random.randint(4000, 9000))
            else:
                #This doesn't stop the whole robot. I only means this one keyword search failed.
                print(f"Search failed for keyword: {keyword}")
                  
        create_data_excel()
        new_jobs_table = compare_jobs(all_jobs)
        added_count = write_new_jobs(new_jobs_table)

        #Send notification only if new jobs were added
        if added_count > 0:
            send_notif_email()
        else:
            print("No notification sent because no new jobs were found.")

    except Exception as e:
        #If any critical error happens anywhere in the main flow, print it to terminal and notify user by email.
        print(f"Robot failed: {e}")
        send_error_email(str(e))

def scrape_linkedin_task():
    """
    Initializes the browser and navigates to LinkedIn Jobs.
    Handles cookie banners and sign-in modals.
    Returns: page object if successful, none otherwise.
    """
    # Configure browser visibility and speed
    browser.configure(headless=False, slowmo=500)
    try:
        print("Step 1: Navigating to LinkedIn...")
        page = browser.goto("https://fi.linkedin.com/jobs/jobs-in-finland?position=1&pageNum=0")
        close_x_button = "button[aria-label='Dismiss'], button[aria-label='Sulje']"
        accept_btn = "button:has-text('Hyväksy'), button:has-text('Accept')"
        page.wait_for_timeout(3000) 
        if page.is_visible(close_x_button):
            page.click(close_x_button)
        if page.is_visible(accept_btn):
            page.click(accept_btn, force=True)
        return page
    
    except Exception as e:
        print(f"Error in scrape_linkedin_task: {e}")
        return None

def search_linkedin(page, job_title, location="Finland"):
    """Searches LinkedIn jobs using the given keyword."""
    page.goto("https://fi.linkedin.com/jobs/jobs-in-finland?position=1&pageNum=0")
    page.wait_for_timeout(5000)
    if "authwall" in page.url:
        print("Authwall detected. Skipping keyword.")
        return False
    job_input_selector = "input[name='keywords']" 
    location_input_selector = "input[name='location']"
    try:
        print(f"Step 2: Searching for '{job_title}'...")
        page.wait_for_selector(job_input_selector, timeout=10000)
        page.fill(job_input_selector, job_title)
        page.fill(location_input_selector, location)
        page.press(location_input_selector, "Enter")
        page.wait_for_load_state("networkidle")
        print("Status: Search results loaded.")

        return True
        
    except Exception as e:
        print(f"Error in search_linkedin: {e}")
        return False


def extract_jobs():
    """Extracts job data from the page."""
    page = browser.page()
    job_cards = page.locator("div.base-search-card")
    count = job_cards.count()
    jobs = []

    for i in range(count):
        card = job_cards.nth(i)

        title_element = card.locator("h3.base-search-card__title")
        if title_element.count() > 0:
            title = title_element.first.inner_text().strip()
        else:
            title = ""

        company_element = card.locator("h4.base-search-card__subtitle")
        if company_element.count() > 0:
            company = company_element.first.inner_text().strip()
        else:
            company = ""

        location_element = card.locator("span.job-search-card__location")
        if location_element.count() > 0:
            location = location_element.first.inner_text().strip()
        else:
            location = ""
        
        link_element = card.locator("a.base-card__full-link")
        if link_element.count() > 0:
            href = link_element.first.get_attribute("href")

            if href:
                link = href.strip()
            else:
                link = ""
        else:
            link = ""

        #Skip job if link is missing, because link is used as unique identifier
        if not link:
            continue 
        
        jobs.append({
            "Company": company,
            "Title": title,
            "Location": location,
            "Deadline": "",
            "Link": link
    })    

    return jobs

def create_data_excel():
    """Creates an excel workbook in the output folder."""
    lib = Files()
    file_path = 'output/data.xlsx'
    headers = [{"Company": "", "Title": "", "Location": "", "Deadline": "", "Link": ""}]
    if os.path.exists(file_path):
        print("Data excel exists in output.")
        lib.open_workbook(file_path)
    else:
        print("Creating new data.xlsx in output.")
        lib.create_workbook(path=file_path, fmt="xlsx")
        lib.create_worksheet(name="Jobs", content=headers, header=True)
        lib.save_workbook()

def compare_jobs(jobs):
    """Read from excel and compare with new data, store new jobs to the main file. 
    Returns a table containing nly new job entries based on unique links
    """
    
    lib = Files()
    tables = Tables()
    
    def normalize(link):
        return link.strip().rstrip("/").split("?")[0]

    # Transform the new jobs list in to a table
    new_links = tables.create_table(jobs)
        
    # Read excel and get old job links as a table
    lib.open_workbook("output/data.xlsx")
    existing_table = lib.read_worksheet_as_table(header=True)

    existing_links = {
        normalize(row["Link"])
        for row in existing_table
        if row.get("Link")
    }

    # See if links matches between tables    
    new_job_rows = []

    for row in new_links:
        link = row.get("Link")
        if link and normalize(link) not in existing_links:
            new_job_rows.append(row)
 
    new_jobs_table = tables.create_table(new_job_rows)
    return new_jobs_table
    

def write_new_jobs(new_jobs_table):
    """
    Write the new jobs in to the existing excel.
    """
    lib = Files()
    tables = Tables()

    # Table in to a list.
    rows = tables.export_table(new_jobs_table)
   
    if not rows:
        print("No new jobs found")
        return 0
        
    lib.open_workbook("output/data.xlsx")
    lib.append_rows_to_worksheet(rows, header=False)
    lib.save_workbook("output/data.xlsx")

    print(f"Added {len(rows)} new jobs.")
    return len(rows)

def send_notif_email():
    """Sends notification via SMTP (Mac/PC/Cloud compatible)."""
    mail = ImapSmtp()
    
    try:
        # mail.authorize(account="email", password="app_password", smtp_server="smtp.gmail.com")
        # mail.send_message(...)
        print("Email: Function prepared, needs credentials to send.")
    except Exception as e:
        print(f"Email Error: {e}")
    """Send notification by email to user, if new jobs has been found"""

#    app = Application()
#    app.open_application()
#    app.send_email(
#        recipients='EMAIL_1, EMAIL_2',
#        subject='New job listings found!',
#        body='StudentJob Robot has found new job listings. Check them out!',
#        attachments=os.path.join(os.path.curdir, "output/data.xlsx")
#    )

def send_error_email(error_message):
    """Send error notification email to user."""

#    try: 
#        app = Application()
#        app.open_application()
#        app.send_email(
#            recipients='EMAIL_1, EMAIL_2',
#            subject='StudentJob Robot ERROR',
#            body=f'Robot encountered an error:\n\n{error_message}'
#        )
#        print("Error email sent.")
    
#    except Exception as e:
#        print(f"Failed to send error email: {e}")
    print(f"Robot error: {error_message}")
    
@teardown
def cleanup(task):
    """Closes browser safely."""
    try:
        browser.get_browser().close()
    except:
        pass
