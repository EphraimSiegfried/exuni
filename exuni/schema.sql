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
