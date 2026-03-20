# -----------------------------------------------------------
# Initializes the database and creates tables
# -----------------------------------------------------------

from db.connection import create_connection
from db.schema import create_tables

def main():
    """Initialize the SQLite database and create all tables."""

    conn = create_connection()

    # Create all tables and indexes if they do not already exist.
    create_tables(conn)

    print("Database and tables created successfully.")

    conn.close()


# Only run main() when this file is executed directly.
if __name__ == "__main__":
    main()
