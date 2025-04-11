
from exuni.main import get_sheet
from exuni.database import *
from pathlib import Path

group_sheet_id = "1BOa_t8w-Y4ELJWbK-ukfWoZ50vlLwTbPZh47hitHHYI"
contribution_sheet_ids = [
    "1QxYPNK3VViJQ2Osxd-IzWLQx83gPMEbdmy4-DnIXRJ0"
]
points_sheet = "1O6ToKqANTOs_5VOK5enNeJVCH_Tkt7NWlNM-p0_75NU"
get = lambda sheet_id: get_sheet(sheet_id, "credentials.json")

db_path = Path("dpi.db")
db_path.unlink(missing_ok=True)

conn = init_db(str(db_path), "exuni/schema.sql")
insert_group_data(get(group_sheet_id), conn)
for ex_num, id in enumerate(contribution_sheet_ids):
    insert_contribution_data(get(id), conn, ex_num + 1)
insert_points_data(get(points_sheet), conn)
insert_person_malus_data(get(points_sheet), conn)


