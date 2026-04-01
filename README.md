# LinkedIn StudentJob Bot
StudentJob Bot is an RPA solution built using Robocorp that automates job searching on LinkedIn.
The robot opens the LinkedIn jobs page, handles popups, extracts job links and compares them with previously saved data (Excel or Control Room storage).
Only new job listings are stored, which helps avoid duplicates and makes job tracking easier and faster.
This project was developed as a part of a group assignment in an RPA course.

## Current Features
- Opens LinkedIn job search page automatically
- Handles cookie and login popups
- Extracts job data (company, title, location, link)
- Temporarily stores extracted jobs in memory for processing
- Compares jobs with existing data using unique links
- Avoids duplicate entries
- Stores only new job data (Excel or Control Room storage)
- Sends email notification when new jobs are found (if configured)


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

## Getting Started

1. Ensure you have the Sema4.ai extension installed in VS Code.
2. Clone this repository.
3. Open the ‘Sema4.ai’  sidebar and select ‘Run Task’.

## Roadmap

- [ ] Add e.g. Duunitori and Oikotie support.
- [ ] Configure Email notifications for new findings.
- [ ] Streamlit UI for easy keyword management.


## Team Contributions

- Satu Grönroos 
- Nele Nestor-Voron 
- Jani Partanen 
- 
## Running
### Local Execution
Run the robot locally using: 

`python -m robocorp.tasks run tasks.py --task student_job_robot`

