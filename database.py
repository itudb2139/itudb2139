import sqlite3 
from sqlite3 import Error

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM total_fertility WHERE (country_iso_code = \"AZE\" AND year = 2000)")
        value, = cursor.fetchone()
        print(value)
        if conn:
            conn.close()

if __name__ == '__main__':
    create_connection(r"pythonsqlite.db")