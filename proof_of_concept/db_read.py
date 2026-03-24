import sqlite3
import re
from config import MODEL
import pandas as pd


def get_connection():
    conn = sqlite3.connect('clerkship_dialogue.db')
    cursor = conn.cursor()
    return conn, cursor

def get_session_ids():
    """
    Retreives new session IDs for doctor-guided filtering

    Args:
        None

    Returns:
        session_ids (list)
    """
    conn, cursor = get_connection()
    # Fetch all values
    cursor.execute("SELECT SessionId FROM Session")
    session_ids = [row[0] for row in cursor.fetchall()]

    return session_ids

def get_conversations(session_id):
    conn, cursor = get_connection()
    sql = f'''
        SELECT Message, Speaker
        FROM Turn 
        WHERE SessionId = {session_id}
        '''
    df = pd.read_sql(sql, conn)
    return df

def get_summary(session_id):
    conn, cursor = get_connection()
    sql = f'''
        SELECT PreSummary, PostSummary
        FROM Summary 
        WHERE SessionId = {session_id}
        '''
    df = pd.read_sql(sql, conn)
    return df

def update_summary(session_id, df):
    conn, cursor = get_connection()
    post_summary = df['PostSummary'].values[0]
    sql = f'''
        UPDATE Summary
        SET PostSummary = '{post_summary}'
        WHERE SessionId = {session_id};
        '''
    cursor.execute(sql)
    conn.commit()
    conn.close()

def check_for_conversation_kg(session_id):
    """
    Checks if there are results in the 'KnowledgeGraphs' table filtered by SessionId.

    Args:
        db_path (str): The path to the SQLite database file.
        session_id (str or int): The SessionId to filter by.

    Returns:
        list: A list of tuples representing the rows that match the criteria.
              Returns an empty list if no matching rows are found.
    """
    conn, cursor = get_connection()

    # Execute the SQL query
    sql = f"""
        SELECT * 
        FROM KnowledgeGraphs 
        WHERE SessionId = {session_id}
        """
    cursor.execute(sql)

    # See if there are results returned
    results = cursor.fetchall()
    if len(results) > 0:
        return True
    else:
        return False

if __name__ == '__main__':
    pass