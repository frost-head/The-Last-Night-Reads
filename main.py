from flask import Flask, redirect, render_template, url_for, flash, session,logging, request
from datetime import datetime, timedelta
from flask_mysqldb import MySQL
from wtforms import Form, TextField, PasswordField, validators, BooleanField, DateField,ValidationError
from passlib.hash import sha256_crypt

# CONFIG
app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'TonyStark@439751'
app.config['MYSQL_DB'] = 'LNR'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.secret_key = b'FD\x89\xeeM\x0cK\x953\x11\x11\xce\xab\xf2\x11\x16'
app.permanent_session_lifetime = timedelta(days=90)
 

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
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password_candidate = form.password.data

        cur = mysql.connection.cursor()
        cur.execute("select Uid,Password from user where UserName = %s",[username])
        data = cur.fetchone()
        cur.close()
        password = data['Password']
        uid = data["Uid"]

        if sha256_crypt.verify(password_candidate,password):
            session['UserID'] = uid
            return redirect(url_for('ShowHome'))

    return render_template('login.html',form=form, route=['login'])

# LOGOUT ROUTE

@app.route('/logout')
def logout():
    if 'UserID' in session:
        session.pop('UserID')
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
        return render_template("profile.html", UserData = data, route=['profile'], session=session)
    return render_template("profile.html",  route=['profile'], session=session)

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
        cur.execute("select Uid from user Where UserName = %s", [username])
        Uid = cur.fetchone()
        cur.close()
        session['UserID'] = Uid
        
        return redirect(url_for("showProfile"))
        

    return render_template("Register.html",form=form, route=['register'])

# ROUTES ENDED
# form classes

# Register Form
class RegistrationForm(Form):
    username = TextField('User Name', [validators.length(min = 1, max=100),validators.DataRequired()])
    name = TextField('Name', [validators.length(min = 4, max=35),validators.DataRequired()])
    age = DateField('Birth Date')
    email = TextField('Email Address', [validators.length(min=7,max=40),validators.DataRequired()])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.length(min=8),
        validators.EqualTo('Confirm', message='Passwords do not match.'),
    ])
    Confirm = PasswordField('Confirm Password')
    
    def validate_username(self, username):
        cur = mysql.connection.cursor()
        cur.execute("select UserName from user where UserName = %s", [username.data])
        user = cur.fetchone()
        cur.close()
        if user:
            raise ValidationError('That username is taken. Please choose another.')
    
#login Form
class LoginForm(Form):
    username = TextField("User Name",[validators.DataRequired()])
    password = PasswordField("Password",[validators.DataRequired()])


if __name__ == "__main__":
    app.run(debug=True)
