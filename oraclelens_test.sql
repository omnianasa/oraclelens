-- OracleLens integration-test schema
-- Run this script while connected as SHEET26 to the target PDB.
-- It creates only ORACLELENS_* objects in the SHEET26 schema.
-- It does NOT modify HR tables or data.
--
-- Suggested execution:
--   sqlplus SHEET26@localhost:8521/FREEPDB1
--   @oraclelens_test.sql
--
-- If you get ORA-00942 when reading HR.EMPLOYEES / HR.DEPARTMENTS,
-- ask a DBA or the HR schema owner to run the optional GRANT statements
-- at the bottom of this file. Do not run those statements as SHEET26.

SET SERVEROUTPUT ON
SET FEEDBACK ON
SET PAGESIZE 100
SET LINESIZE 180

PROMPT
PROMPT === 1. Create test tables ===

CREATE TABLE oraclelens_test_departments (
    department_id   NUMBER(6)       CONSTRAINT ol_test_dept_pk PRIMARY KEY,
    department_name VARCHAR2(60)    CONSTRAINT ol_test_dept_name_nn NOT NULL,
    location        VARCHAR2(100)   DEFAULT 'Cairo',
    created_at      TIMESTAMP       DEFAULT SYSTIMESTAMP,
    CONSTRAINT ol_test_dept_name_uq UNIQUE (department_name)
);

CREATE TABLE oraclelens_test_employees (
    employee_id   NUMBER(10)      CONSTRAINT ol_test_emp_pk PRIMARY KEY,
    first_name    VARCHAR2(40)    NOT NULL,
    last_name     VARCHAR2(40)    NOT NULL,
    email         VARCHAR2(120)   CONSTRAINT ol_test_emp_email_uq UNIQUE,
    salary        NUMBER(10,2)    DEFAULT 10000 NOT NULL,
    hire_date     DATE            DEFAULT SYSDATE NOT NULL,
    status        VARCHAR2(12)    DEFAULT 'ACTIVE' NOT NULL,
    department_id NUMBER(6),
    notes         CLOB,
    CONSTRAINT ol_test_emp_salary_ck CHECK (salary >= 0),
    CONSTRAINT ol_test_emp_status_ck CHECK (status IN ('ACTIVE', 'ON_LEAVE', 'INACTIVE')),
    CONSTRAINT ol_test_emp_dept_fk
        FOREIGN KEY (department_id)
        REFERENCES oraclelens_test_departments(department_id)
);

PROMPT
PROMPT === 2. Create indexes ===

CREATE INDEX oraclelens_test_emp_lastname_ix
    ON oraclelens_test_employees(last_name);

CREATE INDEX oraclelens_test_emp_dept_status_ix
    ON oraclelens_test_employees(department_id, status);

PROMPT
PROMPT === 3. Create a sequence ===

CREATE SEQUENCE oraclelens_test_emp_seq
    START WITH 1001
    INCREMENT BY 1
    MINVALUE 1
    NOCYCLE
    CACHE 20;

PROMPT
PROMPT === 4. Insert sample data ===

INSERT INTO oraclelens_test_departments (department_id, department_name, location)
VALUES (10, 'Engineering', 'Cairo');

INSERT INTO oraclelens_test_departments (department_id, department_name, location)
VALUES (20, 'Research', 'Alexandria');

INSERT INTO oraclelens_test_departments (department_id, department_name, location)
VALUES (30, 'Operations', 'Giza');

INSERT INTO oraclelens_test_employees
    (employee_id, first_name, last_name, email, salary, hire_date, status, department_id, notes)
VALUES
    (oraclelens_test_emp_seq.NEXTVAL, 'Mona', 'Hassan', 'mona.hassan@example.test',
     18000, DATE '2022-02-14', 'ACTIVE', 10, 'Senior engineer');

INSERT INTO oraclelens_test_employees
    (employee_id, first_name, last_name, email, salary, hire_date, status, department_id, notes)
VALUES
    (oraclelens_test_emp_seq.NEXTVAL, 'Omar', 'Ali', 'omar.ali@example.test',
     14500, DATE '2023-06-01', 'ACTIVE', 10, 'Backend engineer');

INSERT INTO oraclelens_test_employees
    (employee_id, first_name, last_name, email, salary, hire_date, status, department_id, notes)
VALUES
    (oraclelens_test_emp_seq.NEXTVAL, 'Salma', 'Ibrahim', 'salma.ibrahim@example.test',
     21000, DATE '2021-09-20', 'ON_LEAVE', 20, 'Research lead');

INSERT INTO oraclelens_test_employees
    (employee_id, first_name, last_name, email, salary, hire_date, status, department_id, notes)
VALUES
    (oraclelens_test_emp_seq.NEXTVAL, 'Youssef', 'Nabil', 'youssef.nabil@example.test',
     12000, DATE '2024-01-10', 'ACTIVE', 30, 'Operations analyst');

INSERT INTO oraclelens_test_employees
    (employee_id, first_name, last_name, email, salary, hire_date, status, department_id, notes)
VALUES
    (oraclelens_test_emp_seq.NEXTVAL, 'Nour', 'Samir', 'nour.samir@example.test',
     16000, DATE '2020-11-05', 'INACTIVE', 20, 'Former researcher');

INSERT INTO oraclelens_test_employees
    (employee_id, first_name, last_name, email, salary, hire_date, status, department_id, notes)
VALUES
    (oraclelens_test_emp_seq.NEXTVAL, 'Karim', 'Fathy', 'karim.fathy@example.test',
     13500, DATE '2023-03-18', 'ACTIVE', 30, 'Shift coordinator');

