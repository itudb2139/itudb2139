from flask import Flask, render_template, request, redirect
import sqlite3

from flask.helpers import url_for
import bcrypt
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from database import Database
import login
import datetime

app = Flask(__name__)

app.secret_key = "81b8316d99a3337cdf36791702a2a2e36296ffc0b531c2cd46ff1926abc1076c"

@app.route("/")
def home_page():

    return render_template("home.html", current_user=current_user, database=Database())

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

    #Form access
    form_data = Database().get_user_form(current_user.data['id'])
    personal_statistics = {'empty' : True}
    if(form_data != None):
        personal_statistics = {
            "siblings": form_data[0],
            "average_age": form_data[1],
            "education": form_data[2],
            "tobacco": form_data[3],
            "alcohol": form_data[4],
            "exercise": form_data[5]
        }
    
    causes_data = Database().get_user_causes(current_user.data['id'])

    #Form assessment
    if(form_data != None):
        accurate = 0

        sib_difference = abs(personal_statistics['siblings'] - fertility)
        if(sib_difference < 1):
            accurate = accurate + 1

        if personal_statistics['average_age'] <= life_expectancy_birth:
            accurate = accurate + 1

        if(current_user.age > 15 and current_user.age < 24):
            if education != None:
                if(education <= 50 and personal_statistics['education'] == "No"):
                    accurate = accurate + 1
                elif(education > 50 and personal_statistics['education'] == "Yes"):
                    accurate = accurate + 1
        else:
            accurate = accurate + 1
        
        if Database().is_applicable(current_user.age, "tobacco_use"):
            if tobacco_use != None:
                if(tobacco_use <= 50 and personal_statistics['tobacco'] == "No"):
                    accurate = accurate + 1
                elif(tobacco_use > 50 and personal_statistics['tobacco'] == "Yes"):
                    accurate = accurate + 1
        else:
            accurate = accurate + 1

        if(current_user.age > 15 and current_user.age < 19):
            if drinking != None:
                if(drinking <= 50 and personal_statistics['alcohol'] == "No"):
                    accurate = accurate + 1
                elif(drinking > 50 and personal_statistics['alcohol'] == "Yes"):
                    accurate = accurate + 1
        else:
            accurate = accurate + 1

        if(current_user.age >= 11 and current_user.age <= 17):
            if physical_activity != None:
                if(physical_activity <= 50 and personal_statistics['exercise'] == "No"):
                    accurate = accurate + 1
                elif(physical_activity > 50 and personal_statistics['exercise'] == "Yes"):
                    accurate = accurate + 1
        else:
            accurate = accurate + 1
        
        if causes_data:
            accurate = accurate + 1

        #Calculate accuracy
        accuracy = (accurate / 7) * 100 
    else:
        accuracy = 0

    has_review = Database().get_review(current_user.data['id'])   
    
    return render_template("statistics.html", current_user=current_user, fertility=fertility, is_applicable = Database().is_applicable, 
    tobacco_use=tobacco_use, tuberculosis=tuberculosis_rate, hepb = hepb, education=education, poverty=poverty, 
    life_expectancy_birth=life_expectancy_birth, life_expectancy_old=life_expectancy_old, physical_activity=physical_activity, drinking=drinking, 
    sanitation=sanitation, water=water, adolescent_mortality=adolescent_mortality, adolescent_mortality_cause=adolescent_mortality_cause,
    personal_statistics = personal_statistics, causes_data=causes_data, accuracy=accuracy, has_review=has_review)

@app.route("/your-page")
@login_required
def your_page():
    return render_template("yourPage.html", current_user=current_user)

@app.route("/form")
def form_page():
    values = {}
    #get_countries function is called in order to get the country options for the registration form
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
    return redirect(url_for("home_page"))

@app.route("/no_account")
def no_account_page():
    return render_template("no_account.html")

@app.route("/statistics_form")
def statistics_form():
    values = {}
    #If the query below returns None, then this data is not available for this user's country
    causes=Database().get_mortality_causes_form(current_user.data['country'], current_user.data['gender'])
        
    return render_template("statistics_form.html", values=values, causes=causes, handler="handle_statistics_form")

