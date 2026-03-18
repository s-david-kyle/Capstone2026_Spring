import sqlite3
from datetime import datetime as dt

def get_session_id():
    """
    Retreives new session ID for patient conversation. Performed at the start of interaction.
    """
    # sql = f'INSERT INTO {table_name} (id) VALUES (next(sqlite_sequence))'
    conn = sqlite3.connect('clerkship_dialogue.db')
    cursor = conn.cursor()
    # 1. Fetch all values
    cursor.execute("SELECT SessionId FROM Session")
    values = [row[0] for row in cursor.fetchall()]

    # 2. Find the maximum
    if values:
        greatest_number = max(values)
    else:
        greatest_number = 0
    session_id = greatest_number + 1
    return session_id

def add_session_data(session_state, session_id, model):
    """
    Extracts information from streamlit's session_state to add to database
    """
    session_name = f'Sess{session_id}'
    created_at = dt.now()
    # start of conversation
    new_row = [session_id, session_name, created_at,
               None, None, None, 'active', model, created_at]
    add_data_to_db('Session', new_row)
    print('session_state: ', session_state)
    # temporary static add to ensure database updates properly
    # new_row = [1, 'Sess1', '2024-03-06 02:11:00', '2024-03-06 02:11:00',
    #            'chest_pain', "{'symptom': 'dizziness', 'symptom': 'urinary'}", 
    #            'reviewed', 'v0', '2024-03-06 02:11:00']
    # add_data_to_db('Session', new_row)

def add_turn_data(session_state, session_id, model):
    """
    Extracts information from streamlit's session_state to add to database's Turn table
    """
    time_of_message = dt.now()
    # TODO: figure out turn_id logic in db (will it create the number automatically?)
    
    print('session_state: ', session_state)

def add_data_to_db(table_name, data):
    """
    Connects to a SQLite database, adds a new row to a table,
    and closes the connection.

    Args:
        table_name (str): The name of the table to add the data to.
        data (list): A list of values to insert into the table.  
                      The order of the values must match the columns
                      in the table.
    """
    try:
        conn = sqlite3.connect('clerkship_dialogue.db')
        cursor = conn.cursor()

        # Construct the SQL query, execute and commit
        sql = f"INSERT INTO {table_name} VALUES ({','.join(['?'] * len(data))})"
        cursor.execute(sql, data)
        conn.commit()

        print(f"Row added successfully to table '{table_name}'.")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    pass