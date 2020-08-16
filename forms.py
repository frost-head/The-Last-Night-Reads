from wtforms import *
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
    remember_me = BooleanField("Remember Me")

# AskQuestion form
class AskQuestionForm(Form):
    # checking for standard data
    question  = TextAreaField("Question")
    standard = SelectField("Standard",validate_choice=False)
    subject = SelectField("Subject",validate_choice=False)

class AnswerForm(Form):
    answer = TextAreaField("Answer",[validators.DataRequired()])