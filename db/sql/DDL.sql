-- CashCow Command Center

-- This sets up the schema for the database where we want our data to persist

-- Initialize using:
--     psql postgres -c "CREATE DATABASE cashcow_dev;"
--     psql -d cashcow_dev
-- then run (when inside CashCow-Full-Stack-Project//db/sql):
--     \i DDL.sql


-- ------------------------------------------------------------
-- ENUM TYPES
-- ------------------------------------------------------------

-- CREATE TYPE user_role AS ENUM (
--     'Operations Admin',
--     'Technician',
--     'Auditor',
--     'Regional Supervisor'
-- );

CREATE TYPE atm_status AS ENUM (
    'Operational',
    'Low-Cash',
    'Maintenance',
    'Offline'
);

CREATE TYPE service_priority AS ENUM (
    'Low',
    'Medium',
    'Critical'
);

CREATE TYPE service_status AS ENUM (
    'Pending',
    'In-Progress',
    'Completed',
    'Failed'
);


-- ------------------------------------------------------------
-- USERS
-- ------------------------------------------------------------

CREATE TABLE users (
    id              SERIAL PRIMARY KEY,
    username        VARCHAR(50) NOT NULL UNIQUE,
    hashed_password TEXT NOT NULL,
    first_name      VARCHAR(100) NOT NULL,
    last_name       VARCHAR(100) NOT NULL,
    role            user_role NOT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE
);


-- ------------------------------------------------------------
-- BRANCHES
-- ------------------------------------------------------------

CREATE TABLE branches (
    id                  SERIAL PRIMARY KEY,
    name                VARCHAR(150) NOT NULL,
    location_region     VARCHAR(100) NOT NULL,
    capacity            INTEGER NOT NULL CHECK (capacity >= 0),
    supervisor_id       INTEGER REFERENCES users(id)
);


-- ------------------------------------------------------------
-- Add technician/supervisor branch relationship
-- ------------------------------------------------------------

ALTER TABLE users
ADD CONSTRAINT fk_user_branch
FOREIGN KEY (branch_id)
REFERENCES branches(id)
ON DELETE SET NULL;


-- ------------------------------------------------------------
-- ATMs
-- ------------------------------------------------------------

CREATE TABLE atms (
    id              SERIAL PRIMARY KEY,
    serial_number   VARCHAR(100) NOT NULL UNIQUE,
    model           VARCHAR(100) NOT NULL,
    status          atm_status NOT NULL DEFAULT 'Operational',
    cash_level      NUMERIC(5,2) NOT NULL DEFAULT 100.00 CHECK (cash_level BETWEEN 0 AND 100),
    branch_id     INTEGER NOT NULL REFERENCES branches(id)
);


-- ------------------------------------------------------------
-- SERVICE CALLS
-- ------------------------------------------------------------

CREATE TABLE service_calls (
    id              SERIAL PRIMARY KEY,
    title           VARCHAR(255) NOT NULL,
    priority        service_priority NOT NULL,
    status          service_status NOT NULL DEFAULT 'Pending',
    atm_id          INTEGER NOT NULL REFERENCES atms(id),
    technician_id   INTEGER REFERENCES users(id),
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    started_at      TIMESTAMP,
    completed_at    TIMESTAMP CHECK (
            completed_at IS NULL
            OR started_at IS NULL
            OR completed_at >= started_at
        )
);


-- ------------------------------------------------------------
-- DIAGNOSTIC REPORTS
-- ------------------------------------------------------------

CREATE TABLE diagnostic_reports (
    id              SERIAL PRIMARY KEY,
    service_call_id INTEGER NOT NULL REFERENCES service_calls(id),
    file_url        TEXT NOT NULL,
    notes           TEXT,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW()
);





-- ------------------------------------------------------------
-- INDEXES
-- ------------------------------------------------------------

-- Branch / ATM lookups
CREATE INDEX idx_atms_facility_id
    ON atms(facility_id);

CREATE INDEX idx_atms_status
    ON atms(status);

CREATE INDEX idx_atms_cash_level
    ON atms(cash_level);

CREATE INDEX idx_atms_model
    ON atms(model);


-- Service-call lookups
CREATE INDEX idx_service_calls_atm_id
    ON service_calls(atm_id);

CREATE INDEX idx_service_calls_technician_id
    ON service_calls(technician_id);

CREATE INDEX idx_service_calls_status
    ON service_calls(status);

CREATE INDEX idx_service_calls_priority
    ON service_calls(priority);


-- Diagnostic reports
CREATE INDEX idx_diagnostic_reports_service_call_id
    ON diagnostic_reports(service_call_id);


-- User lookups
CREATE INDEX idx_users_branch_id
    ON users(branch_id);

CREATE INDEX idx_users_role
    ON users(role);


-- ------------------------------------------------------------
-- updated_at trigger
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER trg_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();


CREATE TRIGGER trg_branches_updated_at
BEFORE UPDATE ON branches
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();


CREATE TRIGGER trg_atms_updated_at
BEFORE UPDATE ON atms
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();


CREATE TRIGGER trg_service_calls_updated_at
BEFORE UPDATE ON service_calls
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();