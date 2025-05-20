CREATE TABLE "Group" (
    group_id INTEGER PRIMARY KEY
);

CREATE TABLE Person (
    member_id VARCHAR(1),
    group_id INTEGER,
    name VARCHAR(40) NOT NULL,
    mail VARCHAR(50) NOT NULL,
    PRIMARY KEY (group_id, member_id),
    FOREIGN KEY (group_id) REFERENCES "Group"(group_id)
);

CREATE TABLE Exercise (
    exercise_num INTEGER PRIMARY KEY
);

CREATE TABLE Feedback (
    exercise_num INTEGER,
    group_id INTEGER,
    reviewer_id VARCHAR(1),
    reviewee_id VARCHAR(1),
    score FLOAT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    PRIMARY KEY (exercise_num, group_id, reviewer_id, reviewee_id),
    FOREIGN KEY (exercise_num) REFERENCES Exercise(exercise_num),
    FOREIGN KEY (group_id, reviewer_id) REFERENCES Person(group_id, member_id),
    FOREIGN KEY (group_id, reviewee_id) REFERENCES Person(group_id, member_id)
);

CREATE TABLE Task (
    task_id INTEGER,
    exercise_num INTEGER,
    PRIMARY KEY (exercise_num, task_id),
    FOREIGN KEY (exercise_num) REFERENCES Exercise(exercise_num)
);

CREATE TABLE TaskResult (
    exercise_num INTEGER,
    task_id INTEGER,
    group_id INTEGER,
    points_awarded FLOAT NOT NULL,
    notes TEXT,
    PRIMARY KEY (exercise_num, task_id, group_id),
    FOREIGN KEY (exercise_num, task_id) REFERENCES Task(exercise_num, task_id),
    FOREIGN KEY (group_id) REFERENCES "Group"(group_id)
);

CREATE TABLE GroupMalus (
    exercise_num INTEGER,
    group_id INTEGER,
    points_deducted FLOAT NOT NULL,
    notes TEXT,
    PRIMARY KEY (exercise_num, group_id),
    FOREIGN KEY (exercise_num) REFERENCES Exercise(exercise_num),
    FOREIGN KEY (group_id) REFERENCES "Group"(group_id)
);

CREATE TABLE PersonMalus (
    exercise_num INTEGER,
    group_id INTEGER,
    member_id VARCHAR(1),
    points_deducted FLOAT NOT NULL,
    notes TEXT,
    PRIMARY KEY (exercise_num, group_id, member_id),
    FOREIGN KEY (exercise_num) REFERENCES Exercise(exercise_num),
    FOREIGN KEY (group_id, member_id) REFERENCES Person(group_id, member_id)
);

CREATE VIEW GroupExerciseSummary AS
WITH
    AggregatedTaskPointsPerExercise AS (
        SELECT
            group_id,
            exercise_num,
            SUM(points_awarded) AS sum_task_points
        FROM TaskResult
        GROUP BY group_id, exercise_num
    ),
    AllGroupExercisePairs AS (
        SELECT group_id, exercise_num FROM TaskResult
        UNION
        SELECT group_id, exercise_num FROM GroupMalus
    )
SELECT
    agep.group_id,
    agep.exercise_num,
    COALESCE(atppe.sum_task_points, 0) AS total_task_points_for_exercise,
    COALESCE(gm.points_deducted, 0) AS group_malus_for_exercise,
    (COALESCE(atppe.sum_task_points, 0) + COALESCE(gm.points_deducted, 0)) AS net_group_points_for_exercise
FROM AllGroupExercisePairs agep
LEFT JOIN AggregatedTaskPointsPerExercise atppe
    ON agep.group_id = atppe.group_id AND agep.exercise_num = atppe.exercise_num
LEFT JOIN GroupMalus gm
    ON agep.group_id = gm.group_id AND agep.exercise_num = gm.exercise_num;

CREATE VIEW StudentExerciseBreakdown AS
WITH
    AllStudentExerciseInvolvements AS (
        SELECT DISTINCT
            p.group_id,
            p.member_id,
            vges.exercise_num
        FROM Person p
        JOIN GroupExerciseSummary vges ON p.group_id = vges.group_id
        UNION
        SELECT DISTINCT
            pm.group_id,
            pm.member_id,
            pm.exercise_num
        FROM PersonMalus pm
    )
SELECT
    asi.group_id,
    asi.member_id,
    p.name AS student_name,
    p.mail AS student_mail,
    asi.exercise_num,
    COALESCE(vges.net_group_points_for_exercise, 0) AS group_contribution_for_exercise,
    COALESCE(pm.points_deducted, 0) AS personal_malus_for_exercise,
    (COALESCE(vges.net_group_points_for_exercise, 0) + COALESCE(pm.points_deducted, 0)) AS student_net_points_for_exercise
FROM AllStudentExerciseInvolvements asi
JOIN Person p ON asi.group_id = p.group_id AND asi.member_id = p.member_id
LEFT JOIN GroupExerciseSummary vges
    ON asi.group_id = vges.group_id AND asi.exercise_num = vges.exercise_num
LEFT JOIN PersonMalus pm
    ON asi.group_id = pm.group_id AND asi.member_id = pm.member_id AND asi.exercise_num = pm.exercise_num;

CREATE VIEW StudentOverallPoints AS
SELECT
    p.group_id,
    p.member_id,
    p.name AS student_name,
    p.mail AS student_mail,
    COALESCE(SUM(vseb.student_net_points_for_exercise), 0) AS final_total_achieved_points
FROM Person p
LEFT JOIN StudentExerciseBreakdown vseb
    ON p.group_id = vseb.group_id AND p.member_id = vseb.member_id
GROUP BY
    p.group_id,
    p.member_id,
    p.name,
    p.mail;