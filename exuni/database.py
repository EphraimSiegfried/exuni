import sqlite3
from sqlite3 import Connection
from gspread import Worksheet
from datetime import datetime
from pathlib import Path
import string

def init_db(db_name: str, schema_file: str):
    db_exists = Path(db_name).exists()
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    if not db_exists:
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
                score = float(feedback.split(" ")[0])

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


def insert_points_data(worksheet: Worksheet, conn: Connection):
    cursor = conn.cursor()
    header = worksheet.row_values(3)
    first_col = worksheet.col_values(1)
    num_groups = max(int(v) for v in first_col if v.isnumeric()) # kind of ugly solution
    exercise_id = int(worksheet.acell("A1").value[-1])
    num_tasks = len([h for h in header if "Task" in h and "Points" in h])
    num_cols = 1 + 2 * (num_tasks + 1) + 1
    col_id = string.ascii_uppercase[num_cols-1]
    data_row_start = 4
    data = worksheet.get(f"A{data_row_start}:{col_id}{data_row_start - 1 + num_groups}", maintain_size=True)
    task_ids = list(range(1, num_tasks + 1))

    for task_id in task_ids:
        cursor.execute('''
        INSERT OR IGNORE INTO Task (task_id, exercise_num)
        VALUES (?, ?)
        ''', (task_id, exercise_id))

    for row in data:
        group_id = int(row[0])
        points = row[1:num_tasks+1]
        points_notes = row[num_tasks+3: 3 + 2 * num_tasks]
        malus = row[num_tasks+1]
        malus_notes = row[3 + 2 * num_tasks]
        for task_id, point, note in zip(task_ids, points, points_notes):
            cursor.execute('''
            INSERT OR IGNORE INTO TaskResult (exercise_num, task_id, group_id, points_awarded, notes)
            VALUES (?, ?, ?, ?, ?)''', (exercise_id, task_id, group_id, point, note))
        if not malus or float(malus) == 0:
            continue
        cursor.execute('''
        INSERT OR IGNORE INTO GroupMalus (exercise_num, group_id, points_deducted, notes)
        VALUES (?, ?, ?, ?) ''', (exercise_id, group_id, malus, malus_notes))
    conn.commit()

def insert_person_malus_data(worksheet: Worksheet, conn: Connection):
    cursor = conn.cursor()
    header_row = 27
    header = worksheet.row_values(header_row)
    exercise_id = int(worksheet.acell("A1").value[-1])
    num_members = (len(header) - 1) // 2
    first_col = worksheet.col_values(1)
    num_groups = max(int(v) for v in first_col if v.isnumeric()) # kind of ugly solution
    col_end_id = string.ascii_uppercase[len(header)-1]
    data = worksheet.get(f"A{header_row+1}:{col_end_id}{header_row + num_groups}", maintain_size=True)
    member_ids = string.ascii_uppercase[:num_members]
    for row in data:
        team_id = int(row[0])
        malus_points = row[1:num_members+1]
        malus_notes = row[num_members+1:]
        for member_id, point, note in zip(member_ids, malus_points, malus_notes):
            if not point:
                continue
            cursor.execute('''
            INSERT OR IGNORE INTO PersonMalus (exercise_num, group_id, member_id, points_deducted, notes)
            VALUES (?, ?, ?, ?, ?)''', (exercise_id, team_id, member_id, float(point), note))
    conn.commit()