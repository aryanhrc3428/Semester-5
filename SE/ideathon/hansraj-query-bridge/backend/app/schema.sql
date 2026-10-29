-- Hansraj Query Bridge schema (PostgreSQL 14+ with pgvector).
-- Table names follow the pseudocode (USERS, ROLE, D2_KNOWLEDGE ... D7_AUDIT_LOGS) and the ER
-- diagram. IDs are text UUIDs because the pseudocode validates them as strings.

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS btree_gist;

CREATE TABLE IF NOT EXISTS ROLE (
    role_id           SERIAL PRIMARY KEY,
    role_name         TEXT NOT NULL UNIQUE CHECK (role_name IN ('Student', 'Admin', 'TIC')),
    description       TEXT,
    permissions_json  TEXT
);

CREATE TABLE IF NOT EXISTS DEPARTMENTS (
    dept_id           TEXT PRIMARY KEY,
    department_name   TEXT NOT NULL,
    department_code   TEXT NOT NULL UNIQUE,
    hod_name          TEXT
);

CREATE TABLE IF NOT EXISTS USERS (
    user_id           TEXT PRIMARY KEY,
    role_id           INT  NOT NULL REFERENCES ROLE(role_id),
    department_id     TEXT REFERENCES DEPARTMENTS(dept_id),   -- null for cross-department admins
    user_identity     TEXT NOT NULL UNIQUE,                    -- identity returned by college auth
    name              TEXT NOT NULL,
    email             TEXT NOT NULL,
    college_id_number TEXT,
    academic_year     TEXT,                                    -- students only
    is_active         BOOLEAN NOT NULL DEFAULT TRUE,
    kb_permission     BOOLEAN NOT NULL DEFAULT FALSE,          -- "Authorized TIC" (SRS 3.4.3-D)
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_login_at     TIMESTAMPTZ
);

