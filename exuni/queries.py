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
