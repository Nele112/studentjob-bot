# LinkedIn StudentJob Bot
StudentJob Bot is an RPA solution built using Robocorp that automates job searching on LinkedIn.
The robot opens the LinkedIn jobs page, handles popups, extracts job links and compares them with previously saved data in an Excel file.
Only new job listings are stored, which helps avoid dublicates and makes job tracking easier and faster.
This project was developed as a part of a group assignment in an RPA course.

## Features
- Opens LinkedIn job search page automatically
- Handles cookie and login popups
- Extracts job links from the page
- Temporarily stores extracted jobs in memory for processing
- Compares new jobs with existing ones
- Avoids duplicate entries
- Stores only new job data in an Excel file
- Supports notifying the user about new job listings via email

## How It Works

1. The robot opens the LinkedIn jobs page.
2. It handles popups such as cookies and login prompts.
3. Job links are extracted form the page and stored in a temporary list.
4. 


## Project Structure



## Technologies Used

- Python
- Robocorp (RPA framework)
- Excel



## Usage


## Team Contributions


## Running

### Command Line

feature/linkedin_setup_satu
For more information, do not forget to check out the following:
- [Robocorp Documentation -site](https://robocorp.com/docs)
- [Portal for more examples](https://robocorp.com/portal)
- Follow our main [robocorp -repository](https://github.com/robocorp/robocorp) as it is the main location where we developed the libraries and the framework.

Markdown
StudentJob Bot 

An automated job search assistant built with Python and Robocorp/Sema4.ai.

Project Scope (MVP)
The goal of this robot is to help IT students find relevant job openings automatically. In its first phase, the robot focuses on LinkedIn.

Current Features
- Automated navigation to LinkedIn Jobs.
- Cookie and popup management (Sign-in dismissal).
- Search with customizable keywords.
- Error logging to `/output` folder.

Roadmap
- [ ] Add Duunitori and Oikotie support.
- [ ] Email notifications for new findings.
- [ ] Streamlit UI for easy keyword management.

Tech Stack
- Language: Python
- Framework: Robocorp / Sema4.ai
- Libraries: robocorp-browser, robocorp-tasks
- Version Control: Git

Getting Started
1. Ensure you have the Sema4.ai extension installed in VS Code.
2. Clone this repository.
3. Open the ‘Sema4.ai’  sidebar and select ‘Run Task’.

Contributors
Satu Grönroos, Nele Nestor-Voron, Jani Partanen
=======

