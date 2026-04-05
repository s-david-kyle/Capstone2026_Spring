from datetime import datetime


def create_session(
    conn,
    session_name,
    model_version,
    primary_complaint = None,
    secondary_complaint = None,
    status = "active"
):
    """
    Create a new session row and return the new SessionId.
    """
    cursor = conn.cursor()

    created_at = datetime.utcnow().isoformat()
    modified_at = created_at

    cursor.execute("""
        INSERT INTO Session (
            SessionName,
            CreatedAt,
            EndedAt,
            PrimaryComplaint,
            SecondaryComplaint,
            Status,
            ModelVersion,
            ModifiedAt
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        session_name,
        created_at,
        None,
        primary_complaint,
        secondary_complaint,
        status,
        model_version,
        modified_at
    ))

    conn.commit()
    return cursor.lastrowid