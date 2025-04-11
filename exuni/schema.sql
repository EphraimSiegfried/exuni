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

