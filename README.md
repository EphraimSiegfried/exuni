# Exuni
This application manages student exercise data. It tracks points students achieved and the relevant notes the tutors have written for each task. 
It also manages feedback data submitted by the students. 

This application combines data gathered from:
* [Group Formation Spreadsheet](https://docs.google.com/spreadsheets/d/1S4hpU8GyryqhRcwaRjkI84BRD5ghWf3J4v0P_5ILSBo/edit?usp=sharing)
* [Exercise Dates Spreadsheet](https://docs.google.com/spreadsheets/d/1yLQ4t-wfCc0JsKpwCH3Tivs8z1XtJgyav1uIA-a5bWc/edit?usp=sharing)
* [Peer Contribution Feedback](https://docs.google.com/forms/d/e/1FAIpQLSfX_6qBTQAvoOufCGbQieKkniO023wXAd6jz8D8ImesiH6n1g/viewform?usp=header)
* [Exercise Points Spreadsheet](https://docs.google.com/spreadsheets/d/100B8bZ3Gw8cEBhu9Z0dQmkjy9sMK11ZKs-Uh5cScIRs/edit?usp=sharing)

# Setup
1. Generate [Google Credentials](https://developers.google.com/workspace/guides/create-credentials) 
2. You will get a service account with an email. Give this email access rights on the spreadsheet you want to use with this application
3. Install [uv](https://docs.astral.sh/uv/guides/install-python/)
4. Run `uv run exuni update` to update the database or `uv run exuni query` to query the database. Or check do something similar like iin `setup_db.py`

# Usage

### Exercise Summary
Get a summary for a given group number and exercise sheet number with:
```bash
uv run exuni points_summary <sheet_num> <group_num>
```
which generates something similar to 
```aiignore
Summary for Group 8 - Exercise 2
============================================================

Task Points:
  Task 1: 3.0 points | Notes: Good documentation, well done!
  Task 2: 6.0 points | Notes: The code is neat and documentation is great, nice!
  Task 3: 4.0 points | Notes: Well done!

Group Malus: -0.5 points | Notes: Submission file is in the wrong format: DPI_SUBMISSION.zip

Members and Individual Scores:
  Friedrich Nietzsche (A)
    Individual Malus: 0 points
    → Total Points: 12.5

  Rene Descartes (B)
    Individual Malus: -1.0 points | Notes: Stated that pointers are Git objects.  Adjustments to the Git graph were incomplete/incorrect.
    → Total Points: 11.5

  Immanuel Kant (C)
    Individual Malus: 0 points
    → Total Points: 12.5
```
### Overall points
Get the total points with:
```sql
SELECT *
FROM StudentOverallPoints
```

### Feedback Status
Check which students have not submitted or submitted the contribution feedback late with:
```sql
SELECT *
FROM StudentSubmissionStatus
```