@app.route("/statistics_edit")
def statistics_edit_page():
    causes = {}
    #If the query below returns None, then this data is not available for this user's country
    causes=Database().get_mortality_causes_form(current_user.data['country'], current_user.data['gender'])
    
    form_data = Database().get_user_form(current_user.data['id'])
    if(form_data != None):
        personal_statistics = {
            "siblings": form_data[0],
            "average_age": form_data[1],
            "education": form_data[2],
            "tobacco": form_data[3],
            "drinking": form_data[4]
        }

    return render_template("statistics_form.html", values=personal_statistics, causes=causes, handler="handle_statistics_edit")

@app.route("/review_form")
def review_form():
    values = {}
    return render_template("review_form.html", values=values, handler="handle_review_form")

@app.route("/review_edit")
def review_edit():
    review_data = Database().get_review(current_user.data['id'])
    if(review_data != None):
        user_review = {
            "experience": review_data[0],
            "recommend": review_data[1],
            "accuracy": review_data[2],
            "more_statistics": review_data[3],
            "comments": review_data[4]
        }

    return render_template("review_form.html", values=user_review, handler="handle_review_edit")

@app.route("/delete_form")
def delete_form():
    Database().delete_form(current_user.data['id'])
    return redirect(url_for('stats_page'))

@app.route("/delete_user")
def delete_user():
    id = current_user.data['id']
    logout_user()
    Database().delete_user(id)
    return render_template("home.html", current_user=current_user)

@app.route("/delete_review")
def delete_review():
    Database().delete_review(current_user.data['id'])
    return redirect(url_for('stats_page'))

def validate_registration(form):
    #Creating 2 dictionaries for errors and data
    form.data = {}
    form.errors = {}

    #If any of the required field are blank, an error message is added to the errors dictionary
    form_name = form['first_name']
    if len(form_name) == 0:
        form.errors['first_name'] = "First name cannot be blank"
    else:
        #Otherwise, the entered data is added to the data dictionary 
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
        if Database().does_email_exist(form_email):
            form.errors['email'] = "This email is already registered"
        else:
            form.data['email'] = form_email

    form_password = form['password']
    if len(form_password) == 0:
        form.errors['password'] = "Password cannot be blank"
    else:
        form.data['password'] = form_password
    
    #The function returns true if the errors dictionary is empty (i.e. when all the required fields are filled)
    return len(form.errors) == 0

    
@app.route("/handle_data", methods=['POST'])
def handle_data():
    if request.method == "GET":
        values = {'first_name':"", 'last_name':"", 'gender':"", 'country':"", 'birthday':"", 'email':"", 'password':""}
        return render_template("form.html", countries=Database().get_countries(), values = values, handler="handle_data")
    else:
        #If the user left some required fields blank, the form will not be validated
        valid = validate_registration(request.form)
        if not valid:
            #Error messages will be printed and the previously entered values will be autofilled (from values dictionary)
            return render_template("form.html", countries=Database().get_countries(), values = request.form, handler="handle_data")
        #If the form is validated, the entered values are assigned to the variables
        user_first_name = request.form.data['first_name']
        user_last_name = request.form.data['last_name']
        user_gender = request.form.get('gender', '')
        user_country = request.form.data['country']
        user_birthday = request.form.data['birthday']
        user_email = request.form.data['email']
        user_password = request.form.data['password']
        #The password that the user entered is turned into hash
        hash1 = create_hash(user_password)
        #The new user is created and added to the users table in the database
        #The function returns the id of the last added row
        new_id = Database().add_user(user_first_name, user_last_name, user_gender, user_country, user_birthday, user_email, hash1)
        #Using the user id of the newly created user, login function is called
        login_user(login.load_user(new_id))
        return render_template("yourPage.html", current_user=current_user)


@app.route("/handle_login", methods=['POST'])
def handle_login():
    user_email = request.form['email']
    user_password = request.form['password']
    hash_pw = Database().get_password(user_email)
    if hash_pw == None:
        #If the function get_password did not find a user the with that email, an error message is shown
        return render_template("login.html", error = True)

    #Otherwise, if the entered password matches the password of the registered user
    if(check_password(user_password, hash_pw[0])):
        #Get user data of the user with the entered email
        #Parameter is the condition parameter to find the user, in this case, find by email
        user_data = Database().get_user(user_email, parameter="EMAIL")
        #Getting user id from the found user
        user_id = user_data[0]
        #Calling the login function with the found user id
        login_user(login.load_user(user_id))
        return render_template("yourPage.html", current_user=current_user)
    else:
        #If the passwords don't match, an error message is printed
        return render_template("login.html", error = True)

