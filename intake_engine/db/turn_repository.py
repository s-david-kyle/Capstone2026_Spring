from datetime import datetime


def save_turn(conn, session_id, speaker, message, time_of_message = None):
    """
    Save a single turn to the Turn table.
    Returns the new TurnId.
    Does not commit. Transaction control belongs to the caller.
    """
    cursor = conn.cursor()

    if time_of_message is None:
        time_of_message = datetime.utcnow().isoformat()

    cursor.execute("""
        INSERT INTO Turn (
            SessionId,
            TimeOfMessage,
            Speaker,
            Message
        )
        VALUES (?, ?, ?, ?)
    """, (
        session_id,
        time_of_message,
        speaker,
        message
    ))

    return cursor.lastrowid


def count_turns_for_session(conn, session_id):
    """
    Return the number of turns already stored for a session.
    """
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM Turn
        WHERE SessionId = ?
    """, (session_id,))

    row = cursor.fetchone()
    return row[0] if row is not None else 0


def save_new_transcript_turns(conn, session_id, transcript):
    """
    Save only transcript entries that have not yet been persisted.
    Assumes transcript order is append-only and matches conversation order.
    Does not commit. Transaction control belongs to the caller.
    """
    cursor = conn.cursor()
    existing_count = count_turns_for_session(conn, session_id)

    new_turns = transcript[existing_count:]
    saved_turn_ids = []

    for turn in new_turns:
        speaker = turn["speaker"]
        message = turn["text"]
        timestamp = datetime.utcnow().isoformat()

        cursor.execute("""
            INSERT INTO Turn (
                SessionId,
                TimeOfMessage,
                Speaker,
                Message
            )
            VALUES (?, ?, ?, ?)
        """, (
            session_id,
            timestamp,
            speaker,
            message
        ))

        saved_turn_ids.append(cursor.lastrowid)

    return saved_turn_ids


def load_turns_for_session(conn, session_id):
    """
    Load all turns for a session in insertion order.
    Returns a list of dictionaries.
    """
    cursor = conn.cursor()

    cursor.execute("""
        SELECT TurnId, SessionId, TimeOfMessage, Speaker, Message
        FROM Turn
        WHERE SessionId = ?
        ORDER BY TurnId
    """, (session_id,))

    rows = cursor.fetchall()

    turns = []
    for row in rows:
        turns.append({
            "turn_id": row[0],
            "session_id": row[1],
            "time_of_message": row[2],
            "speaker": row[3],
            "message": row[4]
        })

    return turns