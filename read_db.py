# The user has provided a script and has requested to execute it to print the database content to the terminal.
# We will run this script with the provided history.db file.
import sqlite3


# Function to connect to the SQLite database
def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as error:
        print(f"Error connecting to database: {error}")
        return None

# Function to query all rows in the history table
def select_all_history(conn):
    cursor = conn.cursor()
    query = "SELECT * FROM history;"
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        return rows
    except sqlite3.Error as error:
        print(f"Error reading from table: {error}")
        return None

# Main function to execute the script logic
def main(db_file):
    database = db_file

    # Create a database connection
    conn = create_connection(database)
    if conn is not None:
        # Query and display the history table content
        rows = select_all_history(conn)
        for row in rows:
            print(row)
        conn.close()
    else:
        print("Error! cannot create the database connection.")

# Assuming the database file is named 'history.db' and is stored at '/mnt/data/'
db_path = "history.db"
main(db_path)  # Execute the main function with the database path