-- Stand-in for the external college authentication service (SRS 2.1.1-B). Only the mock
-- auth gateway reads this table; the application never touches it directly.
CREATE TABLE IF NOT EXISTS COLLEGE_DIRECTORY (
    username          TEXT PRIMARY KEY,
    password_hash     TEXT NOT NULL,
    user_identity     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS SESSIONS (
    jti               TEXT PRIMARY KEY,
    user_id           TEXT NOT NULL,
    expires_at        TIMESTAMPTZ NOT NULL,
    revoked           BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS D2_KNOWLEDGE (
    kb_id               TEXT PRIMARY KEY,
    department_id       TEXT REFERENCES DEPARTMENTS(dept_id),  -- null = institution-wide
    title               TEXT NOT NULL,
    content             TEXT NOT NULL,
    category            TEXT,
    source              TEXT,
    verification_status TEXT NOT NULL DEFAULT 'Verified',
    validity_status     TEXT NOT NULL DEFAULT 'Active' CHECK (validity_status IN ('Active', 'Inactive', 'Archived')),
    version             INT  NOT NULL DEFAULT 1,
    embedding           vector(1536),
    created_by          TEXT,
    verified_by         TEXT,
    source_query_id     TEXT,
    valid_until         DATE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_kb_validity ON D2_KNOWLEDGE (validity_status);
CREATE INDEX IF NOT EXISTS idx_kb_embedding ON D2_KNOWLEDGE USING hnsw (embedding vector_cosine_ops);

CREATE TABLE IF NOT EXISTS D2_KNOWLEDGE_VERSIONS (
    version_id        SERIAL PRIMARY KEY,
    kb_id             TEXT NOT NULL,
    version           INT  NOT NULL,
    title             TEXT,
    content           TEXT,
    category          TEXT,
    source            TEXT,
    changed_by        TEXT,
    changed_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS D3_QUERIES (
    query_id            TEXT PRIMARY KEY,
    student_id          TEXT NOT NULL REFERENCES USERS(user_id),
    department_id       TEXT REFERENCES DEPARTMENTS(dept_id),
    description         TEXT NOT NULL,
    category            TEXT,
    status              TEXT NOT NULL DEFAULT 'Open',
    source              TEXT,                                  -- 'AI Escalation' | 'Direct Raise'
    ai_response_text    TEXT,
    ai_confidence_score REAL,
    resolution          TEXT,
    resolved_by         TEXT REFERENCES USERS(user_id),
    assigned_tic        TEXT REFERENCES USERS(user_id),
    doc_request_note    TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved_at         TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_q_student ON D3_QUERIES (student_id, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_q_status ON D3_QUERIES (status, created_at);
CREATE INDEX IF NOT EXISTS idx_q_tic ON D3_QUERIES (assigned_tic, updated_at DESC);

CREATE TABLE IF NOT EXISTS QUERY_ASSIGNMENTS (
    assignment_id     SERIAL PRIMARY KEY,
    query_id          TEXT NOT NULL REFERENCES D3_QUERIES(query_id),
    assigned_to       TEXT NOT NULL REFERENCES USERS(user_id),
    assigned_by       TEXT NOT NULL REFERENCES USERS(user_id),
    department_id     TEXT REFERENCES DEPARTMENTS(dept_id),
    assignment_status TEXT NOT NULL DEFAULT 'Assigned' CHECK (assignment_status IN ('Assigned', 'Reassigned', 'Withdrawn')),
    assigned_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS D4_DOCUMENTS (
    document_id       TEXT PRIMARY KEY,
    query_id          TEXT NOT NULL REFERENCES D3_QUERIES(query_id),
    uploaded_by       TEXT NOT NULL REFERENCES USERS(user_id),
    file_name         TEXT NOT NULL,
    file_type         TEXT NOT NULL,
    file_size         BIGINT NOT NULL,
    storage_key       TEXT NOT NULL,
    status            TEXT NOT NULL DEFAULT 'Pending Review',
    review_notes      TEXT,
    reviewed_by       TEXT,
    uploaded_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at        TIMESTAMPTZ,
    reviewed_at       TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_doc_query ON D4_DOCUMENTS (query_id);

CREATE TABLE IF NOT EXISTS D5_MEETINGS (
    meeting_id         TEXT PRIMARY KEY,
    query_id           TEXT REFERENCES D3_QUERIES(query_id),
    assigned_tic       TEXT NOT NULL REFERENCES USERS(user_id),
    student_id         TEXT NOT NULL REFERENCES USERS(user_id),
    meeting_date       DATE NOT NULL,
    start_time         TIME NOT NULL,
    end_time           TIME NOT NULL,
    status             TEXT NOT NULL DEFAULT 'Scheduled',
    mode               TEXT,
    location_or_link   TEXT,
    cancellation_reason TEXT,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at         TIMESTAMPTZ,
    CHECK (end_time > start_time),
    -- No double-booking, even under concurrent requests (SRS 3.3.2 / 3.4.2-D).
    CONSTRAINT no_tic_overlap EXCLUDE USING gist (
        assigned_tic WITH =,
        tsrange((meeting_date + start_time), (meeting_date + end_time)) WITH &&
    ) WHERE (status <> 'Cancelled')
);

CREATE TABLE IF NOT EXISTS D6_TIME_SLOTS (
    slot_id           TEXT PRIMARY KEY,
    assigned_tic      TEXT NOT NULL REFERENCES USERS(user_id),
    slot_date         DATE NOT NULL,
    start_time        TIME NOT NULL,
    end_time          TIME NOT NULL,
    status            TEXT NOT NULL DEFAULT 'Available' CHECK (status IN ('Available', 'Requested', 'Accepted')),
    student_id        TEXT REFERENCES USERS(user_id),
    query_id          TEXT REFERENCES D3_QUERIES(query_id),
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at        TIMESTAMPTZ,
    CHECK (end_time > start_time),
    UNIQUE (assigned_tic, slot_date, start_time)
);

CREATE TABLE IF NOT EXISTS TIMETABLE_PERIODS (          -- backing data of the mock timetable service
    period_id         SERIAL PRIMARY KEY,
    tic_id            TEXT NOT NULL REFERENCES USERS(user_id),
    weekday           INT  NOT NULL CHECK (weekday BETWEEN 1 AND 7),   -- ISO: Monday=1
    start_time        TIME NOT NULL,
    end_time          TIME NOT NULL
);

CREATE TABLE IF NOT EXISTS NOTIFICATIONS (
    notification_id     TEXT PRIMARY KEY,
    recipient_id        TEXT NOT NULL REFERENCES USERS(user_id),
    related_query_id    TEXT,
    related_document_id TEXT,
    related_meeting_id  TEXT,
    event_type          TEXT NOT NULL,
    message             TEXT NOT NULL,
    delivery_channel    TEXT NOT NULL DEFAULT 'In-App',
    delivery_status     TEXT NOT NULL DEFAULT 'Pending' CHECK (delivery_status IN ('Sent', 'Failed', 'Pending')),
    email_status        TEXT NOT NULL DEFAULT 'Pending',
    is_read             BOOLEAN NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    read_at             TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_notif_recipient ON NOTIFICATIONS (recipient_id, created_at DESC);

CREATE TABLE IF NOT EXISTS D7_AUDIT_LOGS (
    audit_id          BIGSERIAL PRIMARY KEY,
    user_id           TEXT NOT NULL,                  -- may be 'System' (UC-07), hence no FK
    action_type       TEXT NOT NULL,
    entity            TEXT NOT NULL,
    entity_id         TEXT,
    ip_address        TEXT,
    details           TEXT,
    timestamp         TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_audit_ts ON D7_AUDIT_LOGS (timestamp DESC);

CREATE TABLE IF NOT EXISTS AI_INTERACTIONS (          -- SRS 3.7.3-C: store query, sources, confidence
    interaction_id    TEXT PRIMARY KEY,
    student_id        TEXT NOT NULL,
    query_text        TEXT NOT NULL,
    response_status   TEXT NOT NULL,
    answer_text       TEXT,
    source_ids        TEXT,
    confidence        REAL,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Audit records are protected from modification or deletion (SRS 3.7.2).
CREATE OR REPLACE FUNCTION audit_immutable() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'D7_AUDIT_LOGS is append-only';
END;
$$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_audit_immutable ON D7_AUDIT_LOGS;
CREATE TRIGGER trg_audit_immutable BEFORE UPDATE OR DELETE ON D7_AUDIT_LOGS
    FOR EACH ROW EXECUTE FUNCTION audit_immutable();

-- Stamp resolved_at when a query becomes Resolved.
CREATE OR REPLACE FUNCTION stamp_resolved() RETURNS trigger AS $$
BEGIN
    IF NEW.status = 'Resolved' AND (OLD.status IS DISTINCT FROM 'Resolved') THEN
        NEW.resolved_at := now();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_stamp_resolved ON D3_QUERIES;
CREATE TRIGGER trg_stamp_resolved BEFORE UPDATE ON D3_QUERIES
    FOR EACH ROW EXECUTE FUNCTION stamp_resolved();
