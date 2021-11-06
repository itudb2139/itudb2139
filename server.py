from flask import Flask, render_template, request, redirect
import sqlite3
import bcrypt
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from database import Database
import login
import datetime

app = Flask(__name__)

app.secret_key = "81b8316d99a3337cdf36791702a2a2e36296ffc0b531c2cd46ff1926abc1076c"

@app.route("/")
def home_page():
    return render_template("home.html", current_user=current_user)

@app.route("/statistics")
@login_required
def stats_page():
    country = current_user.data['country']
    fertility, = Database().get_fertility(country=country)
    return render_template("statistics.html", current_user=current_user, fertility=fertility)

@app.route("/your-page")
def your_page():
    age = 0
    if current_user.is_authenticated:
        age = calculate_age(current_user.data['birthday'])
    return render_template("yourPage.html", current_user=current_user, age=age)

@app.route("/form")
def form_page():
    values = {}
    return render_template("form.html", countries=Database().get_countries(), values=values, handler="handle_data")

@app.route("/log_in")
def login_page():
    return render_template("login.html")

@app.route("/edit")
def edit_page():
    return render_template("form.html", countries=Database().get_countries(), values=current_user.data, handler="handle_edit")

@app.route("/logout")
def log_out():
    logout_user()
    return render_template("yourPage.html", current_user=current_user)


def validate_registration(form):
    form.data = {}
    form.errors = {}

    form_name = form['first_name']
    if len(form_name) == 0:
        form.errors['first_name'] = "First name cannot be blank"
    else:
        form.data['first_name'] = form_name

    form_last_name = form['last_name']
    if len(form_last_name) == 0:
        form.errors['last_name'] = "Last name cannot be blank"
    else:
        form.data['last_name'] = form_last_name

    form_gender = form.get('gender', '')
    if len(form_gender) == 0:
        form.errors['gender'] = "Gender cannot be blank"
    else:
        form.data['gender'] = form_gender

    form.data['country'] = form['country']

    form_birthday = form['birthday']
    if len(form_birthday) == 0:
        form.errors['birthday'] = "Birthday cannot be blank"
    else:
        form.data['birthday'] = form_birthday

    form_email = form['email']
    if len(form_email) == 0:
        form.errors['email'] = "Email cannot be blank"
    else:
        form.data['email'] = form_email

    form_password = form['password']
    if len(form_password) == 0:
        form.errors['password'] = "Password cannot be blank"
    else:
        form.data['password'] = form_password
    
    return len(form.errors) == 0

    
@app.route("/handle_data", methods=['POST'])
def handle_data():
    if request.method == "GET":
        values = {'first_name':"", 'last_name':"", 'gender':"", 'country':"", 'birthday':"", 'email':"", 'password':""}
        return render_template("form.html", countries=Database().get_countries(), values = values, handler="handle_data")
    else:
        valid = validate_registration(request.form)
        if not valid:
            return render_template("form.html", countries=Database().get_countries(), values = request.form, handler="handle_data")
        user_first_name = request.form.data['first_name']
        user_last_name = request.form.data['last_name']
        user_gender = request.form.get('gender', '')
        user_country = request.form.data['country']
        user_birthday = request.form.data['birthday']
        user_email = request.form.data['email']
        user_password = request.form.data['password']
        hash1 = create_hash(user_password)
        new_id = Database().add_user(user_first_name, user_last_name, user_gender, user_country, user_birthday, user_email, hash1)
        login_user(login.load_user(new_id))
        user_age = calculate_age(user_birthday)
        return render_template("yourPage.html", current_user=current_user, age=user_age)


@app.route("/handle_login", methods=['POST'])
def handle_login():
    user_email = request.form['email']
    user_password = request.form['password']
    hash_pw = Database().get_password(user_email)
    if hash_pw == None:
        return render_template("login.html", error = True)

    if(check_password(user_password, hash_pw[0])):
        user_data = Database().get_user(user_email, parameter="EMAIL")
        user_id = user_data[0]
        login_user(login.load_user(user_id))
        user_age = calculate_age(current_user.data['birthday'])
        return render_template("yourPage.html", current_user=current_user, age=user_age)
    else:
        return render_template("login.html", error = True)

@app.route("/handle_edit", methods=['POST'])
def handle_edit():
    valid = validate_registration(request.form)
    if not valid:
        return render_template("form.html", countries=Database().get_countries(), values = request.form, handler="handle_edit")
    user_first_name = request.form.data['first_name']
    user_last_name = request.form.data['last_name']
    user_gender = request.form.get('gender', '')
    user_country = request.form.data['country']
    user_birthday = request.form.data['birthday']
    user_email = request.form.data['email']

    user_password = request.form.data['password']
    hash_pw = Database().get_password(current_user.data['email'])
    if (check_password(user_password, hash_pw[0])):
        Database().update_user(current_user.data['id'], user_first_name, user_last_name, user_gender, user_country, user_birthday, user_email)
        current_user.update_data()
        user_age = calculate_age(user_birthday)
        return render_template("yourPage.html", current_user=current_user, age=user_age)
    else:
        return render_template("form.html", countries=Database().get_countries(), values = request.form, handler="handle_edit", error = True)


def create_hash(password):
    pw_hash = bcrypt.hashpw(bytes(password, encoding="utf-8"), bcrypt.gensalt())
    return pw_hash

def check_password(password, pw_hash):
    return bcrypt.checkpw(bytes(password, encoding="utf-8"), pw_hash)

def calculate_age(birthday):
    today = datetime.date.today()
    birthday_obj = datetime.datetime.strptime(birthday, "%Y-%m-%d").date()
    this_year_bday = datetime.date(today.year, birthday_obj.month, birthday_obj.day)
    if this_year_bday < today:
        years = today.year - birthday_obj.year
    else:
        years = today.year - birthday_obj.year - 1
    return years

if __name__ == "__main__":
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.user_loader(login.load_user)
    login_manager.login_view = "login_page"
    app.run(host="0.0.0.0", port=8080, debug=True)