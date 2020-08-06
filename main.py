from flask import Flask, redirect, render_template, url_for, flash, session,logging, request
from datetime import datetime, timedelta
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt
from forms import *
import os

# CONFIG
app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'TonyStark@439751'
app.config['MYSQL_DB'] = 'LNR'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.secret_key = os.urandom(24)
app.permanent_session_lifetime = timedelta(days=30)


#intialising MySQL
mysql = MySQL()
mysql.init_app(app)

# ROUTES
# HOME ROUTE
@app.route('/')
@app.route('/home/')
def ShowHome():
    return render_template('Home.html', route=['/', 'home'])

# LOGIN ROUTE

@app.route('/login/', methods=['GET','POST'])
def login():
    form = LoginForm(request.form)

    if 'UserID' in session:
        return redirect(url_for('showProfile'))

    if request.method == 'POST' and form.validate():
        username = form.username.data
        password_candidate = form.password.data

        cur = mysql.connection.cursor()
        cur.execute("select Uid,Password from user where UserName = %s",[username])
        data = cur.fetchone()
        cur.close()
        if data:
            password = data['Password']
            uid = data["Uid"]

            if sha256_crypt.verify(password_candidate,password):
                session['UserID'] = uid
                flash('Successfully logged in', 'success')
                return redirect(url_for('showQuestions'))
            else:
                flash('Invalid Log In','danger')
        else:
            flash('User not Found','danger')
    return render_template('login.html',form=form, route=['login'])

# LOGOUT ROUTE

@app.route('/logout')
def logout():
    if 'UserID' in session:
        session.pop('UserID')
        flash('Logged Out', 'danger')
    return redirect(url_for('showProfile'))

# QUSTIONS ROUTE


@app.route('/questions/')
def showQuestions():
    return render_template('questions.html', route=['questions'])

# PROFILE ROUTE


@app.route('/profile/')
def showProfile():
    if "UserID" in session:
        cur = mysql.connection.cursor()
        cur.execute("select * from user where Uid = %s",[session['UserID']])
        data = cur.fetchone()
        cur.close()
        
        return render_template("profile.html", UserData = data, route=['profile'])
    return render_template("profile.html",  route=['profile'])

# REGISTER ROUTE


@app.route('/register/', methods=['GET','POST'])
def register():

    form = RegistrationForm(request.form)

    if 'UserID' in session:
        return redirect(url_for('showProfile'))

    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))
        name = form.name.data
        email = form.email.data
        age = form.age.data

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO user(UserName, Name, Email, Password, Age) VALUES(%s, %s, %s, %s, %s)",(username, name, email, password, age))
        mysql.connection.commit()
        
        cur.close()
        flash('You are successfully Registered', 'success')
        return redirect('/login')
        

    return render_template("Register.html",form=form, route=['register'])


# Ask Questions ROUTE 'UserID' in session
@app.route('/askQuestion', methods=['GET', 'POST'])
def askQuestion():
    if True:
        form = AskQuestionForm(request.form)
        StdData = []
        SubData = []
        cur = mysql.connection.cursor()
        
        #got Subject data
        cur.execute("Select StdKey, StdName from standard")
        raw_std_data = cur.fetchall()
        for i in raw_std_data:
            j = (i['StdKey'],i['StdName'])
            StdData.append(j)
        
        #got Standard data
        cur.execute("Select SubKey, SubName from subjects")
        raw_sub_data = cur.fetchall()
        for i in raw_sub_data:
            j = (i['SubKey'],i['SubName'])
            SubData.append(j) 
        
        form.standard.choices = StdData
        form.subject.choices = SubData


        if request.method == 'POST' and form.validate():
            Question = str(form.question.data)
            Standard = str(form.standard.data)
            Subject = str(form.subject.data)
            Uid = session['UserID']
            cur.execute("insert into Textual_Question(Uid, Question, standard, Subject) values(%s,%s,%s,%s)",(Uid,Question,Standard,Subject))
            mysql.connection.commit()
            cur.close()

    else:
        flash("Please login before asking question.",'danger')
        return redirect('/profile')
    return render_template('AskQuestions.html',form=form)


# ROUTES ENDED



if __name__ == "__main__":
    app.run(debug=True)
