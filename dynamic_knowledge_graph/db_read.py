import sqlite3
import re
from config import MODEL
import pandas as pd
from datetime import datetime as dt

# team imports
from knowledge_graph import convert_df_to_kg 


def get_connection():
    """
    Connects to database

    Args:
        None

    Returns:
        conn - db connection object
        cursor - db cursor object    
    """
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
    # TODO: modifty this to search Turn for live updates
    cursor.execute("SELECT DISTINCT SessionId FROM Turn;")
    session_ids = [row[0] for row in cursor.fetchall()]

    return session_ids

def get_conversations(session_id):
    """
    Retrieves conversations from the Turn table based on the session ID.

    Args:
        session_id (int): The ID of the session to retrieve conversations for.

    Returns:
        df (pd.DataFrame): A DataFrame containing the Message and Speaker columns 
        from the Turn table for the specified session ID.
    """
    conn, cursor = get_connection()
    sql = f'''
        SELECT Message, Speaker
        FROM Turn 
        WHERE SessionId = {session_id}
        '''
    df = pd.read_sql(sql, conn)
    return df

def get_summary(session_id):
    """
    Retrieves summaries for a given session ID from the Summary table.

    Args:
        session_id (int): The ID of the session to retrieve summaries for.

    Returns:
        df (pd.DataFrame): A DataFrame containing the PreSummary and 
        PostSummary columns from the Summary table for the specified 
        session ID.
    """
    conn, cursor = get_connection()
    sql = f'''
        SELECT PreSummary, PostSummary
        FROM Summary 
        WHERE SessionId = {session_id}
        '''
    df = pd.read_sql(sql, conn)
    return df

def update_summary(session_id, df):
    """
    Updates the PostSummary for a given session ID in the Summary table.

    Args:
        session_id (int): The ID of the session to update.
        df (pd.DataFrame): A DataFrame containing the PostSummary data.  The function
                           assumes that the DataFrame has exactly one row and that
                           the 'PostSummary' column contains the value to be
                           inserted.

    Returns:
        None
    """
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

    # check for KnowledgeGraph table
    try:
        # Check if KnowledgeGraphs table exists
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='KnowledgeGraphs'")
        table_exists = cursor.fetchone() is not None

        if not table_exists:
            # Create the table if it doesn't exist
            df = pd.DataFrame({'head': [],
                               'relation': [],
                               'tail': [],
                               'SessionId': []})
            df.to_sql('KnowledgeGraphs', conn, if_exists='replace', index=False)
            print(f"Table 'KnowledgeGraphs' created successfully.")
    except:
        print('Unable to create KnowledgeGraph table')

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

def get_conversation_kg(session_id, relation_list):
    """
    Retrieves conversation knowledge graph data from the database.

    Args:
        session_id (str or int): The ID of the conversation session.
        relation_list (list): A list of relationships to filter the results.

    Returns:
        df (pd.DataFrame): A pandas DataFrame containing the filtered knowledge graph data.
    """
    conn, cursor = get_connection()
    # Execute the SQL query
    if len(relation_list) > 0:
        print(f'Filtering by {relation_list}')
        sql_list = "', '".join(map(str, relation_list))
        sql = f"""
            SELECT * 
            FROM KnowledgeGraphs 
            WHERE SessionId = {session_id}
            AND relation IN ('{sql_list}')
            """
    else:
        sql = f"""
            SELECT * 
            FROM KnowledgeGraphs 
            WHERE SessionId = {session_id}
            """
    df = pd.read_sql(sql, conn)
    # print(df.head())
    return df

def filter_conversation_kg(session_id, relation_list):
    """
    Filters conversation knowledge graph data based on session ID and relation list.

    Args:
        session_id (str or int): The ID of the conversation session.
        relation_list (list): A list of relationships to filter the results.

    Returns:
        df (pd.DataFrame): A pandas DataFrame containing the filtered knowledge graph data.
    """
    conn, cursor = get_connection()
    # convet list into SQL-friendly format
    sql_list = "', '".join(map(str, relation_list))
    # Execute the SQL query
    sql = f"""
        SELECT * 
        FROM KnowledgeGraphs 
        WHERE SessionId = {session_id}
        AND relation IN ('{sql_list}')
        """
    df = pd.read_sql(sql, conn)
    # print("Filtered kg", df.head())
    # might remove SessionId before returning (not in original kg)
    return df  # .drop('SessionId', axis=1)