INSERT INTO oraclelens_test_employees
    (employee_id, first_name, last_name, email, salary, hire_date, status, department_id, notes)
VALUES
    (oraclelens_test_emp_seq.NEXTVAL, 'Laila', 'Mostafa', 'laila.mostafa@example.test',
     19500, DATE '2022-08-22', 'ACTIVE', 10, 'Platform engineer');

INSERT INTO oraclelens_test_employees
    (employee_id, first_name, last_name, email, salary, hire_date, status, department_id, notes)
VALUES
    (oraclelens_test_emp_seq.NEXTVAL, 'Adam', 'Sherif', 'adam.sherif@example.test',
     11000, DATE '2024-05-12', 'ACTIVE', 30, 'Junior analyst');

INSERT INTO oraclelens_test_employees
    (employee_id, first_name, last_name, email, salary, hire_date, status, department_id, notes)
VALUES
    (oraclelens_test_emp_seq.NEXTVAL, 'Farida', 'Tarek', 'farida.tarek@example.test',
     23000, DATE '2019-04-30', 'ON_LEAVE', 20, 'Principal researcher');

INSERT INTO oraclelens_test_employees
    (employee_id, first_name, last_name, email, salary, hire_date, status, department_id, notes)
VALUES
    (oraclelens_test_emp_seq.NEXTVAL, 'Ziad', 'Mahmoud', 'ziad.mahmoud@example.test',
     14000, DATE '2023-12-04', 'ACTIVE', 10, 'QA engineer');

COMMIT;

PROMPT
PROMPT === 5. Create views ===

CREATE OR REPLACE VIEW oraclelens_test_employee_details_v AS
SELECT e.employee_id,
       e.first_name,
       e.last_name,
       e.email,
       e.salary,
       e.hire_date,
       e.status,
       d.department_name,
       d.location AS department_location
FROM oraclelens_test_employees e
LEFT JOIN oraclelens_test_departments d
    ON d.department_id = e.department_id;

CREATE OR REPLACE VIEW oraclelens_test_active_employees_v AS
SELECT employee_id, first_name, last_name, email, department_id, salary
FROM oraclelens_test_employees
WHERE status = 'ACTIVE';

PROMPT
PROMPT === 6. Optional synonym for testing synonyms ===

CREATE OR REPLACE SYNONYM oraclelens_test_employees_syn
FOR oraclelens_test_employees;

PROMPT
PROMPT === 7. Basic validation queries ===

SELECT table_name
FROM user_tables
WHERE table_name LIKE 'ORACLELENS_TEST%'
ORDER BY table_name;

SELECT column_name, data_type, data_length, nullable, data_precision, data_scale
FROM user_tab_columns
WHERE table_name = 'ORACLELENS_TEST_EMPLOYEES'
ORDER BY column_id;

SELECT constraint_name, constraint_type, status, search_condition
FROM user_constraints
WHERE table_name = 'ORACLELENS_TEST_EMPLOYEES'
ORDER BY constraint_type, constraint_name;

SELECT index_name, uniqueness, status
FROM user_indexes
WHERE table_name = 'ORACLELENS_TEST_EMPLOYEES'
ORDER BY index_name;

SELECT sequence_name, min_value, increment_by, cycle_flag, cache_size, last_number
FROM user_sequences
WHERE sequence_name = 'ORACLELENS_TEST_EMP_SEQ';

SELECT view_name, text_length
FROM user_views
WHERE view_name LIKE 'ORACLELENS_TEST%';

SELECT * FROM oraclelens_test_employee_details_v ORDER BY employee_id;

PROMPT
PROMPT === Test objects created. Connect with OracleLens as SHEET26. ===
PROMPT Suggested OracleLens commands:
PROMPT   tables ORACLELENS_TEST
PROMPT   views ORACLELENS_TEST
PROMPT   describe ORACLELENS_TEST_EMPLOYEES
PROMPT   relations ORACLELENS_TEST_EMPLOYEES
PROMPT   indexes ORACLELENS_TEST_EMPLOYEES
PROMPT   constraints ORACLELENS_TEST_EMPLOYEES
PROMPT   sequences ORACLELENS_TEST
PROMPT   sequence-info ORACLELENS_TEST_EMP_SEQ
PROMPT   view-definition ORACLELENS_TEST_EMPLOYEE_DETAILS_V
PROMPT   show ORACLELENS_TEST_EMPLOYEES --limit 3 --page 2
PROMPT   query SELECT employee_id, first_name, last_name, salary FROM ORACLELENS_TEST_EMPLOYEES
PROMPT   query SELECT * FROM ORACLELENS_TEST_EMPLOYEE_DETAILS_V
PROMPT
PROMPT === Optional grants (run as HR or a DBA, not as SHEET26) ===
PROMPT These grants are only needed if SHEET26 should read the original HR schema.
PROMPT Uncomment and execute the appropriate statements separately with an authorized account:
PROMPT GRANT SELECT ON HR.EMPLOYEES TO SHEET26;
PROMPT GRANT SELECT ON HR.DEPARTMENTS TO SHEET26;
PROMPT GRANT SELECT ON HR.JOBS TO SHEET26;
PROMPT GRANT SELECT ON HR.LOCATIONS TO SHEET26;
PROMPT GRANT SELECT ON HR.COUNTRIES TO SHEET26;
PROMPT GRANT SELECT ON HR.REGIONS TO SHEET26;

-- Example query for OracleLens after HR grants have been provided:
-- SELECT e.employee_id, e.first_name, e.last_name, d.department_name
-- FROM HR.EMPLOYEES e
-- JOIN HR.DEPARTMENTS d ON d.department_id = e.department_id
-- ORDER BY e.employee_id
-- FETCH FIRST 10 ROWS ONLY;
