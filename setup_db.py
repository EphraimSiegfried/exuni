import gspread
from google.oauth2.service_account import Credentials
from exuni.database import *
from pathlib import Path

credentials_file = "credentials.json"
group_sheet_id = "1BOa_t8w-Y4ELJWbK-ukfWoZ50vlLwTbPZh47hitHHYI"
contribution_sheet_ids = [
    "1QxYPNK3VViJQ2Osxd-IzWLQx83gPMEbdmy4-DnIXRJ0",
    "1UG5eq0ziOLwhQry5vMqfAcVLKMU9dEsGlP1KVtb5DBE",
    "1qDrvFVR-8e1wa5iVVprs2WRgWR4ZSoXdLcm4OzNA40E"
]
points_sheet = "1O6ToKqANTOs_5VOK5enNeJVCH_Tkt7NWlNM-p0_75NU"
db_path = Path("dpi.db")
db_path.unlink(missing_ok=True)

scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file(credentials_file, scopes=scopes)
print("Authorizing Google Sheets API...")
client = gspread.authorize(creds)

print("Creating and initializing database")
conn = init_db(str(db_path), "exuni/schema.sql")

print("Inserting group data")
insert_group_data(client.open_by_key(group_sheet_id).sheet1, conn)

for ex_num, sheet_id in enumerate(contribution_sheet_ids):
    print(f"Inserting exercise {ex_num + 1} contribution feedback sheet")
    insert_contribution_data(client.open_by_key(sheet_id).sheet1, conn, ex_num + 1)

for ex_num, points_sheet in enumerate(client.open_by_key(points_sheet).worksheets()):
    print(f"Inserting exercise {ex_num + 1} points data")
    insert_points_data(points_sheet, conn)
    print(f"Inserting exercise {ex_num + 1} malus data")
    insert_person_malus_data(points_sheet, conn)
