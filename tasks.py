import os
import random

from robocorp.tasks import task, teardown
from robocorp import browser
from RPA.Excel.Files import Files
from RPA.Tables import Tables
from RPA.Email.ImapSmtp import ImapSmtp 
from robocorp import storage

# Email settings for SMTP sending.
# Use a separate robot email account, not your personal main email.
EMAIL_ACCOUNT = ""
EMAIL_PASSWORD = ""
EMAIL_RECIPIENTS = ""

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

        #If LinkedIn page could not be opened, treat it as a real error.
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
        print(f"Step 3: Extraction completed. Total collected jobs: {len(all_jobs)}")          
        
        print("Step 4: Preparing Excel data file...")
        create_data_excel()

        print("Step 5: Comparing jobs and updating Excel...")
        new_jobs_table = compare_jobs(all_jobs)
        added_count = write_new_jobs(new_jobs_table)

        #Send notification only if new jobs were added
        if added_count > 0:
            send_notif_email(added_count)
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
        print(f"Status: Search completed for '{job_title}'.")

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
        print("Status: Excel data found in output.")
        lib.open_workbook(file_path)
        lib.close_workbook()
    else:
        print("Creating new data.xlsx in output.")
        lib.create_workbook(path=file_path, fmt="xlsx")
        lib.create_worksheet(name="Jobs", content=headers, header=True)
        lib.save_workbook()
        lib.close_workbook()

def get_seen_links():
    """Load previously seen job links from Control Room asset storage.
    Returns a set of normalized link. If the asset is missing or unreadable, returns an empty set.
    """
    try:
        data = storage.get_json("studentjob_seen_links")
        return set(data)
    except Exception:
        return set()
    

def compare_jobs(jobs):
    """Compare extracted jobs against previously seen job links stored in Control Room asset storage.
    Returns a table containing only new job entries based on normalized unique links.
    Also updates the stored link set so future runs can skip already seen jobs.
    """
    tables = Tables()
    
    def normalize(link):
        """Normalize LinkedIn job links for reliable duplicate comparison."""
        return link.strip().rstrip("/").split("?")[0]

    # Transform the new jobs list in to a table
    new_links = tables.create_table(jobs)
        
    #Load previously seen links form persistent asset storage.
    existing_links = get_seen_links()

    # See if links matches between tables    
    new_job_rows = []
    new_links_set = set()

    for row in new_links:
        link = row.get("Link")
        if link:
            clean = normalize(link)
            new_links_set.add(clean)

            if clean not in existing_links:
                new_job_rows.append(row)
 
    #Update persistent storage with both old and newly seen links
    all_links = existing_links.union(new_links_set)
    storage.set_json("studentjob_seen_links", list(all_links))
    
    return tables.create_table(new_job_rows)
    

def write_new_jobs(new_jobs_table):
    """
    Write the new jobs in to the existing excel.
    """
    lib = Files()
    tables = Tables()

    # Table in to a list.
    rows = tables.export_table(new_jobs_table)
   
    if not rows:
        print("Status: No new jobs found")
        return 0
        
    lib.open_workbook("output/data.xlsx")
    lib.append_rows_to_worksheet(rows, name="Jobs", header=False)
    lib.save_workbook("output/data.xlsx")
    lib.close_workbook()

    print(f"Added {len(rows)} new jobs.")
    return len(rows)

def send_email(subject, body, attachment_path=None):
    """Generic function for sending emails through SMTP.
    """
    mail = ImapSmtp()

    try:
        mail.authorize(
            account=EMAIL_ACCOUNT,
            password=EMAIL_PASSWORD,
            smtp_server="smtp.gmail.com",
            smtp_port=587
        )

        if attachment_path and os.path.exists(attachment_path):
            mail.send_message(
                sender=EMAIL_ACCOUNT,
                recipients=EMAIL_RECIPIENTS,
                subject=subject,
                body=body,
                attachments=attachment_path
            )
        else:
            mail.send_message(
                sender=EMAIL_ACCOUNT,
                recipients=EMAIL_RECIPIENTS,
                subject=subject,
                body=body
            )

        print(f"Notification email process completed: {subject}")

    except Exception as e:
        print("❌ EMAIL ERROR ❌")
        print(f"Failed to send email: {e}")
        print(f"Account: {EMAIL_ACCOUNT}")
        print("Check SMTP credentials and App Password.")

def send_notif_email(added_count):
    """Sends notification via SMTP (Mac/PC/Cloud compatible)."""
    
    subject = "StudentJob bot: New job listings found"
    body = (f"StudentJob Robot found {added_count} new job listing(s).\n\n"
        "Please check the attached Excel file for details."
    )
    
    send_email(
        subject=subject,
        body=body,
        attachment_path="output/data.xlsx"
    )


def send_error_email(error_message):
    """Send error notification email to user."""

    subject = "StudentJob bot ERROR"
    body = ("The robot encountered a critical error during execution.\n\n"
        f"Error details:\n{error_message}"
    )

    send_email(subject=subject, body=body)
    print(f"Robot error: {error_message}")

    
@teardown
def cleanup(task):
    """Closes browser safely."""
    try:
        browser.get_browser().close()
    except Exception:
        pass
