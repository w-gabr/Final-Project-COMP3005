DROP TABLE IF EXISTS ClassRegistration CASCADE;
DROP TABLE IF EXISTS PersonalTrainingSession CASCADE;
DROP TABLE IF EXISTS TrainerAvailability CASCADE;
DROP TABLE IF EXISTS HealthMetric CASCADE;
DROP TABLE IF EXISTS Class CASCADE;
DROP TABLE IF EXISTS Room CASCADE;
DROP TABLE IF EXISTS Member CASCADE;
DROP TABLE IF EXISTS Trainer CASCADE;
DROP TABLE IF EXISTS Admin CASCADE;


CREATE TABLE Admin (
    admin_id      SERIAL PRIMARY KEY,
    first_name    VARCHAR(50) NOT NULL,
    last_name     VARCHAR(50) NOT NULL,
    email         VARCHAR(100) UNIQUE NOT NULL,
    phone         VARCHAR(20)
);


CREATE TABLE Member (
    member_id     SERIAL PRIMARY KEY,
    first_name    VARCHAR(50) NOT NULL,
    last_name     VARCHAR(50) NOT NULL,
    email         VARCHAR(100) UNIQUE NOT NULL,
    date_of_birth DATE,
    gender        VARCHAR(10),
    phone         VARCHAR(20),
    fitness_goal  TEXT,
    created_at    TIMESTAMP DEFAULT NOW()
);


CREATE TABLE Trainer (
    trainer_id    SERIAL PRIMARY KEY,
    first_name    VARCHAR(50) NOT NULL,
    last_name     VARCHAR(50) NOT NULL,
    specialty     VARCHAR(100),
    hourly_rate   NUMERIC(8,2)
);


CREATE TABLE HealthMetric (
    metric_id          SERIAL PRIMARY KEY,
    member_id          INT NOT NULL REFERENCES Member(member_id) ON DELETE CASCADE,
    recorded_at        TIMESTAMP NOT NULL DEFAULT NOW(),
    weight_kg          NUMERIC(5,2),
    body_fat_pct       NUMERIC(5,2),
    resting_heart_rate INT,
    systolic_bp        INT,
    diastolic_bp       INT
);


CREATE TABLE TrainerAvailability (
    availability_id SERIAL PRIMARY KEY,
    trainer_id      INT NOT NULL REFERENCES Trainer(trainer_id) ON DELETE CASCADE,
    admin_id        INT REFERENCES Admin(admin_id),
    start_time      TIMESTAMP NOT NULL,
    end_time        TIMESTAMP NOT NULL,
    is_booked       BOOLEAN NOT NULL DEFAULT FALSE,
    CHECK (end_time > start_time)
);

CREATE TABLE PersonalTrainingSession (
    session_id   SERIAL PRIMARY KEY,
    member_id    INT NOT NULL REFERENCES Member(member_id) ON DELETE CASCADE,
    trainer_id   INT NOT NULL REFERENCES Trainer(trainer_id) ON DELETE CASCADE,
    start_time   TIMESTAMP NOT NULL,
    end_time     TIMESTAMP NOT NULL,
    status       VARCHAR(20) NOT NULL DEFAULT 'scheduled',
    CHECK (end_time > start_time)
);

CREATE TABLE Room (
    room_id      SERIAL PRIMARY KEY,
    room_name    VARCHAR(100) NOT NULL,
    room_type    VARCHAR(50),
    capacity     INT CHECK (capacity > 0),
    location     VARCHAR(100)
);

CREATE TABLE Class (
    class_id     SERIAL PRIMARY KEY,
    trainer_id   INT NOT NULL REFERENCES Trainer(trainer_id) ON DELETE CASCADE,
    admin_id     INT REFERENCES Admin(admin_id),
	room_id      INT REFERENCES Room(room_id),
    class_name   VARCHAR(100) NOT NULL,
    description  TEXT,
    start_time   TIMESTAMP NOT NULL,
    end_time     TIMESTAMP NOT NULL,
    capacity     INT NOT NULL CHECK (capacity > 0),
    CHECK (end_time > start_time)
);


CREATE TABLE ClassRegistration (
    registration_id SERIAL PRIMARY KEY,
    class_id        INT NOT NULL REFERENCES Class(class_id) ON DELETE CASCADE,
    member_id       INT NOT NULL REFERENCES Member(member_id) ON DELETE CASCADE,
    UNIQUE (class_id, member_id) 
);


CREATE OR REPLACE VIEW member_dashboard AS
SELECT m.member_id, CONCAT(m.first_name, ' ', m.last_name) AS full_name,
    m.fitness_goal,
    COUNT(DISTINCT cr.class_id) AS total_classes_registered,
    COUNT(DISTINCT pts.session_id) AS total_training_sessions,
    MAX(h.recorded_at) AS last_metric_timestamp,
    h.weight_kg,
    h.body_fat_pct
FROM Member AS m
LEFT JOIN ClassRegistration AS cr ON m.member_id = cr.member_id
LEFT JOIN PersonalTrainingSession AS pts ON m.member_id = pts.member_id
LEFT JOIN HealthMetric AS h ON m.member_id = h.member_id
GROUP BY m.member_id, m.first_name, m.last_name, m.fitness_goal, h.weight_kg, h.body_fat_pct;


CREATE OR REPLACE FUNCTION enforce_class_capacity()
RETURNS TRIGGER AS $$
DECLARE
    current_count INT;
    max_capacity INT;
BEGIN
    
    SELECT COUNT(*) INTO current_count
    FROM ClassRegistration
    WHERE class_id = NEW.class_id;

    
    SELECT capacity INTO max_capacity
    FROM Class
    WHERE class_id = NEW.class_id;

 
    IF current_count >= max_capacity THEN
        RAISE EXCEPTION 'Class is full. Cannot register.';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER trg_enforce_class_capacity
BEFORE INSERT ON ClassRegistration
FOR EACH ROW
EXECUTE FUNCTION enforce_class_capacity();


CREATE INDEX idx_classregistration_class_member
ON ClassRegistration (class_id, member_id);
