INSERT INTO Admin (first_name, last_name, email, phone) VALUES
('Alice', 'Nguyen', 'alice.admin@fitclub.com', '555-1010'),
('Brian', 'Lopez', 'brian.admin@fitclub.com', '555-2020');

INSERT INTO Member (first_name, last_name, email, date_of_birth, gender, phone, fitness_goal)
VALUES
('Sarah', 'Ali', 'sarah.member@fitclub.com', '1998-03-15', 'F', '555-3001', 'Lose 5kg and improve cardio'),
('James', 'Kim', 'james.member@fitclub.com', '1995-07-22', 'M', '555-3002', 'Gain muscle mass'),
('Lena', 'Patel', 'lena.member@fitclub.com', '2000-11-05', 'F', '555-3003', 'Improve flexibility');

INSERT INTO Trainer (first_name, last_name, specialty, hourly_rate, email)
VALUES
('Michael', 'Reed', 'Strength Training', 60.00, 'michael.reed@fitclub.com'),
('Emily', 'Stone', 'Yoga', 55.00, 'emily.stone@fitclub.com'),
('David', 'Khan', 'HIIT/Cardio', 50.00, 'david.khan@fitclub.com');

INSERT INTO Room (room_name, room_type, capacity, location)
VALUES
('Studio A', 'Yoga Studio', 20, '1st Floor'),
('Studio B', 'HIIT Room', 15, '1st Floor'),
('Weight Room', 'Strength Training', 25, 'Basement');

INSERT INTO HealthMetric (member_id, recorded_at, weight_kg, body_fat_pct, resting_heart_rate, systolic_bp, diastolic_bp)
VALUES
(1, '2025-10-01 09:00', 70.5, 24.0, 72, 118, 76),
(2, '2025-10-10 18:00', 80.2, 20.0, 68, 120, 80),
(3, '2025-10-12 08:30', 60.0, 22.0, 75, 115, 73);

INSERT INTO TrainerAvailability (trainer_id, admin_id, start_time, end_time, is_booked)
VALUES
(1, 1, '2025-10-20 09:00', '2025-10-20 11:00', FALSE),
(1, 1, '2025-10-21 14:00', '2025-10-21 16:00', TRUE),
(2, 2, '2025-10-20 08:00', '2025-10-20 10:00', FALSE),
(3, 2, '2025-10-22 18:00', '2025-10-22 20:00', FALSE);

INSERT INTO Class (trainer_id, admin_id, room_id, class_name, description, start_time, end_time, capacity)
VALUES
(1, 1, 3, 'Strength 101', 'Intro strength training basics', '2025-10-25 09:00', '2025-10-25 10:00', 10),
(2, 2, 1, 'Morning Yoga Flow', 'Relaxing yoga for flexibility', '2025-10-26 08:00', '2025-10-26 09:00', 20),
(3, 1, 2, 'HIIT Blast', 'High intensity interval training', '2025-10-27 18:00', '2025-10-27 19:00', 15);

INSERT INTO ClassRegistration (class_id, member_id)
VALUES
(1, 1), 
(1, 2),
(2, 3),
(3, 1);

INSERT INTO PersonalTrainingSession (member_id, trainer_id, start_time, end_time, status)
VALUES
(1, 1, '2025-10-20 09:00', '2025-10-20 10:00', 'scheduled'),
(2, 3, '2025-10-22 18:00', '2025-10-22 19:00', 'scheduled'),
(3, 2, '2025-10-20 08:00', '2025-10-20 09:00', 'scheduled');



