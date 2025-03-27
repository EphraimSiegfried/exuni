# Exuni
This application manages student feedback data gathered from google spreadsheets.

This application combines data gathered from a
[group formation spreadsheet](https://docs.google.com/spreadsheets/d/1S4hpU8GyryqhRcwaRjkI84BRD5ghWf3J4v0P_5ILSBo/edit?usp=sharing)
with a [peer contribution feedback](https://docs.google.com/forms/d/e/1FAIpQLSfX_6qBTQAvoOufCGbQieKkniO023wXAd6jz8D8ImesiH6n1g/viewform?usp=header) spreadsheet
in a database. It can query which students have not submitted, submitted late or have given another student a score lower than a given threshold. 

# Usage
1. Generate [Google Credentials](https://developers.google.com/workspace/guides/create-credentials) 
2. You will get a service account with an email. Give this email access rights on the spreadsheet you want to use with this application
3. Install [uv](https://docs.astral.sh/uv/guides/install-python/)
4. Run `uv exuni/main.py update` to update the database or `uv exuni/main.py query` to query the database.
