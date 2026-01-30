EXECUTE IMMEDIATE 'DROP TABLE ATTENDANCE';
EXECUTE IMMEDIATE 'DROP TABLE REGISTRATIONS';
EXECUTE IMMEDIATE 'DROP TABLE EVENTS';
EXECUTE IMMEDIATE 'DROP TABLE STUDENTS';
EXECUTE IMMEDIATE 'DROP TABLE USERS';
EXECUTE IMMEDIATE 'DROP SEQUENCE event_id_seq';
EXECUTE IMMEDIATE 'DROP SEQUENCE reg_id_seq';
EXECUTE IMMEDIATE 'DROP SEQUENCE attendance_id_seq';
EXECUTE IMMEDIATE 'DROP SEQUENCE user_id_seq';

CREATE SEQUENCE user_id_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE event_id_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE reg_id_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE attendance_id_seq START WITH 1 INCREMENT BY 1;

CREATE TABLE EVENTS (
    event_id NUMBER DEFAULT event_id_seq.NEXTVAL NOT NULL,
    event_name VARCHAR2(255) NOT NULL,
    event_date DATE NOT NULL,
    event_time VARCHAR2(20) NOT NULL,
    venue VARCHAR2(255) NOT NULL,
    total_slots NUMBER NOT NULL,
    CONSTRAINT pk_events PRIMARY KEY (event_id)
);

CREATE TABLE STUDENTS (
    student_id VARCHAR2(255) NOT NULL,
    name VARCHAR2(255) NOT NULL,
    email VARCHAR2(255) NOT NULL UNIQUE,
    course VARCHAR2(255),
    year NUMBER,
    CONSTRAINT pk_students PRIMARY KEY (student_id)
);

CREATE TABLE REGISTRATIONS (
    reg_id NUMBER DEFAULT reg_id_seq.NEXTVAL NOT NULL,
    event_id NUMBER NOT NULL,
    student_id VARCHAR2(255) NOT NULL,
    reg_date DATE DEFAULT SYSDATE,
    status VARCHAR2(50) DEFAULT 'REGISTERED',
    CONSTRAINT pk_registrations PRIMARY KEY (reg_id),
    CONSTRAINT fk_reg_events FOREIGN KEY (event_id) REFERENCES EVENTS(event_id),
    CONSTRAINT fk_reg_students FOREIGN KEY (student_id) REFERENCES STUDENTS(student_id),
    CONSTRAINT uk_event_student UNIQUE (event_id, student_id)
);

CREATE TABLE ATTENDANCE (
    attendance_id NUMBER DEFAULT attendance_id_seq.NEXTVAL NOT NULL,
    event_id NUMBER NOT NULL,
    student_id VARCHAR2(255) NOT NULL,
    attended CHAR(1) DEFAULT 'N' NOT NULL,
    CONSTRAINT pk_attendance PRIMARY KEY (attendance_id),
    CONSTRAINT fk_att_events FOREIGN KEY (event_id) REFERENCES EVENTS(event_id),
    CONSTRAINT fk_att_students FOREIGN KEY (student_id) REFERENCES STUDENTS(student_id),
    CONSTRAINT uk_att_event_student UNIQUE (event_id, student_id),
    CONSTRAINT chk_attended CHECK (attended IN ('Y', 'N'))
);

CREATE TABLE USERS (
    user_id NUMBER DEFAULT user_id_seq.NEXTVAL NOT NULL,
    username VARCHAR2(255) NOT NULL,
    password VARCHAR2(255) NOT NULL,
    role VARCHAR2(50) NOT NULL,
    CONSTRAINT pk_users PRIMARY KEY (user_id),
    CONSTRAINT uk_username UNIQUE (username),
    CONSTRAINT chk_role CHECK (role IN ('admin', 'volunteer'))
);
