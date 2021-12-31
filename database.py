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
            query = "PRAGMA foreign_keys=on"
            cursor.execute(query)
            query = "DELETE FROM users WHERE (ID = ?)"
            cursor.execute(query, (id,))
            connection.commit()

    # Form Table
    def add_form(self, siblings, grandparent_age, education, tobacco, alcohol, user_id):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "INSERT INTO form (SIBLINGS, GR_AGE, EDUCATION, TOBACCO, ALCOHOL, USER_ID) VALUES (?, ?, ?, ?, ?, ?)"
            cursor.execute(query, (siblings, grandparent_age, education, tobacco, alcohol, user_id))
            connection.commit()
        return cursor.lastrowid

    def add_causes(self, user_id, cause):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "INSERT INTO mortality_causes (USER_ID, CAUSE) VALUES (?, ?)"
            cursor.execute(query, (user_id, cause))
            connection.commit()
        return cursor.lastrowid

    def update_form(self, siblings, grandparent_age, education, tobacco, alcohol, user_id):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "UPDATE form SET SIBLINGS = ?, GR_AGE = ?, EDUCATION = ?, TOBACCO = ?, ALCOHOL = ? WHERE (USER_ID = ?)"
            cursor.execute(query, (siblings, grandparent_age, education, tobacco, alcohol, user_id))
            connection.commit()

    def update_causes(self, user_id, causes):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "DELETE FROM mortality_causes WHERE (USER_ID = ?)"
            cursor.execute(query, (user_id, ))
            connection.commit()
        for cause in causes:
            self.add_causes(user_id, cause)

    def delete_form(self, user_id):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "DELETE FROM form WHERE (USER_ID = ?)"
            cursor.execute(query, (user_id, ))
            query = "DELETE FROM mortality_causes WHERE (USER_ID = ?)"
            cursor.execute(query, (user_id, ))
            connection.commit()

    # Review table
    def add_review(self, experience, recommend, accuracy, more_statistics, comment, date, user_id):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "INSERT INTO review (EXPERIENCE, RECOMMEND, ACCURACY, MORE_STATISTICS, COMMENTS, DATE, USER_ID) VALUES (?, ?, ?, ?, ?, ?, ?)"
            cursor.execute(query, (experience, recommend, accuracy, more_statistics, comment, date, user_id))
            connection.commit()
        return cursor.lastrowid

    def update_review(self, experience, recommend, accuracy, more_statistics, comments, date, user_id):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "UPDATE review SET EXPERIENCE = ?, RECOMMEND = ?, ACCURACY = ?, MORE_STATISTICS = ?, COMMENTS = ?, DATE = ? WHERE (USER_ID = ?)"
            cursor.execute(query, (experience, recommend, accuracy, more_statistics, comments, date, user_id))
            connection.commit()

    def delete_review(self, user_id):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "DELETE FROM review WHERE (USER_ID = ?)"
            cursor.execute(query, (user_id, ))
            connection.commit()

    # Login
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

    # Form utility
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

    def get_countries(self):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "SELECT DISTINCT COUNTRY FROM total_fertility"
            cursor.execute(query)
        return cursor.fetchall()

    def get_mortality_causes_form(self, country, sex):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "SELECT DISTINCT CAUSE FROM adolescent_mortality_causes WHERE (COUNTRY = ? AND SEX = ?) ORDER BY CAUSE ASC"
            cursor.execute(query, (country, sex))
        return cursor.fetchall()

    # Dataset access
    def get_fertility(self, country):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "SELECT VALUE FROM total_fertility WHERE (COUNTRY = ? AND YEAR = 2020)"
            cursor.execute(query, (country, ))
        return cursor.fetchone()
        
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
            #If the user fits in one of the age groups, the value for that age group is returned
            for group in groups:
                if is_age_in_range(age, group[1]):
                    #Divide by 1000, since the data is given per 100 000 population
                    return group[0] / 1000
                else:
                    #If the user does not fit in any of the age groups, the total and then the average value is calculated
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
            #Works in a similar way to the above function
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
        #If nothing was found, the user's country is not in the dataset, return None
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
                    #Method to find the best fitting group for the current user
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
                #The method is similar to the function above
                if is_age_in_range(age, group[1]):
                    if best_fitting_group == None or range_width(group[1]) < range_width(best_fitting_group[1]):
                        best_fitting_group = group
            if best_fitting_group == None:
                return None
            return best_fitting_group[0]

    #Form dataset access
    def get_user_form(self, id):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "SELECT * FROM form WHERE (USER_ID = ?)"
            cursor.execute(query, (id, ))
        return cursor.fetchone()

    def get_user_causes(self, id):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "SELECT * FROM mortality_causes WHERE (USER_ID = ?)"
            cursor.execute(query, (id, ))
        rows = cursor.fetchall()
        #If no causes were selected, the function returns None
        if rows == None:
            return None
        #Create an array of all entered causes
        causes = [row[1] for row in rows]

        return causes

    def get_review(self, id):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "SELECT * FROM review WHERE (USER_ID = ?)"
            cursor.execute(query, (id, ))
        return cursor.fetchone()

    #Data access for the home page
    def get_most_births(self):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "SELECT COUNTRY, VALUE FROM total_fertility WHERE (YEAR = 2020) ORDER BY VALUE DESC"
            cursor.execute(query)
        return cursor.fetchone()

    def get_least_births(self):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "SELECT COUNTRY, VALUE FROM total_fertility WHERE (YEAR = 2020) ORDER BY VALUE ASC"
            cursor.execute(query)
        return cursor.fetchone()

    def get_most_education(self):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "SELECT COUNTRY, VALUE FROM young_education WHERE (SEX = 'Both sexes') ORDER BY VALUE DESC"
            cursor.execute(query)
        return cursor.fetchone()

    def get_least_education(self):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "SELECT COUNTRY, VALUE FROM young_education WHERE (SEX = 'Both sexes') ORDER BY VALUE ASC"
            cursor.execute(query)
        return cursor.fetchone()

    def get_most_tobacco(self):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "SELECT COUNTRY, VALUE FROM tobacco_use WHERE (SEX = 'Both sexes') ORDER BY VALUE DESC"
            cursor.execute(query)
        return cursor.fetchone()

    def get_least_tobacco(self):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "SELECT COUNTRY, VALUE FROM tobacco_use WHERE (SEX = 'Both sexes') ORDER BY VALUE ASC"
            cursor.execute(query)
        return cursor.fetchone()
    
    def get_most_expectancy(self):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "SELECT COUNTRY, VALUE FROM life_expectancy_birth WHERE (SEX = 'Both sexes') ORDER BY VALUE DESC"
            cursor.execute(query)
        return cursor.fetchone()

    def get_least_expectancy(self):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "SELECT COUNTRY, VALUE FROM life_expectancy_birth WHERE (SEX = 'Both sexes') ORDER BY VALUE ASC"
            cursor.execute(query)
        return cursor.fetchone()

    def get_most_poverty(self):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "SELECT COUNTRY, VALUE FROM population_poverty ORDER BY VALUE DESC"
            cursor.execute(query)
        return cursor.fetchone()

    def get_least_poverty(self):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "SELECT COUNTRY, VALUE FROM population_poverty ORDER BY VALUE ASC"
            cursor.execute(query)
        return cursor.fetchone()

    def get_most_basic_drinking(self):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "SELECT COUNTRY, VALUE FROM water_services WHERE (RESIDENCE_AREA = 'All') ORDER BY VALUE DESC"
            cursor.execute(query)
        return cursor.fetchone()

    def get_least_basic_drinking(self):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "SELECT COUNTRY, VALUE FROM water_services WHERE (RESIDENCE_AREA = 'All') ORDER BY VALUE ASC"
            cursor.execute(query)
        return cursor.fetchone()

    def get_most_sanitation(self):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "SELECT COUNTRY, VALUE FROM sanitation_services WHERE (RESIDENCE_AREA = 'All') ORDER BY VALUE DESC"
            cursor.execute(query)
        return cursor.fetchone()

    def get_least_sanitation(self):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "SELECT COUNTRY, VALUE FROM sanitation_services WHERE (RESIDENCE_AREA = 'All') ORDER BY VALUE ASC"
            cursor.execute(query)
        return cursor.fetchone()

#Function to check if the user's age is in the given age group
def is_age_in_range(age, group):
    if "+" in group:
        #If the age group is given as "age+", check if the user's age is bigger
        return age >= int(group.replace("+", ""))
    #Otherwise, check if the age is within the limits
    limits = group.split("-")
    return age >= int(limits[0]) and age <= int(limits[1])

#Function to calculate the range of the age group
def range_width(group):
    limits = group.split("-")
    return int(limits[1]) - int(limits[0]) + 1