from sqlite3 import Connection


def get_students_without_feedback_submission( exercise_number:int, conn:Connection):
    cursor = conn.cursor()
    cursor.execute('''
       SELECT p.name, p.mail
       FROM Person p
       WHERE NOT EXISTS (
           SELECT 1
           FROM Feedback f
           WHERE f.exercise_num = ?
             AND f.group_id = p.group_id
             AND f.reviewer_id = p.member_id
       );
       ''', (exercise_number,))
    return cursor.fetchall()

def get_students_submitted_feedback_later_than(timestamp, exercise_number:int, conn:Connection):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT DISTINCT p.name, p.mail, f.created_at
        FROM Person p
        NATURAL JOIN Feedback f
        WHERE f.exercise_num = ?
        AND f.created_at > ?
       ''', (exercise_number, timestamp))
    return cursor.fetchall()


def get_feedbacks_where_score_less_than(score: float, exercise_number: int, conn: Connection):
    cursor = conn.cursor()
    cursor.execute("""
    SELECT r.name, r.mail, re.name, re.mail, f.score
    FROM Feedback f
    JOIN Person r ON f.group_id = r.group_id AND f.reviewer_id = r.member_id
    JOIN Person re ON f.group_id = re.group_id AND f.reviewee_id = re.member_id
    WHERE f.exercise_num = ? AND f.score < ?
    """ ,(exercise_number, score))
    return cursor.fetchall()


def print_group_summary(conn, exercise_num, group_id):
    cursor = conn.cursor()

    print(f"\nSummary for Group {group_id} - Exercise {exercise_num}")
    print("=" * 60)

    # 1. Task Points for the Group
    cursor.execute("""
        SELECT task_id, points_awarded, COALESCE(notes, '') 
        FROM TaskResult
        WHERE exercise_num = ? AND group_id = ?
        ORDER BY task_id
    """, (exercise_num, group_id))
    task_results = cursor.fetchall()

    print("\nTask Points:")
    total_task_points = 0
    for task_id, points, notes in task_results:
        print(f"  Task {task_id}: {points} points", end='')
        if notes:
            print(f" | Notes: {notes}")
        else:
            print()
        total_task_points += points

    # 2. Group Malus
    cursor.execute("""
        SELECT points_deducted, COALESCE(notes, '')
        FROM GroupMalus
        WHERE exercise_num = ? AND group_id = ?
    """, (exercise_num, group_id))
    group_malus = cursor.fetchone()
    group_malus_points = group_malus[0] if group_malus else 0
    group_malus_notes = group_malus[1] if group_malus else ''

    if group_malus:
        print(f"\nGroup Malus: {group_malus_points} points", end='')
        if group_malus_notes:
            print(f" | Notes: {group_malus_notes}")
        else:
            print()
    else:
        print("\nGroup Malus: None")

    group_total = total_task_points + group_malus_points

    # 3. Member list with individual malus and calculated personal score

    print("\nMembers and Individual Scores:")

    cursor.execute("""
        SELECT P.member_id, P.name, P.mail,
               COALESCE(PM.points_deducted, 0), COALESCE(PM.notes, '')
        FROM Person P
        LEFT JOIN PersonMalus PM ON P.group_id = PM.group_id 
                                 AND P.member_id = PM.member_id 
                                 AND PM.exercise_num = ?
        WHERE P.group_id = ?
        ORDER BY P.member_id
    """, (exercise_num, group_id))


    members = cursor.fetchall()
    for member_id, name, mail, person_malus, malus_notes in members:
        individual_score = group_total + person_malus
        print(f"  {name} ({member_id})")
        print(f"    Individual Malus: {person_malus} points", end='')
        if malus_notes:
            print(f" | Notes: {malus_notes}")
        else:
            print()
        print(f"    → Total Points: {individual_score}")
        print()
