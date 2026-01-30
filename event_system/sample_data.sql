-- ============================================================
-- SAMPLE DATA SCRIPT
-- College Event Registration and Attendance Management System
-- ============================================================
-- This script inserts sample data for testing purposes.
-- It is safe to run after the database setup script.
-- No hard-coded primary key values are used.
-- ============================================================

-- ------------------------------------------------------------
-- 1. Clear existing data (child tables first)
-- ------------------------------------------------------------
DELETE FROM ATTENDANCE;
DELETE FROM REGISTRATIONS;
DELETE FROM EVENTS;
DELETE FROM STUDENTS;
DELETE FROM USERS;

COMMIT;

-- ------------------------------------------------------------
-- 2. Insert sample USERS
--    NOTE: Passwords are bcrypt hashed. Original passwords:
--    admin1: admin123
--    volunteer1: vol123
--    volunteer2: vol456
-- ------------------------------------------------------------

INSERT INTO USERS (username, password, role)
VALUES ('admin1', '$2b$12$uYZb79h4JHuDK2jVji9wUuHjZCCVDThvd88t4Gwqwnz.pCMJg3O8G', 'admin');

INSERT INTO USERS (username, password, role)
VALUES ('volunteer1', '$2b$12$ySqHn2NqerpxPTtktG1U4.sUJTpqS7.zWRJtO8iRUO2o8ayoH5wfK', 'volunteer');

INSERT INTO USERS (username, password, role)
VALUES ('volunteer2', '$2b$12$jyCDQnXb/DlCaP9Z36n72OXnRoQkI9JFZKALKYkgK4/gP2RzFQ7fy', 'volunteer');

-- ------------------------------------------------------------
-- 3. Insert sample STUDENTS
-- ------------------------------------------------------------

INSERT INTO STUDENTS (student_id, name, email, course, year)
VALUES ('S101', 'Neha Verma', 'neha.verma@example.com', 'BCA', 1);

INSERT INTO STUDENTS (student_id, name, email, course, year)
VALUES ('S102', 'Rohit Patel', 'rohit.patel@example.com', 'BSc IT', 3);

INSERT INTO STUDENTS (student_id, name, email, course, year)
VALUES ('S103', 'Priya Singh', 'priya.singh@example.com', 'BCom', 2);

-- ------------------------------------------------------------
-- 4. Insert sample EVENTS
-- ------------------------------------------------------------
INSERT INTO EVENTS (event_name, event_date, event_time, venue, total_slots)
VALUES ('Tech Talk on AI', DATE '2026-02-10', '10:00 AM', 'Seminar Hall A', 100);

INSERT INTO EVENTS (event_name, event_date, event_time, venue, total_slots)
VALUES ('Annual Sports Meet', DATE '2026-02-15', '09:00 AM', 'College Ground', 200);

INSERT INTO EVENTS (event_name, event_date, event_time, venue, total_slots)
VALUES ('Cultural Fest', DATE '2026-03-01', '05:00 PM', 'Open Auditorium', 300);

COMMIT;

-- ------------------------------------------------------------
-- 5. Insert sample REGISTRATIONS (no hard-coded IDs)
-- ------------------------------------------------------------
INSERT INTO REGISTRATIONS (event_id, student_id)
SELECT event_id, 'S101'
FROM EVENTS
WHERE event_name = 'Tech Talk on AI';

INSERT INTO REGISTRATIONS (event_id, student_id)
SELECT event_id, 'S102'
FROM EVENTS
WHERE event_name = 'Tech Talk on AI';

INSERT INTO REGISTRATIONS (event_id, student_id)
SELECT event_id, 'S101'
FROM EVENTS
WHERE event_name = 'Annual Sports Meet';

INSERT INTO REGISTRATIONS (event_id, student_id)
SELECT event_id, 'S103'
FROM EVENTS
WHERE event_name = 'Annual Sports Meet';

INSERT INTO REGISTRATIONS (event_id, student_id)
SELECT event_id, 'S104'
FROM EVENTS
WHERE event_name = 'Cultural Fest';

COMMIT;

-- ------------------------------------------------------------
-- 6. Insert sample ATTENDANCE
-- ------------------------------------------------------------
INSERT INTO ATTENDANCE (event_id, student_id, attended)
SELECT event_id, 'S101', 'Y'
FROM EVENTS
WHERE event_name = 'Tech Talk on AI';

INSERT INTO ATTENDANCE (event_id, student_id, attended)
SELECT event_id, 'S102', 'N'
FROM EVENTS
WHERE event_name = 'Tech Talk on AI';

INSERT INTO ATTENDANCE (event_id, student_id, attended)
SELECT event_id, 'S101', 'Y'
FROM EVENTS
WHERE event_name = 'Annual Sports Meet';

INSERT INTO ATTENDANCE (event_id, student_id, attended)
SELECT event_id, 'S103', 'Y'
FROM EVENTS
WHERE event_name = 'Annual Sports Meet';

INSERT INTO ATTENDANCE (event_id, student_id, attended)
SELECT event_id, 'S104', 'N'
FROM EVENTS
WHERE event_name = 'Cultural Fest';

COMMIT;

-- ------------------------------------------------------------
-- 7. Verification Queries (optional)
-- ------------------------------------------------------------
-- SELECT * FROM USERS;
-- SELECT * FROM STUDENTS;
-- SELECT * FROM EVENTS;
-- SELECT * FROM REGISTRATIONS;
-- SELECT * FROM ATTENDANCE;

-- ============================================================
-- END OF SAMPLE DATA SCRIPT
-- ============================================================
