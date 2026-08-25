-- ------------------------------------------------------------
-- ENUM TYPES
-- ------------------------------------------------------------

CREATE TYPE user_role AS ENUM (
    'OPERATIONS_ADMIN',
    'FIELD_TECHNICIAN',
    'AUDITOR',
    'REGIONAL_SUPERVISOR'
);

CREATE TYPE atm_status AS ENUM (
    'Operational',
    'Low-Cash',
    'Maintenance',
    'Offline'
);

CREATE TYPE service_call_priority AS ENUM (
    'Low',
    'Medium',
    'Critical'
);

CREATE TYPE service_call_status AS ENUM (
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
    username        VARCHAR(100) NOT NULL UNIQUE,
    email           VARCHAR(255) NOT NULL UNIQUE,
    password_hash   TEXT NOT NULL,
    first_name      VARCHAR(100) NOT NULL,
    last_name       VARCHAR(100) NOT NULL,
    role            user_role NOT NULL,
    branch_id       INTEGER,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW()
);


-- ------------------------------------------------------------
-- BRANCHES
-- ------------------------------------------------------------

CREATE TABLE branches (
    id                  SERIAL PRIMARY KEY,
    name                VARCHAR(150) NOT NULL,
    location_region     VARCHAR(100) NOT NULL,
    capacity            INTEGER NOT NULL,
    supervisor_id       INTEGER,
    created_at          TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_branch_capacity
        CHECK (capacity >= 0),

    CONSTRAINT fk_branch_supervisor
        FOREIGN KEY (supervisor_id)
        REFERENCES users(id)
        ON DELETE SET NULL
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
    cash_level      NUMERIC(5,2) NOT NULL DEFAULT 100.00,
    facility_id     INTEGER NOT NULL,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_atm_cash_level
        CHECK (cash_level >= 0 AND cash_level <= 100),

    CONSTRAINT fk_atm_branch
        FOREIGN KEY (facility_id)
        REFERENCES branches(id)
        ON DELETE RESTRICT
);


-- ------------------------------------------------------------
-- SERVICE CALLS
-- ------------------------------------------------------------

CREATE TABLE service_calls (
    id              SERIAL PRIMARY KEY,
    title           VARCHAR(255) NOT NULL,
    priority        service_call_priority NOT NULL DEFAULT 'Medium',
    status          service_call_status NOT NULL DEFAULT 'Pending',
    atm_id          INTEGER NOT NULL,
    technician_id   INTEGER,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    started_at      TIMESTAMP,
    completed_at    TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_service_call_atm
        FOREIGN KEY (atm_id)
        REFERENCES atms(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_service_call_technician
        FOREIGN KEY (technician_id)
        REFERENCES users(id)
        ON DELETE SET NULL,

    CONSTRAINT chk_service_call_dates
        CHECK (
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
    service_call_id INTEGER NOT NULL,
    file_url        TEXT NOT NULL,
    notes           TEXT,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_report_service_call
        FOREIGN KEY (service_call_id)
        REFERENCES service_calls(id)
        ON DELETE CASCADE
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