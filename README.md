# LinkedIn StudentJob Bot
StudentJob Bot is an RPA solution built using Robocorp that automates job searching on LinkedIn.
The robot opens the LinkedIn jobs page, handles popups, extracts job links and compares them with previously saved data in an Excel file.
Only new job listings are stored, which helps avoid duplicates and makes job tracking easier and faster.
This project was developed as a part of a group assignment in an RPA course.

## Features
- Opens LinkedIn job search page automatically
- Handles cookie and login popups
- Extracts job data (company, title, location, link)
- Temporarily stores extracted jobs in memory for processing
- Compares jobs with existing data using unique links
- Avoids duplicate entries
- Stores only new job data in an Excel file
- Sends email notification when new jobs are found (if configured)

## How It Works
1. The robot opens the LinkedIn jobs page.
2. It handles popups such as cookies and login prompts.
3. Job data (company, title, location, link) is extracted from the page.
4. The data is stored temporarily in memory.
5. The robot compares extracted jobs with existing entries in data.xlsx using job links.
6. Only new job listings are identified.
7. New jobs are appended to the Excel file.
8. An email notification is sent to the user.


## Project Structure
- tasks.py - main robot logic
- data.xlsx - stored job data (generated at runtime)
- output/ - robot execution logs
- README.md - project documentation



## Technologies Used

- Python
- Robocorp (RPA framework)
- Excel



## Usage


## Team Contributions


## Running

### Command Line