def retreive_system_symptom_kg(session_id, turn_number=1):
    conn, cursor = get_connection()
    # query SymptomSystemKG, filtering by session_id and turn_number
    sql = f"""
        SELECT * 
        FROM SymptomSystemKG 
        WHERE SessionId = {session_id}
        AND turn = {turn_number};
        """
    # read this into a dataframe
    df = pd.read_sql(sql, conn)
    # convert to kg
    # TODO: check order of columns - system and relation are swapped
    df = df[['symptom', 'system', 'relation']].copy()
    df.columns = ['head', 'tail', 'relation']
    kg = convert_df_to_kg(df)
    print(f'Pulling system-symptom kg: Session {session_id}, Turn {turn_number}')
    return kg

def get_system_symptom_df(session_id, turn_number):
    """
    Returns system_symptom data for given session_id, turn_number
    """
    conn, cursor = get_connection()
    # query SymptomSystemKG, filtering by session_id and turn_number
    sql = f"""
        SELECT * 
        FROM SymptomSystemKG 
        WHERE SessionId = {session_id}
        AND turn = {turn_number};
        """
    # read this into a dataframe
    df = pd.read_sql(sql, conn)
    return df

def get_turns(session_id):
    """
    Returns a list of turns for a given session
    """
    conn, cursor = get_connection()
    # query SymptomSystemKG, filtering by session_id and turn_number
    sql = f"""
        SELECT DISTINCT turn 
        FROM SymptomSystemKG 
        WHERE SessionId = {session_id};
        """
    cursor.execute(sql)
    turns = [row[0] for row in cursor.fetchall()]
    return turns

def get_rankings(session_id, turn_number):
    """
    Retrieves rankings from the SystemRank table based on the session ID and turn number.

    Args:
        session_id (int): The ID of the session
        turn_number (int): The turn in the conversation

    Returns:
        df (pd.DataFrame): A DataFrame containing the rank, system and drilldown_start 
        columns from the SystemRank table for the specified session ID and turn number.
    """
    conn, cursor = get_connection()
    sql = f'''
        SELECT rank, system, drilldown_start
        FROM SystemRank 
        WHERE SessionId = {session_id}
            AND turn_number = {turn_number}
        '''
    df = pd.read_sql(sql, conn)
    return df

def get_previous_drilldown_messages(session_id):
    conn, cursor = get_connection()
    sql = f'''
        SELECT MAX(timestamp) 
        FROM SystemRank 
        WHERE SessionId = {session_id} 
            AND drilldown_start = 1;
        '''
    cursor.execute(sql)
    # pull previous system drilldown dialogue
    drilldown_datetime = [dt.strptime(row[0],"%Y-%m-%d %H:%M:%S.%f")
                           for row in cursor.fetchall()][0]
    """
    I have a throbbing feeling in my head
    Yes, there is pressure just above my eyes
    It feels like a dull pain, but it is always there
    """
    # requery all conversations from Turn greater than or equal to datetime
    sql = f"""
        SELECT *
        FROM Turn
        WHERE SessionId = {session_id}
            AND TimeOfMessage >= '{drilldown_datetime}'
        """
    df = pd.read_sql(sql, conn)
    # print(df)
    # TODO: filter to message column and split results into text
    message_string = ""
    for index, row in df.iterrows():
        message_string += f"{row['Speaker']}: {row['Message']}\n"
    return message_string, drilldown_datetime

def check_prev_rank_1(session_id, drilldown_datetime):
    conn, cursor = get_connection()
    # rank, system, timestamp
    sql = f'''
    SELECT system
    FROM SystemRank 
    WHERE SessionId = {session_id} 
        AND timestamp >= '{drilldown_datetime}'
        AND rank = 1
    ORDER BY timestamp;
    '''
    cursor.execute(sql)
    rank_1_list = [row[0] for row in cursor.fetchall()]
    print('System rank 1 history:', rank_1_list)
    freq_system = check_repeating_strings(rank_1_list)
    return freq_system

