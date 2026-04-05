import json
from datetime import datetime

from intake_engine.IntakeState import IntakeState


def save_intake_state(conn, session_id, intake_state):
    """
    Save the current IntakeState for a session.
    If a row already exists for the session, update it.
    Does not commit. Transaction control belongs to the caller.
    """
    cursor = conn.cursor()

    intake_json = json.dumps(intake_state.to_dict())
    updated_at = datetime.utcnow().isoformat()

    cursor.execute("""
        INSERT INTO IntakeState (SessionId, IntakeJson, UpdatedAt)
        VALUES (?, ?, ?)
        ON CONFLICT(SessionId) DO UPDATE SET
            IntakeJson = excluded.IntakeJson,
            UpdatedAt = excluded.UpdatedAt
    """, (session_id, intake_json, updated_at))


def load_intake_state(conn, session_id):
    """
    Load IntakeState for a session.
    Returns an IntakeState object or None if no row exists.
    """
    cursor = conn.cursor()

    cursor.execute("""
        SELECT IntakeJson
        FROM IntakeState
        WHERE SessionId = ?
    """, (session_id,))

    row = cursor.fetchone()

    if row is None:
        return None

    intake_data = json.loads(row[0])
    return IntakeState(data = intake_data)