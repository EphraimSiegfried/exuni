import sqlite3
from sqlite3 import Connection
from gspread import Worksheet
from datetime import datetime
from pathlib import Path

def init_db(db_name:str, schema_file:str):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    if not Path(db_name).exists():
        with open(schema_file, "r") as f:
            schema = f.read()
            cursor.executescript(schema)
        conn.commit()
    return conn

def insert_group_data(worksheet: Worksheet, conn: Connection):
    cursor = conn.cursor()
    rows = worksheet.get_all_values()
    data = rows[3:]

    for row in data:
        team_id = int(row[0])
        cursor.execute("INSERT OR IGNORE INTO 'Group' (group_id) VALUES (?)", (int(team_id),))

        member_names = row[1:5]
        member_emails = row[5:9]
        member_ids = ["A", "B", "C", "D"]
        for member_id, name, email in zip(member_ids, member_names, member_emails):
            if name and email:
                cursor.execute('''
                                INSERT OR IGNORE INTO Person (member_id, group_id, name, mail)
                                VALUES (?, ?, ?, ?)
                            ''', (member_id, team_id, name, email))
    conn.commit()

def insert_contribution_data(worksheet: Worksheet, conn: Connection, exercise_id: int):
    cursor = conn.cursor()
    rows = worksheet.get_all_values()
    for row in rows:
        if row[0] and row[0] != "Timestamp":
            time, id, name, c1, c2, c3, c4 = row
            timestamp = datetime.strptime(time, "%d/%m/%Y %H:%M:%S")
            group_id = int(id[:-1])
            member_id = id[-1]

            for feedback, peer_id in zip([c1, c2, c3, c4], ["A", "B", "C", "D"]):
                if feedback == "Teammate does not exist":
                    continue
                score = float(feedback[:4])

                # Check for existing entry
                cursor.execute('''
                    SELECT created_at FROM Feedback
                    WHERE exercise_num = ? AND group_id = ? AND reviewer_id = ? AND reviewee_id = ?
                ''', (exercise_id, group_id, member_id, peer_id))
                existing = cursor.fetchone()

                if existing:
                    existing_timestamp = datetime.strptime(existing[0], "%Y-%m-%d %H:%M:%S")
                    if timestamp > existing_timestamp:
                        cursor.execute('''
                            UPDATE Feedback
                            SET score = ?, created_at = ?
                            WHERE exercise_num = ? AND group_id = ? AND reviewer_id = ? AND reviewee_id = ?
                        ''', (score, timestamp, exercise_id, group_id, member_id, peer_id))
                else:
                    cursor.execute('''
                        INSERT OR IGNORE INTO Feedback (exercise_num, group_id, reviewer_id, reviewee_id, score, created_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (exercise_id, group_id, member_id, peer_id, score, timestamp))

    conn.commit()