@app.route("/handle_edit", methods=['POST'])
def handle_edit():
    #The edit form works in a similar way to the registration form. Thus, the same validation function is used.
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
    #Getting the password (hash) of the current user (using the email)
    hash_pw = Database().get_password(current_user.data['email'])
    if (check_password(user_password, hash_pw[0])):
        #If the passwords match, update user function is called with the new parameters
        Database().update_user(current_user.data['id'], user_first_name, user_last_name, user_gender, user_country, user_birthday, user_email)
        #Calling update data function on the current user
        current_user.update_data()
        #Redirecting to yourPage
        return render_template("yourPage.html", current_user=current_user)
    else:
        #If the passwords don't match, an error message will be printed and the values will be autofilled
        return render_template("form.html", countries=Database().get_countries(), values = request.form, handler="handle_edit")

def validate_statistics_form(form):
    #This function works in the same way as "validate_registration" function
    #Required fields need to be filled or an error message will be added to the errors dictionary
    #Otherwise, the entered data will be added to the data dictionary
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

    form_exercise = form.get('exercise', '')
    if len(form_exercise) == 0:
        form.errors['exercise'] = "This field cannot be blank"
    else:
        form.data['exercise'] = form_exercise

    #The function returns true if there were no errors (all the required fields were filled)
    return len(form.errors) == 0

@app.route("/handle_statistics_form", methods=['POST'])
def handle_statistics_form():
    valid = validate_statistics_form(request.form)
    if not valid:
        #If some of the required fields were not filled, error messages are printed and the form is loaded again
        causes=Database().get_mortality_causes_form(current_user.data['country'], current_user.data['gender'])
        return render_template("statistics_form.html", values=request.form, causes=causes, handler="handle_statistics_form")

    sibling_number = request.form.data['siblings']

    grandparent1 = int(request.form.data['grandparent1'])
    #The count variable is used to keep track of how many grandparents' ages were entered
    count = 1
    #The first grandparent has to be entered, the remaining ones are initialized with 0
    grandparent2 = grandparent3 = grandparent4 = 0
    if 'grandparent2' in request.form.data:
        #If the second grandparent is entered, the value is cast into an integer and the count variable is incremented
        grandparent2 = int(request.form.data['grandparent2'])
        count += 1
    if 'grandparent3' in request.form.data:
        #The logic above applies to the remaining grandparents
        grandparent3 = int(request.form.data['grandparent3'])
        count += 1
    if 'grandparent4' in request.form.data:
        grandparent4 = int(request.form.data['grandparent4'])
        count += 1
    #Ater all the values are received, the average between the ages is found, using the count variable
    gp_age = (grandparent1 + grandparent2 + grandparent3 + grandparent4) / count

    is_education = request.form.data['education']
    is_tobacco = request.form.data['tobacco']
    is_alcohol = request.form.data['drinking']
    is_exercise = request.form.data['exercise']

    #In order to access the entered checkbox data, a dictionary is created
    form_causes = dict(request.form.lists()).get('cause', [])
    #If any were selected, the causes will be added to the mortality_causes table one by one with the current user id
    for cause in form_causes:
        Database().add_causes(current_user.data['id'], cause)
    #The rest of the entered information will be added to the form table with the current user id
    Database().add_form(sibling_number, gp_age, is_education, is_tobacco, is_alcohol, is_exercise, current_user.data['id'])
    #After the form is submitted, the user will be redirected back to the statistis page
    return redirect(url_for('stats_page'))

