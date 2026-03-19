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

def add_new_session_data(session_id, model, session_start):
    """
    Extracts information from streamlit's session_state to add to database
    """
    session_name = f'Sess{session_id}'
    # start of conversation
    new_row = [session_id, session_name, session_start,
               None, None, None, 'active', model, session_start]
    add_data_to_db('Session', new_row)
    # print('session_state: ', session_state)
    # temporary static add to ensure database updates properly
    # new_row = [1, 'Sess1', '2024-03-06 02:11:00', '2024-03-06 02:11:00',
    #            'chest_pain', "{'symptom': 'dizziness', 'symptom': 'urinary'}", 
    #            'reviewed', 'v0', '2024-03-06 02:11:00']
    # add_data_to_db('Session', new_row)

def add_turn_data(session_id, time_of_message, speaker, message):
    """
    Extracts information from streamlit's session_state to add to database's Turn table
    """
    # write message to db
    new_row = [session_id, time_of_message, speaker, message]
    columns = ['SessionId', 'TimeOfMessage', 'Speaker', 'Message']
    add_data_to_db('Turn', new_row, columns)

def add_summary_data(session_id, pre_summary):
    """
    Extracts information from streamlit's session_state to add to database's Summary table
    """
    new_row = [session_id, pre_summary, None, None]
    add_data_to_db('Summary', new_row)

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

if __name__ == '__main__':
    pass