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
                if form.remember_me.data == True:
                    session.permanent = True
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
    cur = mysql.connection.cursor()
    cur.execute("""Select Qid, Username, Question, StdName, SubName, PostDate, AnsCount from user
    inner join Textual_Question, subjects, standard where 
    user.Uid = Textual_Question.Uid and
    Textual_Question.Subject = subjects.Subkey and
    Textual_Question.standard = standard.StdKey
    ORDER BY PostDate desc
    """)
    q_data = cur.fetchall()


    cur.close()
    return render_template('questions.html', route=['questions'],Question_data=q_data)

# PROFILE ROUTE


@app.route('/profile/', methods=['GET','POST'])
def showProfile():
    if "UserID" in session:
        cur = mysql.connection.cursor()
        
        cur.execute("select * from user where Uid = %s",[session['UserID']])
        u_data = cur.fetchone()
        
        cur.execute("""Select Qid, Username, Question, StdName, SubName, PostDate, AnsCount from Textual_Question
        inner join user, subjects, standard where 
        Textual_Question.Uid = {} and
        user.Uid = {} and
        Textual_Question.Subject = subjects.Subkey and
        Textual_Question.standard = standard.StdKey
        ORDER BY PostDate desc
        """.format(int(session['UserID']),int(session['UserID'])))
        q_data = cur.fetchall()
        
        cur.execute("""
        Select Textual_Question.Qid, Textual_Question.PostDate, AnsCount, Username, Question, StdName, SubName from Textual_Question
        inner join user, subjects, standard,Textual_Answers where 
        Textual_Answers.Uid = {} and
        Textual_Question.Qid = Textual_Answers.Qid and
        user.Uid = Textual_Question.Uid and
        Textual_Question.Subject = subjects.Subkey and
        Textual_Question.standard = standard.StdKey
        """.format(int(session['UserID'])))
        a_data = cur.fetchall()
        
        cur.close()
        
        return render_template("profile.html", UserData = u_data,Question_data=q_data,Answer_data=a_data, route=['profile'])
    else:
        return redirect('/login')
    
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


# Ask Questions ROUTE 
@app.route('/askQuestion', methods=['GET', 'POST'])
def askQuestion():
    if 'UserID' in session:
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
            flash("successfully asked",'success')
            return redirect(url_for('showQuestions'))
    else:
        flash("Please login before asking question.",'danger')
        return redirect('/profile')
    return render_template('AskQuestions.html',form=form)

@app.route('/answer/<Qid>', methods=['GET','POST'])
def answer(Qid):
    form = AnswerForm(request.form)
    if 'UserID' in session:

        cur = mysql.connection.cursor()
        cur.execute("""Select Qid, Username, Question, StdName, SubName, PostDate, AnsCount from user
        inner join Textual_Question, subjects, standard where 
        Textual_Question.Qid = {} and
        user.Uid = Textual_Question.Uid and
        Textual_Question.Subject = subjects.Subkey and
        Textual_Question.standard = standard.StdKey""".format(Qid))
        
        q_data = cur.fetchone()

        cur.execute("""
        select Username, Answer,PostDate from user
        inner join Textual_Answers 
        where user.Uid = Textual_Answers.Uid and 
        Textual_Answers.Qid = {} 
        """.format(Qid))

        a_data = cur.fetchall()

        cur.close()
        if request.method == 'POST':
            answer = str(form.answer.data)
            cur = mysql.connection.cursor()
            cur.execute("""
            insert into Textual_Answers(Qid, Uid ,Answer)values(%s,%s,%s)
            """,(Qid, session['UserID'], answer))
            Anscount = int(q_data['AnsCount']) + 1
            cur.execute("""
            UPDATE Textual_Question SET AnsCount = {} WHERE Textual_Question.Qid = {}
            """.format(Anscount, Qid))
            mysql.connection.commit()
            cur.close()
            return redirect('/answer/{}'.format(Qid))

        return render_template('Answer.html',q_data=q_data,a_data=a_data,form=form)
    else:
        flash("Please loggin before answering", 'danger')
        return redirect(url_for('showProfile'))

# Indiviusdal Question route
@app.route('/question/<Qid>', methods=['GET','POST'])
def question(Qid):
    cur = mysql.connection.cursor()
    cur.execute("""Select Qid, Username, Question, StdName, SubName, PostDate, AnsCount from user
    inner join Textual_Question, subjects, standard where 
    Textual_Question.Qid = {} and
    user.Uid = Textual_Question.Uid and
    Textual_Question.Subject = subjects.Subkey and
    Textual_Question.standard = standard.StdKey
    
    """.format(Qid))
    
    q_data = cur.fetchone()

    cur.execute("""
    select Username, Answer,PostDate from user
    inner join Textual_Answers 
    where user.Uid = Textual_Answers.Uid and 
    Textual_Answers.Qid = {}
    """.format(Qid))

    a_data = cur.fetchall()

    cur.close()
    return render_template('indivisual_question.html',q_data=q_data,a_data=a_data)
    

# ROUTES ENDED


if __name__ == "__main__":
    app.run(debug=True,host= '0.0.0.0')
