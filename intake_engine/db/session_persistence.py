from datetime import datetime

from intake_engine.db.intake_state_repository import save_intake_state, load_intake_state
from intake_engine.db.turn_repository import save_new_transcript_turns


def update_session_modified_at(conn, session_id):
    """
    Update Session.ModifiedAt to the current UTC timestamp.
    Does not commit. Transaction control belongs to the caller.
    """
    cursor = conn.cursor()
    modified_at = datetime.utcnow().isoformat()

    cursor.execute("""
        UPDATE Session
        SET ModifiedAt = ?
        WHERE SessionId = ?
    """, (modified_at, session_id))


def sync_session_state(conn, session_id, intake_state):
    """
    Persist the current intake state and any new transcript turns for a session.
    This operation is atomic: either all changes are saved or none are.
    """
    try:
        save_intake_state(
            conn = conn,
            session_id = session_id,
            intake_state = intake_state
        )

        saved_turn_ids = save_new_transcript_turns(
            conn = conn,
            session_id = session_id,
            transcript = intake_state.data["conversation_meta"]["transcript"]
        )

        update_session_modified_at(
            conn = conn,
            session_id = session_id
        )

        conn.commit()

        return {
            "session_id": session_id,
            "saved_turn_ids": saved_turn_ids
        }

    except Exception:
        conn.rollback()
        raise


def load_session_state(conn, session_id):
    """
    Load the canonical IntakeState snapshot for a session.
    Returns an IntakeState object or None if the session has no saved state.
    """
    return load_intake_state(
        conn = conn,
        session_id = session_id
    )