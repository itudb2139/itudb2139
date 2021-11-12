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

    def is_applicable(self, age, table):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "SELECT DISTINCT AGE_GROUP FROM {}".format(table)
            cursor.execute(query)
            groups = cursor.fetchall()
        for group in groups:
            if(is_age_in_range(age, group[0])):
                return True
        return False
        
    def get_tobacco_use(self, country, sex):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "SELECT VALUE FROM tobacco_use WHERE (COUNTRY = ? AND SEX = ?) ORDER BY YEAR DESC"
            cursor.execute(query, (country, sex))
        result = cursor.fetchone()
        if result == None:
            return None
        return result[0]

    def get_tuberculosis(self, country, sex, age):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "SELECT VALUE, AGE_GROUP FROM tuberculosis_rate WHERE (COUNTRY = ? AND SEX = ?)"
            cursor.execute(query, (country, sex))
            groups = cursor.fetchall()
            group_total = 0
            group_count = 0
            for group in groups:
                if is_age_in_range(age, group[1]):
                    return group[0] / 1000
                else:
                    group_total += group[0]
                group_count = group_count + 1
            return group_total / (group_count * 1000)

    def get_hepb(self, country, sex, age):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "SELECT VALUE, AGE_GROUP FROM hepb_rate WHERE (COUNTRY = ? AND SEX = ?)"
            cursor.execute(query, (country, sex))
            groups = cursor.fetchall()
            group_total = 0
            group_count = 0
            for group in groups:
                if is_age_in_range(age, group[1]):
                    return group[0] / 1000
                else:
                    group_total += group[0]
                group_count = group_count + 1
            return group_total / (group_count * 1000)

    def get_education(self, country, sex):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "SELECT VALUE FROM young_education WHERE (COUNTRY = ? AND SEX = ?) ORDER BY YEAR DESC"
            cursor.execute(query, (country, sex))
        result = cursor.fetchone()
        if result == None:
            return None
        return result[0]

    def get_poverty(self, country):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "SELECT VALUE FROM population_poverty WHERE (COUNTRY = ?) ORDER BY YEAR DESC"
            cursor.execute(query, (country,))
        result = cursor.fetchone()
        if result == None:
            return None
        return result[0]

    def get_life_expectancy_birth(self, country, sex):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "SELECT VALUE FROM life_expectancy_birth WHERE (COUNTRY = ? AND SEX = ? AND YEAR = 2021)"
            cursor.execute(query, (country, sex))
        return cursor.fetchone()[0]

    def get_life_expectancy_60(self, country, sex):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "SELECT VALUE FROM life_expectancy_old WHERE (COUNTRY = ? AND SEX = ?)"
            cursor.execute(query, (country, sex))
        result = cursor.fetchone()
        if result == None:
            return None
        return result[0]

    def get_physical_activity(self, country, sex):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "SELECT VALUE FROM physical_activity_adolescents WHERE (COUNTRY = ? AND SEX = ?) ORDER BY YEAR DESC"
            cursor.execute(query, (country, sex))
        result = cursor.fetchone()
        if result == None:
            return None
        return result[0]

    def get_drinking(self, country, sex):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "SELECT VALUE FROM drinking_adolescents WHERE (COUNTRY = ? AND SEX = ?)"
            cursor.execute(query, (country, sex))
        result = cursor.fetchone()
        if result == None:
            return None
        return result[0]

    def get_sanitation_services(self, country):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "SELECT VALUE FROM sanitation_services WHERE (COUNTRY = ?) ORDER BY YEAR DESC, RESIDENCE_AREA"
            cursor.execute(query, (country,))
        result = cursor.fetchone()
        if result == None:
            return None
        return result[0]

    def get_water_services(self, country):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "SELECT VALUE FROM water_services WHERE (COUNTRY = ?) ORDER BY YEAR DESC, RESIDENCE_AREA"
            cursor.execute(query, (country,))
        result = cursor.fetchone()
        if result == None:
            return None
        return result[0]

    def get_adolescent_mortality(self, country, sex, age):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "SELECT VALUE, AGE_GROUP FROM adolescents_mortality_rate WHERE (COUNTRY = ? AND SEX = ?)"
            cursor.execute(query, (country, sex))
            groups = cursor.fetchall()
            if groups == None:
                return None
            best_fitting_group = None
            for group in groups:
                if is_age_in_range(age, group[1]):
                    if best_fitting_group == None or range_width(group[1]) < range_width(best_fitting_group[1]):
                        best_fitting_group = group
            if best_fitting_group == None:
                return None
            return best_fitting_group[0] / 1000

    def get_mortality_causes(self, country, sex, age):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "SELECT CAUSE, AGE_GROUP FROM adolescent_mortality_causes WHERE (COUNTRY = ? AND SEX = ? AND VALUE = 1)"
            cursor.execute(query, (country, sex))
            groups = cursor.fetchall()
            if groups == None:
                return None
            best_fitting_group = None
            for group in groups:
                if is_age_in_range(age, group[1]):
                    if best_fitting_group == None or range_width(group[1]) < range_width(best_fitting_group[1]):
                        best_fitting_group = group
            if best_fitting_group == None:
                return None
            return best_fitting_group[0]



def is_age_in_range(age, group):
    if "+" in group:
        return age >= int(group.replace("+", ""))
    limits = group.split("-")
    return age >= int(limits[0]) and age <= int(limits[1])

def range_width(group):
    limits = group.split("-")
    return int(limits[1]) - int(limits[0]) + 1