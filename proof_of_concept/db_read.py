import sqlite3
import re
from config import MODEL

# TODO: remove these functions once you've built new ones
def get_session_ids():
    """
    Retreives new session IDs for doctor-guided filtering

    Args:
        None

    Returns:
        session_ids (list)
    """
    conn = sqlite3.connect('clerkship_dialogue.db')
    cursor = conn.cursor()
    # Fetch all values
    cursor.execute("SELECT SessionId FROM Session")
    session_ids = [row[0] for row in cursor.fetchall()]

    return session_ids

if __name__ == '__main__':
    pass