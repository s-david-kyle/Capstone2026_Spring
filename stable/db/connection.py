import sqlite3

# -----------------------------------------------------------
# Database connection utility
# -----------------------------------------------------------

def create_connection(db_path: str = "clerkship_dialogue.db"):
    """
    Create and return a connection to the SQLite database.

    Parameters
    ----------
    db_path : str
        Path to the SQLite database file. If the file does not exist,
        SQLite will create it automatically.

    Returns
    -------
    sqlite3.Connection
        Active connection object used for executing SQL commands.
    """

    # Open or create the SQLite database file
    conn = sqlite3.connect(db_path)

    # Enable foreign key constraints because SQLite disables them by default
    conn.execute("PRAGMA foreign_keys = ON;")

    return conn
