import os
import random

from robocorp.tasks import task, teardown
from robocorp import browser
from RPA.Excel.Files import Files
from RPA.Tables import Tables
from RPA.Email.ImapSmtp import ImapSmtp # Vaihdettu Mac-yhteensopivaksi

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
    # 1. Start Navigation (Module 1)
    active_page = scrape_linkedin_task()
    
    if active_page:
        # 2. Start Search (Module 2)
        all_jobs = []

        for keyword in SEARCH_KEYWORDS:
            search_linkedin(active_page, keyword)
            jobs = extract_jobs()
            all_jobs.extend(jobs)
            # Small delay to mimic human behavior and reduce blocking risk
            active_page.wait_for_timeout(random.randint(4000, 9000))
        
        # 3. Continue to data extraction and Excel processing
        print("Navigation and search successful. Starting extraction...")
        
        create_data_excel()
        new_jobs_table = compare_jobs(all_jobs)
        write_new_jobs(new_jobs_table)
        
        # HUOM: Sähköposti vaatii SMTP-asetukset toimiakseen (ks. funktio lopussa)
        # send_notif_email() 

    else:
        print("Robot execution stopped: Could not initialize the LinkedIn page.")

def scrape_linkedin_task():
    """Initializes the browser and navigates to LinkedIn Jobs."""
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
        return True
    except Exception as e:
        print(f"Error in search_linkedin: {e}")
        return False

@teardown
def cleanup(task):
    """Closes browser safely."""
    try:
        browser.get_browser().close()
    except:
        pass

def extract_jobs():
    """Extracts job data from the page."""
    page = browser.page()
    job_cards = page.locator("div.base-search-card")
    jobs = []
    for i in range(job_cards.count()):
        card = job_cards.nth(i)
        title = card.locator("h3.base-search-card__title").first.inner_text().strip() if card.locator("h3.base-search-card__title").count() > 0 else ""
        company = card.locator("h4.base-search-card__subtitle").first.inner_text().strip() if card.locator("h4.base-search-card__subtitle").count() > 0 else ""
        location = card.locator("span.job-search-card__location").first.inner_text().strip() if card.locator("span.job-search-card__location").count() > 0 else ""
        link_el = card.locator("a.base-card__full-link").first
        link = link_el.get_attribute("href").strip() if link_el.count() > 0 else ""
        if link:
            jobs.append({"Company": company, "Title": title, "Location": location, "Deadline": "", "Link": link})
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
    """Compares new data with existing Excel."""
    lib = Files()
    tables = Tables()
    def normalize(link): return link.strip().rstrip("/").split("?")[0]
    new_links = tables.create_table(jobs)
    lib.open_workbook("output/data.xlsx")
    existing_table = lib.read_worksheet_as_table(header=True)
    existing_links = {normalize(row["Link"]) for row in existing_table if row.get("Link")}
    new_job_rows = [row for row in new_links if row.get("Link") and normalize(row["Link"]) not in existing_links]
    return tables.create_table(new_job_rows)

def write_new_jobs(new_jobs_table):
    """Writes new entries to Excel."""
    lib = Files()
    tables = Tables()
    rows = tables.export_table(new_jobs_table)
    if not rows:
        print("No new jobs found")
        return
    lib.open_workbook("output/data.xlsx")
    lib.append_rows_to_worksheet(rows, header=False)
    lib.save_workbook("output/data.xlsx")
    print(f"Added {len(rows)} new jobs.")

def send_notif_email():
    """Sends notification via SMTP (Mac/PC/Cloud compatible)."""
    mail = ImapSmtp()
    # TÄHÄN TARVITAAN OMAT TUNNUKSET JOTTA TOIMII:
    try:
        # mail.authorize(account="email", password="app_password", smtp_server="smtp.gmail.com")
        # mail.send_message(...)
        print("Email: Function prepared, needs credentials to send.")
    except Exception as e:
        print(f"Email Error: {e}")