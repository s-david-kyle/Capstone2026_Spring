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
    

if __name__ == '__main__':
    pass