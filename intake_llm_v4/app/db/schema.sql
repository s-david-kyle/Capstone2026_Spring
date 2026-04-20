-- Clinical Intake — schema.sql
-- Keep in lock-step with db_manager.py SCHEMA constant.
-- Bootstrap version: v2.1.0

-- schema_version table (added v2.1.0)
CREATE TABLE IF NOT EXISTS schema_version (
    version TEXT PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- encounters table
CREATE TABLE IF NOT EXISTS encounters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_name TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    primary_complaint TEXT NOT NULL,
    secondary_complaint TEXT DEFAULT '[]',
    pertinent_positive TEXT DEFAULT '[]',
    pertinent_negative TEXT DEFAULT '[]',
    model_version TEXT DEFAULT 'v2.1.0',
    status TEXT DEFAULT 'active',
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    patient_age INTEGER,
    patient_sex TEXT,
    escalation_level TEXT DEFAULT 'none',
    extracted_state TEXT DEFAULT '{}'
);

-- turns table
CREATE TABLE IF NOT EXISTS turns (
    turn_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    time_of_message TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    speaker TEXT NOT NULL,
    message TEXT NOT NULL,
    question_id TEXT,
    phase TEXT,
    FOREIGN KEY(session_id) REFERENCES encounters(id) ON DELETE CASCADE
);

-- summaries table
CREATE TABLE IF NOT EXISTS summaries (
    session_id INTEGER PRIMARY KEY,
    pre_summary TEXT,
    ai_summary TEXT,
    post_summary TEXT,
    reviewed_at TIMESTAMP,
    FOREIGN KEY(session_id) REFERENCES encounters(id) ON DELETE CASCADE
);

-- session_metrics table
CREATE TABLE IF NOT EXISTS session_metrics (
    session_id INTEGER PRIMARY KEY,
    patient_turn_count INTEGER DEFAULT 0,
    system_turn_count INTEGER DEFAULT 0,
    required_fields_total INTEGER DEFAULT 0,
    required_fields_filled INTEGER DEFAULT 0,
    completion_rate REAL DEFAULT 0.0,
    missing_fields_count INTEGER DEFAULT 0,
    missing_fields TEXT DEFAULT '[]',
    summary_length INTEGER DEFAULT 0,
    similarity_ratio REAL DEFAULT 0.0,
    major_edit_flag INTEGER DEFAULT 0,
    clinician_acceptance INTEGER DEFAULT 0,
    hallucination_flag_count INTEGER DEFAULT 0,
    hallucination_notes TEXT DEFAULT '[]',
    FOREIGN KEY(session_id) REFERENCES encounters(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_encounters_status ON encounters(status);
CREATE INDEX IF NOT EXISTS idx_encounters_created_at ON encounters(created_at);
CREATE INDEX IF NOT EXISTS idx_turns_session_id ON turns(session_id);
CREATE INDEX IF NOT EXISTS idx_turns_question_id ON turns(question_id);
