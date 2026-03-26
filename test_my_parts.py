from robocorp.tasks import task, teardown
from robocorp import browser
from linkedin_scraper_1 import scrape_linkedin_task
from linkedin_search_2 import search_linkedin

@task
def run_my_test_flow():
    # 1. Konfigurointi
    browser.configure(slowmo=500)
    
    # 2. Moduuli 1: Haetaan sivu
    active_page = scrape_linkedin_task()
    
    # 3. Tarkistetaan onnistuiko Mod 1
    if active_page:
        # 4. Moduuli 2: Lähetetään sivu hakuun
        search_linkedin(active_page)
        print("Testiajo: Haku suoritettu onnistuneesti.")
    else:
        print("Testiajo: active_page oli tyhjä (None). Tarkista Moduuli 1 return-lause!")

@teardown
def cleanup(task):
    browser.close_all()