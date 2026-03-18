import sqlite3


def add_data_to_db(table_name, data):
    """
    Connects to a SQLite database, adds a new row to a table,
    and closes the connection.

    Args:
        db_name (str): The name of the SQLite database file.
        table_name (str): The name of the table to add the data to.
        data (list): A list of values to insert into the table.  
                      The order of the values must match the columns
                      in the table.
    """
    try:
        conn = sqlite3.connect('clerkship_dialogue.db')
        cursor = conn.cursor()

        # Construct the SQL query
        sql = f"INSERT INTO {table_name} VALUES ({','.join(['?'] * len(data))})"

        # Execute the query with the data
        cursor.execute(sql, data)

        # Commit the changes
        conn.commit()

        print(f"Row added successfully to table '{table_name}'.")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    # Example Usage:
    # table = 'customers'
    # customer_data = ['Alice', 'Smith', '123 Main St', 'Anytown']

    # add_data_to_db(table, customer_data)
    pass