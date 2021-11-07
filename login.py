from database import Database
import datetime

class user_login:
    def __init__(self, data) -> None:
        if data == None:
            self.data = None
        else:
            self.data = {
                "id": data[0],
                "first_name": data[1],
                "last_name": data[2],
                "gender": data[3],
                "country": data[4],
                "birthday": data[5],
                "email": data[6]
            }

    @property
    def is_authenticated(self):
        return self.data != None

    @property
    def is_active(self):
        return True
    
    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.data['id']

    def update_data(self):
        data = Database().get_user(self.data['id'],"ID")
        self.data = {
                "id": data[0],
                "first_name": data[1],
                "last_name": data[2],
                "gender": data[3],
                "country": data[4],
                "birthday": data[5],
                "email": data[6]
            }

    @property
    def age(self):
        today = datetime.date.today()
        birthday_obj = datetime.datetime.strptime(self.data['birthday'], "%Y-%m-%d").date()
        this_year_bday = datetime.date(today.year, birthday_obj.month, birthday_obj.day)
        if this_year_bday < today:
            years = today.year - birthday_obj.year
        else:
            years = today.year - birthday_obj.year - 1
        return years

def load_user(user_id):
    return user_login(Database().get_user(user_id,"ID"))