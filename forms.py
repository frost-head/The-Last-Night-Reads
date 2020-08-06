from wtforms import Form, TextAreaField, SelectField, TextField, PasswordField, validators, BooleanField, DateField,ValidationError
from main import mysql

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

# AskQuestion form
class AskQuestionForm(Form):
    # checking for standard data
    ls = []
    cur = mysql.connection.cursor()
    cur.execute("Select StdKey, StdName from standard")
    raw_std_data = cur.fetchall()
    for i in raw_std_data:
        j = (i['StdKey'],i['StdName'])
        ls.append(j)
    print(ls)

    question  = TextAreaField("Question",[validators.DataRequired()])
    standard = SelectField("Standard",choices=[("hello","mello")])