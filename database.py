import sqlite3
from sqlite3.dbapi2 import Cursor 

class Database:
    def __init__(self, dbfile = r"pythonsqlite.db"):
        self.dbfile = dbfile

    def add_user(self, first_name, last_name, gender, country, birthday, email, password_hash):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "INSERT INTO users (NAME, LAST_NAME, GENDER, COUNTRY, BIRTHDAY, EMAIL, PASSWORD) VALUES (?, ?, ?, ?, ?, ?, ?)"
            cursor.execute(query, (first_name, last_name, gender, country, birthday, email, password_hash))
            connection.commit()
        return cursor.lastrowid

    def update_user(self, id, name, last_name, gender, country, birthday, email):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "UPDATE users SET NAME = ?, LAST_NAME = ?, GENDER = ?, COUNTRY = ?, BIRTHDAY = ?, EMAIL = ? WHERE (ID = ?)"
            cursor.execute(query, (name, last_name, gender, country, birthday, email, id))
            connection.commit()

    def delete_user(self, id):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "DELETE FROM users WHERE (ID = ?)"
            cursor.execute(query, (id,))
            connection.commit()

    def get_countries(self):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "SELECT DISTINCT COUNTRY FROM total_fertility"
            cursor.execute(query)
        return cursor.fetchall()

    def get_password(self, email):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "SELECT PASSWORD FROM users WHERE (EMAIL = ?)"
            cursor.execute(query, (email,))
        return cursor.fetchone()

    def get_user(self, value, parameter = "ID"):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "SELECT * FROM users WHERE ({} = ?)".format(parameter) 
            cursor.execute(query, (value,))
        return cursor.fetchone()

    def get_fertility(self, country):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "SELECT VALUE FROM total_fertility WHERE (COUNTRY = ? AND YEAR = 2020)"
            cursor.execute(query, (country, ))
        return cursor.fetchone()
