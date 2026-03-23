import os
from robocorp.tasks import task
from robocorp import browser
from RPA.Excel.Files import Files
from extract import extract_jobs, get_jobs
@task
def student_job_robot():
    browser.configure(
        slowmo = 100,
    )
    search_linkedin()
    extract_jobs()
    compare_data()

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