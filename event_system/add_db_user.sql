-- Create a new database user
CREATE USER adi
IDENTIFIED BY 1234
DEFAULT TABLESPACE users
TEMPORARY TABLESPACE temp
QUOTA UNLIMITED ON users;

-- Basic connection privilege
GRANT CREATE SESSION TO adi;

-- Object creation privileges
GRANT CREATE TABLE TO adi;
GRANT CREATE SEQUENCE TO adi;
GRANT CREATE VIEW TO adi;
GRANT CREATE PROCEDURE TO adi;
GRANT CREATE TRIGGER TO adi;

-- Optional but useful for development
GRANT ALTER ANY TABLE TO adi;

GRANT CONNECT, RESOURCE TO adi;

commit;
