import time
import json
from typing import Optional, List, Dict, Any

# -----------------------------------------------------------
# CRUD operations for the database
# These helper functions insert, update, and retrieve data.
# -----------------------------------------------------------

def create_session(conn, session_id: int, model_version: str = "v0") -> None:
    """Start a new conversation session."""

    conn.execute(
        """
        INSERT INTO Session (SessionId, CreatedAt, ModelVersion, Status)
        VALUES (?, ?, ?, 'active')
        """,
        (session_id, time.time(), model_version)
    )
    conn.commit()


def update_session_complaint(
    conn,
    session_id: str,
    primary: str,
    secondary: Optional[List[str]] = None
) -> None:
    """Set the primary and secondary complaints for a session."""

    # Convert the secondary complaint list to JSON text for storage.
    secondary_json = json.dumps(secondary) if secondary else "[]"

    conn.execute(
        """
        UPDATE Session
        SET PrimaryComplaint = ?, SecondaryComplaint = ?
        WHERE SessionId = ?
        """,
        (primary, secondary_json, session_id)
    )
    conn.commit()


def end_session(conn, session_id: str, status: str = "completed") -> None:
    """Mark a session as completed or reviewed."""

    conn.execute(
        """
        UPDATE Session
        SET EndedAt = ?, Status = ?
        WHERE SessionId = ?
        """,
        (time.time(), status, session_id)
    )
    conn.commit()


def add_turn(conn, session_id: str, speaker: str, message: str) -> int:
    """Add one message to the conversation and return the new TurnId."""

    cursor = conn.execute(
        """
        INSERT INTO Turn (SessionId, TimeOfMessage, Speaker, Message)
        VALUES (?, ?, ?, ?)
        """,
        (session_id, time.time(), speaker, message)
    )
    conn.commit()

    # Return the auto-generated primary key for the inserted turn.
    return cursor.lastrowid


def get_turns(conn, session_id: str) -> List[Dict[str, Any]]:
    """Retrieve all turns for a session in chronological order."""

    rows = conn.execute(
        """
        SELECT TurnId, TimeOfMessage, Speaker, Message
        FROM Turn
        WHERE SessionId = ?
        ORDER BY TurnId
        """,
        (session_id,)
    ).fetchall()

    # Convert database rows into Python dictionaries.
    return [
        {
            "TurnId": r[0],
            "TimeOfMessage": r[1],
            "Speaker": r[2],
            "Message": r[3]
        }
        for r in rows
    ]


def save_pre_summary(conn, session_id: str, pre_summary: str) -> None:
    """Store the AI-generated draft summary."""

    conn.execute(
        """
        INSERT INTO Summary (SessionId, PreSummary)
        VALUES (?, ?)
        ON CONFLICT(SessionId) DO UPDATE SET
            PreSummary = excluded.PreSummary
        """,
        (session_id, pre_summary)
    )
    conn.commit()


def save_post_summary(conn, session_id: str, post_summary: str) -> None:
    """Store the doctor-edited final summary and review timestamp."""

    conn.execute(
        """
        INSERT INTO Summary (SessionId, PostSummary, ReviewedAt)
        VALUES (?, ?, ?)
        ON CONFLICT(SessionId) DO UPDATE SET
            PostSummary = excluded.PostSummary,
            ReviewedAt = excluded.ReviewedAt
        """,
        (session_id, post_summary, time.time())
    )
    conn.commit()

    