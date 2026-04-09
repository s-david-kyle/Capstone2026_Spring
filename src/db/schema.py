# -----------------------------------------------------------
# Database schema creation
# Responsible for building the database tables and indexes
# -----------------------------------------------------------

def create_tables(conn):
    """Create all required database tables if they do not exist."""

    # Create a cursor so SQL commands can be executed
    cursor = conn.cursor()

    # -------------------------
    # Session Table
    # -------------------------
    # Stores one row per conversation session.
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Session (
        SessionId INTEGER PRIMARY KEY NOT NULL UNIQUE,
        SessionName TEXT NOT NULL,
        CreatedAt DATETIME NOT NULL,
        EndedAt DATETIME,
        PrimaryComplaint TEXT,
        SecondaryComplaint  TEXT,          -- JSON list of secondary complaints
        Status TEXT DEFAULT 'active',
        ModelVersion TEXT NOT NULL,
        ModifiedAt DATETIME
    )
    """)

    # -------------------------
    # Turn Table
    # -------------------------
    # Stores each individual message in a conversation.
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Turn (
        TurnId INTEGER PRIMARY KEY AUTOINCREMENT,
        SessionId INTEGER NOT NULL,
        TimeOfMessage DATETIME NOT NULL,  
        Speaker TEXT NOT NULL CHECK (Speaker IN ('patient', 'system')),
        Message TEXT NOT NULL,
        FOREIGN KEY (SessionId) REFERENCES Session(SessionId) ON DELETE CASCADE
    )
    """)

    # -------------------------
    # Summary Table
    # -------------------------
    # Stores LLM generated and clinician-edited summaries.
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Summary (
        SessionId INTEGER PRIMARY KEY,
        PreSummary TEXT,
        PostSummary TEXT,
        ReviewedAt DATETIME,
        FOREIGN KEY (SessionId) REFERENCES Session(SessionId) ON DELETE CASCADE
    )
    """)

    # -------------------------
    # SessionMetric Table
    # -------------------------
    # Stores calculated metrics for each completed or reviewed session.
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS SessionMetric (
        SessionId INTEGER PRIMARY KEY,
        PatientTurnCount INTEGER NOT NULL,
        SystemTurnCount INTEGER NOT NULL,
        RequiredFieldsTotal INTEGER,
        RequiredFieldsFilled INTEGER,
        CompletionRate REAL,
        MissingFieldsCount INTEGER,
        MissingFields           TEXT,          -- JSON list of missing fields
        SummaryLength INTEGER,
        CoverageMissedCount INTEGER,
        CoverageMissedFields TEXT,          -- JSON list of missed coverage fields
        SimilarityRatio REAL,
        MajorEditFlag INTEGER,              -- 0 or 1
        ClinicianAcceptance INTEGER,        -- 0 or 1
        HallucinationFlagCount INTEGER,
        HallucinationNotes TEXT,          -- JSON list of hallucination notes
        FOREIGN KEY (SessionId) REFERENCES Session(SessionId) ON DELETE CASCADE
    )
    """)

    # These indexes speed up common lookups.
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_turn_session ON Turn(SessionId);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_session_status ON Session(Status);")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS IntakeState (
    IntakeStateId INTEGER PRIMARY KEY AUTOINCREMENT,
    SessionId INTEGER NOT NULL UNIQUE,
    IntakeJson TEXT NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    FOREIGN KEY (SessionId) REFERENCES Session(SessionId) ON DELETE CASCADE
    )
    """)
    
    # Save all changes
    conn.commit()
