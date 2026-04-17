"""Raw sqlite3 persistence layer."""
from __future__ import annotations

import json
import os
import sqlite3
from typing import Any, Dict, List, Optional

DB_DIR = os.environ.get("DB_DIR", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data"))
DB_PATH = os.environ.get("DATABASE_URL", os.path.join(DB_DIR, "clinical_intake.db"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS encounters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_name TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    primary_complaint TEXT NOT NULL,
    secondary_complaint TEXT DEFAULT '[]',
    pertinent_positive TEXT DEFAULT '[]',
    pertinent_negative TEXT DEFAULT '[]',
    model_version TEXT DEFAULT 'v3.0',
    status TEXT DEFAULT 'active',
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    patient_age INTEGER,
    patient_sex TEXT,
    escalation_level TEXT DEFAULT 'none',
    extracted_state TEXT DEFAULT '{}'
);

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

CREATE TABLE IF NOT EXISTS summaries (
    session_id INTEGER PRIMARY KEY,
    pre_summary TEXT,
    ai_summary TEXT,
    post_summary TEXT,
    reviewed_at TIMESTAMP,
    FOREIGN KEY(session_id) REFERENCES encounters(id) ON DELETE CASCADE
);

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
"""

def get_connection() -> sqlite3.Connection:
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(SCHEMA)

def create_encounter(session_name: str, primary_complaint: str, patient_age: int, patient_sex: str, secondary_complaint: str) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO encounters (session_name, primary_complaint, patient_age, patient_sex, secondary_complaint) VALUES (?, ?, ?, ?, ?)",
            (session_name, primary_complaint, patient_age, patient_sex, secondary_complaint),
        )
        return int(cur.lastrowid)

def add_turn(session_id: int, speaker: str, message: str, question_id: Optional[str], phase: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO turns (session_id, speaker, message, question_id, phase) VALUES (?, ?, ?, ?, ?)",
            (session_id, speaker, message, question_id, phase),
        )

def get_turns(session_id: int) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cur = conn.execute("SELECT * FROM turns WHERE session_id = ? ORDER BY turn_id", (session_id,))
        return [dict(row) for row in cur.fetchall()]

def save_summary(session_id: int, pre_summary: Optional[str] = None, ai_summary: Optional[str] = None, post_summary: Optional[str] = None, reviewed_at: Optional[str] = None) -> None:
    with get_connection() as conn:
        exists = conn.execute("SELECT 1 FROM summaries WHERE session_id = ?", (session_id,)).fetchone()
        if exists:
            conn.execute(
                "UPDATE summaries SET pre_summary=COALESCE(?,pre_summary), ai_summary=COALESCE(?,ai_summary), post_summary=COALESCE(?,post_summary), reviewed_at=COALESCE(?,reviewed_at) WHERE session_id=?",
                (pre_summary, ai_summary, post_summary, reviewed_at, session_id),
            )
        else:
            conn.execute(
                "INSERT INTO summaries (session_id, pre_summary, ai_summary, post_summary, reviewed_at) VALUES (?, ?, ?, ?, ?)",
                (session_id, pre_summary, ai_summary, post_summary, reviewed_at),
            )

def save_metrics(session_id: int, metrics: Dict[str, Any]) -> None:
    with get_connection() as conn:
        exists = conn.execute("SELECT 1 FROM session_metrics WHERE session_id = ?", (session_id,)).fetchone()
        if exists:
            sql = "UPDATE session_metrics SET " + ", ".join(f"{k}=?" for k in metrics.keys()) + " WHERE session_id = ?"
            conn.execute(sql, tuple(metrics.values()) + (session_id,))
        else:
            cols = ", ".join(metrics.keys())
            placeholders = ", ".join(["?" for _ in metrics])
            conn.execute(f"INSERT INTO session_metrics (session_id, {cols}) VALUES (?, {placeholders})", (session_id, *tuple(metrics.values())))

def update_encounter_status(session_id: int, status: str, ended_at: Optional[str] = None) -> None:
    with get_connection() as conn:
        if ended_at:
            conn.execute("UPDATE encounters SET status=?, ended_at=?, modified_at=CURRENT_TIMESTAMP WHERE id=?", (status, ended_at, session_id))
        else:
            conn.execute("UPDATE encounters SET status=?, modified_at=CURRENT_TIMESTAMP WHERE id=?", (status, session_id))

def update_encounter_state(session_id: int, extracted_state: Dict[str, Any], pertinent_positive: List[str], pertinent_negative: List[str], escalation_level: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "UPDATE encounters SET extracted_state=?, pertinent_positive=?, pertinent_negative=?, escalation_level=?, modified_at=CURRENT_TIMESTAMP WHERE id=?",
            (json.dumps(extracted_state), json.dumps(pertinent_positive), json.dumps(pertinent_negative), escalation_level, session_id),
        )

def get_encounter(session_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM encounters WHERE id=?", (session_id,)).fetchone()
        return dict(row) if row else None

def get_summary(session_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM summaries WHERE session_id=?", (session_id,)).fetchone()
        return dict(row) if row else None


def get_metrics(session_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM session_metrics WHERE session_id=?", (session_id,)).fetchone()
        return dict(row) if row else None
