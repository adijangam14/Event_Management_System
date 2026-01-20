-- Create a new database user
CREATE USER admin
IDENTIFIED BY 1234
DEFAULT TABLESPACE users
TEMPORARY TABLESPACE temp
QUOTA UNLIMITED ON users;

-- Basic connection privilege
GRANT CREATE SESSION TO admin;

-- Object creation privileges
GRANT CREATE TABLE TO admin;
GRANT CREATE SEQUENCE TO admin;
GRANT CREATE VIEW TO admin;
GRANT CREATE PROCEDURE TO admin;
GRANT CREATE TRIGGER TO admin;

-- Optional but useful for development
GRANT ALTER ANY TABLE TO admin;

GRANT CONNECT, RESOURCE TO admin;

commit;
