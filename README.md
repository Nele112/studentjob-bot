# LinkedIn StudentJob Bot
StudentJob Bot is an RPA solution built using Robocorp that automates job searching on LinkedIn.
The robot opens the LinkedIn jobs page, handles popups, extracts job links and compares them with previously saved data (Excel or Control Room storage).
Only new job listings are stored, which helps avoid duplicates and makes job tracking easier and faster.
This project was developed as a part of a group assignment in an RPA course.

## Features
- Opens LinkedIn job search page automatically
- Handles cookie and login popups
- Extracts job data (company, title, location, link)
- Temporarily stores extracted jobs in memory for processing
- Compares jobs with existing data using unique links
- Avoids duplicate entries
- Stores only new job data (Excel or Control Room storage)
- Sends email notification when new jobs are found (if configured)

## How It Works
1. The robot opens the LinkedIn jobs page.
2. It handles popups such as cookies and login prompts.
3. Job data (company, title, location, link) is extracted from the page.
4. The data is stored temporarily in memory.
5. The robot compares extracted jobs with previously seen job data using job links.
6. Only new job listings are identified.
7. New jobs are appended to the Excel file.
8. An email notification is triggered if new jobs are found.


## Project Structure
- tasks.py - main robot logic
- output/data.xlsx - optional local data file
- output/ - robot execution logs
- README.md - project documentation

## Robocorp Control Room Integration
The robot is designed to run in Robocorp Control Room, not only locally.

### Persistent Storage
The robot uses Robocorp Control Room asset storage:

- `storage.get_json("studentjob_seen_links")`

This allows the robot to:
- Store previously seen job links
- Persist data between runs
- Avoid duplicates across executions

This replaces relying only on local Excel files, which are not reliable in cloud execution.

### Scheduling
The robot is configured to run once per day in Control Room.
- Runs automatically without manual input  
- Searches for new jobs daily  
- Works as a background automation

### Notification Logic
- If new jobs are found → notification is triggered
- If no new jobs → no notification is sent
- If an error occurs → error is logged (email logic prepared)

## Technologies Used

- Python
- Robocorp (RPA framework)
- RPA.Excel.Files
- RPA.Tables
- Robocorp Storage

## Usage
This robot is designed to reduce manual job searching effort.
Typical workflow:
- Robot runs automatically (daily)
- Searches for jobs using predefined keywords
- Stores only new job listings
- Notifies the user if new jobs are found


## Team Contributions
Group 5

- Satu Grönroos – Notification & UX
- Nele Nestor-Voron – RPA development
- Jani Partanen – Data processing & integration

## Running
### Local Execution
Run the robot locally using: 

`python -m robocorp.tasks run tasks.py --task student_job_robot`

### Control Room Execution
In production, the robot runs in Robocorp Control Room.
The robot can be scheduled to run automatically (e.g., once per day)
No manual execution is required