def check_symptom_rank_1(session_id, symptom_phase):
    conn, cursor = get_connection()
    # rank, symptom, SessionId, turn_number, timestamp, symptom_phase
    sql = f'''
    SELECT symptom
    FROM SymptomRank 
    WHERE SessionId = {session_id} 
        AND symptom_phase = {symptom_phase}
        AND rank = 1
    ORDER BY timestamp;
    '''
    print(sql)
    cursor.execute(sql)
    rank_1_list = [row[0] for row in cursor.fetchall()]
    print('Symptom rank 1 history:', rank_1_list)
    freq_symptom = check_repeating_strings(rank_1_list)
    return freq_symptom

def check_repeating_strings(data_list):
    """Checks if a list contains 3 repeating string values.

    Args:
        data_list: A list of strings.

    Returns:
        A tuple: (string with 3 counts, False) if a string appears 3 times,
                 (None, True) if there are 3 repeating strings,
                 (None, False) otherwise.
    """
    counts = {}
    for item in data_list:
        if item in counts:
            counts[item] += 1
        else:
            counts[item] = 1

    for item, count in counts.items():
        if count == 3:
            return item

    return None

def check_session_consistency():
    conn, cursor = get_connection()
    sql = """
        SELECT
            MAX(CASE WHEN table_name = 'SystemRank' THEN max_total END) AS SystemRank_last_session,
            MAX(CASE WHEN table_name = 'SymptomSystemKG' THEN max_total END) AS SymptomSystemKG_last_session,
            MAX(CASE WHEN table_name = 'KnowledgeGraphs' THEN max_total END) AS KnowledgeGraphs_last_session,
            MAX(CASE WHEN table_name = 'SessionMetric' THEN max_total END) AS SessionMetric_last_session,
            MAX(CASE WHEN table_name = 'Summary' THEN max_total END) AS Summary_last_session,
            MAX(CASE WHEN table_name = 'Turn' THEN max_total END) AS Turn_last_session,
            MAX(CASE WHEN table_name = 'Session' THEN max_total END) AS Session_last_session
        FROM (
            SELECT
                'SymptomRank' AS table_name, MAX(SessionId) AS max_total FROM SymptomRank
            UNION ALL
            SELECT
                'SystemRank' AS table_name, MAX(SessionId) AS max_total FROM SystemRank
            UNION ALL
            SELECT
                'SymptomSystemKG' AS table_name, MAX(SessionId) AS max_total FROM SymptomSystemKG
            UNION ALL
            SELECT
                'KnowledgeGraphs' AS table_name, MAX(SessionId) AS max_total FROM KnowledgeGraphs
            UNION ALL
            SELECT
                'SessionMetric' AS table_name, MAX(SessionId) AS max_total FROM SessionMetric
            UNION ALL
            SELECT
                'Summary' AS table_name, MAX(SessionId) AS max_total FROM Summary
            UNION ALL
            SELECT
                'Turn' AS table_name, MAX(SessionId) AS max_total FROM Turn
            UNION ALL
            SELECT
                'Session' AS table_name, MAX(SessionId) AS max_total FROM Session
        ) AS all_tables;
        """
    df = pd.read_sql(sql, conn)
    df = df.T
    print(df)
    
def get_symptom_rankings(session_id, turn_number):
    """
    Retrieves rankings from the SystemRank table based on the session ID and turn number.

    Args:
        session_id (int): The ID of the session
        turn_number (int): The turn in the conversation

    Returns:
        df (pd.DataFrame): A DataFrame containing the rank, system and drilldown_start 
        columns from the SystemRank table for the specified session ID and turn number.
    """
    conn, cursor = get_connection()
    sql = f'''
        SELECT rank, symptom
        FROM SymptomRank 
        WHERE SessionId = {session_id}
            AND turn_number = {turn_number}
        '''
    df = pd.read_sql(sql, conn)
    return df

if __name__ == '__main__':
    pass
