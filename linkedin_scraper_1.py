from robocorp import browser
from robocorp.tasks import task

def scrape_linkedin_task():
    """
    1. Avaa selaimen ja LinkedInin.
    2. Sulkee kirjautumisikkunan ja evästebannerin, jos ne näkyvät.
    3. Palauttaa sivu-olion (page) seuraavalle moduulille.
    """
    
    # Määritetään selaimen näkyvyys ja hidastus kehitystä varten
    browser.configure(
        headless=False,
        slowmo=1000
    )
    
    page = None

    try:
        print("Moduuli 1: Navigoidaan LinkedIniin...")
        page = browser.goto("https://fi.linkedin.com/jobs/jobs-in-finland?position=1&pageNum=0")
        
        # Määritetään mahdolliset napit (suomi ja englanti)
        accept_button = "button:has-text('Accept'), button:has-text('Hyväksy')"
        close_popup_button = "button[aria-label='Dismiss'], button[aria-label='Sulje']"
        
        # Odotetaan hetki, että pop-upit ehtivät latautua
        page.wait_for_timeout(3000) 
        
        # 1. Yritetään sulkea kirjautumis-popup
        if page.is_visible(close_popup_button):
            page.click(close_popup_button)
            print("Moduuli 1: Kirjautumisikkuna suljettu.")
        
        # 2. Yritetään hyväksyä evästeet
        # HUOM: Emme käytä wait_for_selectoria, jotta robotti ei jää jumiin jos banneria ei tule.
        if page.is_visible(accept_button):
            page.click(accept_button)
            print("Moduuli 1: Evästeet hyväksytty.")
        else:
            print("Moduuli 1: Evästebanneria ei näkynyt, jatketaan eteenpäin.")

    except Exception as e:
        print(f"Moduuli 1: Tapahtui virhe navigoinnissa: {e}")
    
    # PALAUTETAAN SIVU (tämä on se kriittinen kaukosäädin)
    # Tämä on nyt sisennetty try-lohkon ulkopuolelle, jotta se palautuu aina.
    return page

if __name__ == "__main__":
    # Tämä mahdollistaa tiedoston testaamisen yksinään, mutta ei sekoita päärobottia
    scrape_linkedin_task()