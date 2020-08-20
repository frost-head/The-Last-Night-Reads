from wtforms import *
from main import mysql

# form classes

# Register Form
class RegistrationForm(Form):
    username = TextField('User Name', [validators.length(min = 1, max=100),validators.DataRequired()],description="Please enter a unique Username")
    name = TextField('Name', [validators.length(min = 4, max=35),validators.DataRequired()],description="Please enter Your full Name")
    age = DateField('Birth Date',description="Please enter your DOB in YYYY-MM-DD format")

    email = TextField('Email Address', [validators.length(min=7,max=40),validators.DataRequired()], description="Please enter your Email address")
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.length(min=8),
        validators.EqualTo('Confirm', message='Passwords do not match.'),
    ], description="Password must contain 8 characters.")
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
    username = TextField("User Name",[validators.DataRequired()], description="Please enter your unique Username")
    password = PasswordField("Password",[validators.DataRequired()], description='Enter your Password')
    remember_me = BooleanField("Remember Me",widget=widgets.CheckboxInput(), description='If you check this you will remain logged in for a span of 30 days on thsi browser')

# AskQuestion form
class AskQuestionForm(Form):
    # checking for standard data
    question  = TextAreaField("Question",[validators.DataRequired()],description="Type your Question in the following feild")
    standard = SelectField("Standard",validate_choice=False,description="Select the Standard of Question")
    subject = SelectField("Subject",validate_choice=False,description="Select the Subject of Question")

class AnswerForm(Form):
    answer = TextAreaField("Answer",[validators.DataRequired()],description="Type your Answer in the following field")

class SearchForm(Form):
    search = TextAreaField('Search', [validators.DataRequired()], description="Type your Question in the following field. Recomended to type tags like 'projectile'")
