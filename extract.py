from robocorp import browser

def extract_jobs():
    """ -opens current page
        -finds all job listings
        -iterates through each job
        -extracts job links from the current linkedin results page
        -stores them in a list
        -returns the list """
    page = browser.page()
    job_elements = page.locator("a.base-card__full-link")
    count = job_elements.count()
    jobs = []
    for i in range(count):
        job = job_elements.nth(i)
        link = job.get_attribute ("href")
        jobs.append( {
            "link" : link
        })

    return jobs