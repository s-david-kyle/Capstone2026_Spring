import pandas as pd
import sqlite3
import re
from config import MODEL

# team modules
from db_read import get_connection

def get_session_id():
    """
    Retreives new session ID for patient conversation. Performed at the start of interaction.

    Args:
        None

    Returns:
        session_id (int)
    """
    conn = sqlite3.connect('clerkship_dialogue.db')
    cursor = conn.cursor()
    # Fetch all values
    cursor.execute("SELECT SessionId FROM Session")
    values = [row[0] for row in cursor.fetchall()]

    # Find the maximum, increment
    if values:
        greatest_number = max(values)
    else:
        greatest_number = 0
    session_id = greatest_number + 1
    return session_id

def add_new_session_data(session_id, session_start, session_end, clinical_summary, symptoms):
    """
    Adds new session data to the database.

    Args:
        session_id (int): The unique identifier for the session.
        session_start (datetime): The start time of the session.
        session_end (datetime): The end time of the session.
        clinical_summary (str): A textual summary of the clinical session.
        symptoms (list): A list of symptoms associated with the session.

    Returns:
        None
    """    
    session_name = f'Sess{session_id}'
    # parse out primary_complaint with regex
    match = re.search(r"Chief Complaint:\s*(.*)", clinical_summary)
    if match:
        extracted_text = match.group(1)
        # remove ** from beginning of text
        extracted_text = re.sub(r"\*\*|\*", "", extracted_text)
        extracted_text = extracted_text.strip()
        primary_complaint = extracted_text
    else:
        primary_complaint = "Primary Complaint not found."

    # parse out secondary_complaint with symptom list
    symptom_json = []
    for sublist in symptoms:
        symptom_json.append({'symptoms': sublist})
    symptom_json = str(symptom_json)

    # format data for table
    new_row = [session_id, session_name, session_start,
               session_end, primary_complaint, symptom_json, 
               'active', MODEL, session_start]
    add_data_to_db('Session', new_row)

def add_turn_data(session_id, time_of_message, speaker, message):
    """
    Adds turn data to the database.

    Args:
        session_id (int): The unique identifier for the session.
        time_of_message (datetime): The timestamp of the message.
        speaker (str): The speaker of the message.
        message (str): The content of the message.

    Returns:
        None
    """
    new_row = [session_id, time_of_message, speaker, message]
    columns = ['SessionId', 'TimeOfMessage', 'Speaker', 'Message']
    add_data_to_db('Turn', new_row, columns)

def add_summary_data(session_id, pre_summary):
    """
    Adds summary data to the database.

    Args:
        session_id (int): The unique identifier for the session.
        pre_summary (str): The session summary.

    Returns:
        None
    """
    new_row = [session_id, pre_summary, None, None]
    add_data_to_db('Summary', new_row)

def add_session_metric_data(session_id):
    """
    Adds session metric data to the database.

    Args:
        session_id (int): The unique identifier for the session.

    Returns:
        None
    """
    # calculate patient_turn_count
    sql = f"""
            SELECT COUNT(TurnId) 
            FROM Turn 
            WHERE SessionId = {session_id} AND Speaker = 'patient';
            """
    patient_turn_count = run_sql_return_result(sql)[0]
    # calculate system_turn_count
    sql = f"""
            SELECT COUNT(TurnId) 
            FROM Turn 
            WHERE SessionId = {session_id} AND Speaker = 'system';
            """
    system_turn_count = run_sql_return_result(sql)[0]
    # TODO: calculate required_fields_total
    # TODO: calculate required_fields_filled
    # TODO: calculate completion_rate
    # TODO: calculate missing_fields_count
    # TODO: create list of missing_fields
    # calculate summary_length - NOTE: this is presummary not postsummary
    sql = f"""
            SELECT LENGTH(PreSummary) 
            FROM Summary 
            WHERE SessionId = {session_id};
            """
    summary_length = run_sql_return_result(sql)[0]
    # update what you can currently
    new_row = [session_id, patient_turn_count, system_turn_count, summary_length]
    columns = ['SessionId', 'PatientTurnCount', 'SystemTurnCount', 'SummaryLength']
    add_data_to_db('SessionMetric', new_row, columns)

def run_sql_return_result(sql):
    """
    Runs a SQL query and returns the first result.

    Args:
        sql (str): The SQL query to execute.

    Returns:
        result (str): The first row returned by the query, or None if no rows are returned.
    """
    conn = sqlite3.connect('clerkship_dialogue.db')
    cursor = conn.cursor()
    cursor.execute(sql)
    result = cursor.fetchone()
    conn.close()
    return result

def add_data_to_db(table_name, data, columns=None):
    """
    Connects to a SQLite database, adds a new row to a table,
    and closes the connection.

    Args:
        table_name (str): The name of the table to add the data to.
        data (list): A list of values to insert into the table.  
                      The order of the values must match the columns
                      in the table.
        columns (list): Optional. List of columns to update if not all
                        are specified.
    Returns:
        None
    """
    try:
        conn = sqlite3.connect('clerkship_dialogue.db')
        cursor = conn.cursor()

        if columns == None:
        # Construct the SQL query, execute and commit
            sql = f"INSERT INTO {table_name} VALUES ({','.join(['?'] * len(data))})"
            cursor.execute(sql, data)
            conn.commit()
        else:
            sql = """INSERT INTO {table_name} ({columns}) VALUES ({data})""".format(
                table_name=table_name,
                columns=','.join(columns),
                data=','.join(['?'] * len(data))
            )
            cursor.execute(sql, data)
            conn.commit()

        print(f"Row added successfully to table '{table_name}'.")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

    finally:
        if conn:
            conn.close()

def push_kg_to_db(df, session, overwrite=False):
    """
    Pushes a pandas DataFrame to a SQLite database, filtering by SessionId
    and adding only if the data doesn't already exist.
    """
    # add session to dataframe
    df['SessionId'] = session

    conn, cursor = get_connection()

    try:
        # Check if KnowledgeGraphs table exists
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='KnowledgeGraphs'")
        table_exists = cursor.fetchone() is not None

        if not table_exists:
            # Create the table if it doesn't exist
            df.to_sql('KnowledgeGraphs', conn, if_exists='replace', index=False)
            print(f"Table 'KnowledgeGraphs' created successfully.")
        else:
            # Filter the DataFrame by SessionId and check for duplicates
            existing_data = pd.read_sql_query(f"SELECT * FROM KnowledgeGraphs WHERE SessionId = '{df['SessionId'].iloc[0]}';", conn)
            if existing_data.empty:
                # Add the DataFrame to the database if no duplicates are found
                df.to_sql('KnowledgeGraphs', conn, if_exists='append', index=False)
                print(f"DataFrame added to table 'KnowledgeGraphs'.")
            # TODO: check for overwrite flag
            elif overwrite:
                print('overwriting kg')
                # wipe out data then push
                sql_query = f"""DELETE 
                            FROM KnowledgeGraphs
                            WHERE SessionId = '{session}';
                            """
                cursor.execute(sql_query)
                conn.commit()
                df.to_sql('KnowledgeGraphs', conn, if_exists='append', index=False)
                
            else:
                print(f"Data with SessionId '{df['SessionId'].iloc[0]}' already exists in table 'KnowledgeGraphs'.")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        conn.close()

if __name__ == '__main__':
    pass