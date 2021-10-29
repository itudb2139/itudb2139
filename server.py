from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

@app.route("/")
def home_page():
    return render_template("home.html")

@app.route("/statistics")
def stats_page():
    return render_template("statistics.html")

@app.route("/your-page")
def your_page():
    return render_template("yourPage.html")

@app.route("/form")
def form_page():
    return render_template("form.html", countries=get_countries())

@app.route("/handle_data", methods=['POST'])
def handle_data():
    user_first_name = request.form['first_name']
    user_last_name = request.form['last_name']
    add_user(user_first_name, user_last_name)
    return redirect('/your-page')

def create_connection():
    connection = sqlite3.connect("pythonsqlite.db")
    cursor = connection.cursor()
    return connection

def add_user(first_name, last_name):
    conn = create_connection()
    cursor = conn.cursor()
    query = "INSERT INTO users (name, last_name) VALUES (?, ?)"
    cursor.execute(query, (first_name, last_name))
    conn.commit()
    return cursor.lastrowid

def get_countries():
    conn = create_connection()
    cursor = conn.cursor()
    query = "SELECT DISTINCT country FROM total_fertility"
    cursor.execute(query)
    return cursor.fetchall()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)