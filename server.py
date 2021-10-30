from flask import Flask, render_template, request, redirect
import sqlite3
from hashlib import sha256

app = Flask(__name__)

@app.route("/")
def home_page():
    return render_template("home.html")

@app.route("/statistics")
def stats_page():
    return render_template("statistics.html")

@app.route("/your-page")
def your_page():
    return render_template("yourPage.html", login = False)

@app.route("/form")
def form_page():
    values = {}
    return render_template("form.html", countries=get_countries(), values=values)

@app.route("/log_in")
def login_page():
    return render_template("login.html")


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
        return render_template("form.html", countries=get_countries(), values = values)
    else:
        valid = validate_registration(request.form)
        if not valid:
            return render_template("form.html", countries=get_countries(), values = request.form)
        user_first_name = request.form.data['first_name']
        user_last_name = request.form.data['last_name']
        user_gender = request.form.get('gender', '')
        user_country = request.form.data['country']
        user_birthday = request.form.data['birthday']
        user_email = request.form.data['email']
        user_password = request.form.data['password']
        hash1 = create_hash(user_password)
        add_user(user_first_name, user_last_name, user_gender, user_country, user_birthday, user_email, hash1)
        return render_template("yourPage.html", login = True, name = user_first_name)

@app.route("/handle_login", methods=['POST'])
def handle_login():
    user_email = request.form['email']
    user_password = request.form['password']
    hash_password = create_hash(user_password)
    hash2 = get_password(user_email)
    if hash2 == None:
        hash2 = ('',)
    if hash_password == hash2[0]:
        user_name = get_name(user_email)
        return render_template("yourPage.html", login = True, name = user_name[0])
    else:
        return render_template("login.html", error = True)


def create_connection():
    connection = sqlite3.connect("pythonsqlite.db")
    cursor = connection.cursor()
    return connection

def create_hash(password):
    pw_bytestring = password.encode()
    return sha256(pw_bytestring).hexdigest()

def add_user(first_name, last_name, gender, country, birthday, email, password_hash):
    conn = create_connection()
    cursor = conn.cursor()
    query = "INSERT INTO users (NAME, LAST_NAME, GENDER, COUNTRY, BIRTHDAY, EMAIL, PASSWORD) VALUES (?, ?, ?, ?, ?, ?, ?)"
    cursor.execute(query, (first_name, last_name, gender, country, birthday, email, password_hash))
    conn.commit()
    return cursor.lastrowid

def get_password(email):
    conn = create_connection()
    cursor = conn.cursor()
    query = "SELECT PASSWORD FROM users WHERE (EMAIL = ?)"
    cursor.execute(query, (email,))
    return cursor.fetchone()

def get_name(email):
    conn = create_connection()
    cursor = conn.cursor()
    query = "SELECT NAME FROM users WHERE (EMAIL = ?)"
    cursor.execute(query, (email,))
    return cursor.fetchone()

def get_countries():
    conn = create_connection()
    cursor = conn.cursor()
    query = "SELECT DISTINCT country FROM total_fertility"
    cursor.execute(query)
    return cursor.fetchall()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)