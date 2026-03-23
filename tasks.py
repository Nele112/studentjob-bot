from robocorp.tasks import task
from robocorp import browser
from RPA.Excel.Files import Files
@task
def student_job_robot():
    browser.configure(
        slowmo = 100,
    )
    search_linkedin()
    extract_data()
    compare_data()

def compare_data():
    open_data_excel()
    compare_jobs()
    write_new_jobs()
    notify_user_by_email()
    
def open_data_excel():
    lib = Files()
    lib.open_workbook(path="data.xlsx")