@app.route("/handle_statistics_edit", methods=['POST'])
def handle_statistics_edit():
    #The edit form works in a similar way to the original form. Thus, the same validation function is used.
    valid = validate_statistics_form(request.form)
    if not valid:
        causes=Database().get_mortality_causes_form(current_user.data['country'], current_user.data['gender'])
        return render_template("statistics_form.html", values=request.form, causes=causes, handler="handle_statistics_edit")

    sibling_number = request.form.data['siblings']

    grandparent1 = int(request.form.data['grandparent1'])
    #The count variable is used to keep track of how many grandparents' ages were entered
    count = 1
    #The first grandparent has to be entered, the remaining ones are initialized with 0
    grandparent2 = grandparent3 = grandparent4 = 0
    if 'grandparent2' in request.form.data:
        #If the second grandparent is entered, the value is cast into an integer and the count variable is incremented
        grandparent2 = int(request.form.data['grandparent2'])
        count += 1
    if 'grandparent3' in request.form.data:
        #The logic above applies to the remaining grandparents
        grandparent3 = int(request.form.data['grandparent3'])
        count += 1
    if 'grandparent4' in request.form.data:
        grandparent4 = int(request.form.data['grandparent4'])
        count += 1
    #Ater all the values are received, the average between the ages is found, using the count variable
    gp_age = (grandparent1 + grandparent2 + grandparent3 + grandparent4) / count

    is_education = request.form.data['education']
    is_tobacco = request.form.data['tobacco']
    is_alcohol = request.form.data['drinking']
    is_exercise = request.form.data['exercise']

    #In order to access the entered checkbox data, a dictionary is created
    form_causes = dict(request.form.lists()).get('cause', [])
    Database().update_causes(current_user.data['id'], form_causes)
    #The rest of the entered information will be added to the form table with the current user id
    Database().update_form(sibling_number, gp_age, is_education, is_tobacco, is_alcohol, is_exercise, current_user.data['id'])
    #After the form is submitted, the user will be redirected back to the statistis page
    return redirect(url_for('stats_page'))

def validate_review(form):
    #Creating 2 dictionaries for errors and data
    form.data = {}
    form.errors = {}
        
    form_experience = form.get('experience', '')
    if len(form_experience) == 0:
        form.errors['experience'] = "This field cannot be blank"
    else:
        form.data['experience'] = form_experience

    form_recommend= form.get('recommend', '')
    if len(form_recommend) == 0:
        form.errors['recommend'] = "This field cannot be blank"
    else:
        form.data['recommend'] = form_recommend

    form_accuracy = form.get('accuracy', '')
    if len(form_accuracy) == 0:
        form.errors['accuracy'] = "This field cannot be blank"
    else:
        form.data['accuracy'] = form_accuracy

    form_morestats = form['morestats']
    if len(form_morestats) == 0:
        form.errors['morestats'] = "This field cannot be blank"
    else:
        form.data['morestats'] = form_morestats

    form_comments = form['comments']
    if len(form_comments) == 0:
        form.errors['comments'] = "This field cannot be blank"
    else:
        form.data['comments'] = form_comments

    #The function returns true if there were no errors (all the required fields were filled)
    return len(form.errors) == 0
    

@app.route("/handle_review_form", methods=['POST'])
def handle_review_form():
    valid = validate_review(request.form)
    if not valid:
        #If some of the required fields were not filled, error messages are printed and the form is loaded again
        return render_template("review_form.html", values=request.form, handler="handle_review_form")

    form_experience = request.form.data['experience']
    form_recommend = request.form.data['recommend']
    form_accuracy = request.form.data['accuracy']
    form_more_statistics = request.form.data['morestats']
    form_comments = request.form.data['comments']

    today = datetime.date.today()
    today_string = today.strftime("%d%m%Y")

    Database().add_review(form_experience, form_recommend, form_accuracy, form_more_statistics, form_comments, today_string, current_user.data['id'])
    #After the form is submitted, the user will be redirected back to the statistis page
    return redirect(url_for('stats_page'))

@app.route("/handle_review_edit", methods=['POST'])
def handle_review_edit():
    valid = validate_review(request.form)
    if not valid:
        return render_template("review_form.html", values=request.form, handler="handle_review_edit")
    
    form_experience = request.form.data['experience']
    form_recommend = request.form.data['recommend']
    form_accuracy = request.form.data['accuracy']
    form_more_statistics = request.form.data['morestats']
    form_comments = request.form.data['comments']

    today = datetime.date.today()
    today_string = today.strftime("%d%m%Y")

    Database().update_review(form_experience, form_recommend, form_accuracy, form_more_statistics, form_comments, today_string, current_user.data['id'])
    return redirect(url_for('stats_page'))

#Function to create hash for the password
def create_hash(password):
    pw_hash = bcrypt.hashpw(bytes(password, encoding="utf-8"), bcrypt.gensalt())
    return pw_hash

#Function to compare the password with the hash
def check_password(password, pw_hash):
    return bcrypt.checkpw(bytes(password, encoding="utf-8"), pw_hash)


if __name__ == "__main__":
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.user_loader(login.load_user)
    login_manager.login_view = "no_account_page"
    app.run(host="0.0.0.0", port=8080, debug=True)