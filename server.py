from flask import Flask, render_template, request, redirect
import sqlite3

from flask.helpers import url_for
import bcrypt
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from database import Database
import login

app = Flask(__name__)

app.secret_key = "81b8316d99a3337cdf36791702a2a2e36296ffc0b531c2cd46ff1926abc1076c"

@app.route("/")
def home_page():
    return render_template("home.html", current_user=current_user)

@app.route("/statistics")
@login_required
def stats_page():
    country = current_user.data['country']
    gender = current_user.data['gender']

    #Getting data based on the user's country, age and gender from the respective tables
    fertility, = Database().get_fertility(country=country)

    tobacco_use = Database().get_tobacco_use(country=country, sex=gender)

    tuberculosis_rate = Database().get_tuberculosis(country=country, sex=gender, age=current_user.age)

    hepb = Database().get_hepb(country=country, sex=gender, age=current_user.age)

    education = Database().get_education(country=country, sex=gender)

    poverty = Database().get_poverty(country=country)

    life_expectancy_birth = Database().get_life_expectancy_birth(country=country, sex=gender)

    life_expectancy_old = Database().get_life_expectancy_60(country=country, sex=gender)

    physical_activity = Database().get_physical_activity(country=country, sex=gender)

    drinking = Database().get_drinking(country=country, sex=gender)

    sanitation = Database().get_sanitation_services(country=country)

    water = Database().get_water_services(country=country)

    adolescent_mortality = Database().get_adolescent_mortality(country=country, sex=gender, age=current_user.age)

    adolescent_mortality_cause = Database().get_mortality_causes(country=country, sex=gender, age=current_user.age)

    return render_template("statistics.html", current_user=current_user, fertility=fertility, is_applicable = Database().is_applicable, 
    tobacco_use=tobacco_use, tuberculosis=tuberculosis_rate, hepb = hepb, education=education, poverty=poverty, 
    life_expectancy_birth=life_expectancy_birth, life_expectancy_old=life_expectancy_old, physical_activity=physical_activity, drinking=drinking, 
    sanitation=sanitation, water=water, adolescent_mortality=adolescent_mortality, adolescent_mortality_cause=adolescent_mortality_cause)

@app.route("/your-page")
@login_required
def your_page():
    return render_template("yourPage.html", current_user=current_user)

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
    return render_template("home.html", current_user=current_user)

@app.route("/no_account")
def no_account_page():
    return render_template("no_account.html")

@app.route("/statistics_form")
def statistics_form():
    values = {}
    causes = {}
    #If the query below returns None, then this data is not available for this user's country
    adolescent_mortality_cause = Database().get_mortality_causes(country=current_user.data['country'], sex=current_user.data['gender'], age=current_user.age)
    #The form is going to have this field only if the data for mortality causes is available for this user
    if(adolescent_mortality_cause != None):
        causes=Database().get_mortality_causes_form(current_user.data['country'], current_user.data['gender'])
    return render_template("statistics_form.html", values=values, causes=causes, adolescent_mortality_cause=adolescent_mortality_cause)


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
        return render_template("yourPage.html", current_user=current_user)


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
        return render_template("yourPage.html", current_user=current_user)
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
        return render_template("yourPage.html", current_user=current_user)
    else:
        return render_template("form.html", countries=Database().get_countries(), values = request.form, handler="handle_edit")

def validate_statistics_form(form):
    form.data = {}
    form.errors = {}

    form_siblings = form['siblings']
    if len(form_siblings) == 0:
        form.errors['siblings'] = "Number of siblings cannot be blank"
    else:
        form.data['siblings'] = form_siblings

    form_grandparent1 = form['grandparent1']
    if len(form_grandparent1) == 0:
        form.errors['grandparent1'] = "At least one grandparent's age should be entered."
    else:
        form.data['grandparent1'] = form_grandparent1

    form_grandparent2 = form['grandparent2']
    if len(form_grandparent2) != 0:
        form.data['grandparent2'] = form_grandparent2

    form_grandparent3 = form['grandparent3']
    if len(form_grandparent3) != 0:
        form.data['grandparent3'] = form_grandparent3
    
    form_grandparent4 = form['grandparent4']
    if len(form_grandparent4) != 0:
        form.data['grandparent4'] = form_grandparent4
        
    form_education = form.get('education', '')
    if len(form_education) == 0:
        form.errors['education'] = "This field cannot be blank"
    else:
        form.data['education'] = form_education

    form_tobacco = form.get('tobacco', '')
    if len(form_tobacco) == 0:
        form.errors['tobacco'] = "This field cannot be blank"
    else:
        form.data['tobacco'] = form_tobacco

    form_drinking = form.get('drinking', '')
    if len(form_drinking) == 0:
        form.errors['drinking'] = "This field cannot be blank"
    else:
        form.data['drinking'] = form_drinking

    return len(form.errors) == 0

@app.route("/handle_statistics_form", methods=['POST'])
def handle_statistics_form():
    valid = validate_statistics_form(request.form)
    if not valid:
        adolescent_mortality_cause = Database().get_mortality_causes(country=current_user.data['country'], sex=current_user.data['gender'], age=current_user.age)
        causes = {}
        if(adolescent_mortality_cause != None):
            causes=Database().get_mortality_causes_form(current_user.data['country'], current_user.data['gender'])
        return render_template("statistics_form.html", causes=causes, adolescent_mortality_cause=adolescent_mortality_cause)

    sibling_number = request.form.data['siblings']

    grandparent1 = int(request.form.data['grandparent1'])
    count = 1
    grandparent2 = grandparent3 = grandparent4 = 0
    if 'grandparent2' in request.form.data:
        grandparent2 = int(request.form.data['grandparent2'])
        count += 1
    if 'grandparent3' in request.form.data:
        grandparent3 = int(request.form.data['grandparent3'])
        count += 1
    if 'grandparent4' in request.form.data:
        grandparent4 = int(request.form.data['grandparent4'])
        count += 1
    gp_age = (grandparent1 + grandparent2 + grandparent3 + grandparent4) / count

    is_education = request.form.data['education']
    is_tobacco = request.form.data['tobacco']
    is_alcohol = request.form.data['drinking']

    form_causes = dict(request.form.lists()).get('cause', [])
    for cause in form_causes:
        Database().add_causes(current_user.data['id'], cause)
    
    Database().add_form(sibling_number, gp_age, is_education, is_tobacco, is_alcohol, current_user.data['id'])

    return redirect(url_for('stats_page'))

def create_hash(password):
    pw_hash = bcrypt.hashpw(bytes(password, encoding="utf-8"), bcrypt.gensalt())
    return pw_hash

def check_password(password, pw_hash):
    return bcrypt.checkpw(bytes(password, encoding="utf-8"), pw_hash)


if __name__ == "__main__":
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.user_loader(login.load_user)
    login_manager.login_view = "no_account_page"
    app.run(host="0.0.0.0", port=8080, debug=True)