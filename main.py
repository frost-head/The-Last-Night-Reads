from flask import Flask, redirect, render_template, url_for
from datetime import datetime


# CONFIG
app = Flask(__name__)


# ROUTES
# HOME ROUTE
@app.route('/')
@app.route('/home/')
def ShowHome():
    return render_template('Home.html', route=['/', 'home'])

# LOGIN ROUTE


@app.route('/login/')
def login():
    return render_template('login.html', route=['login'])

# QUSTIONS ROUTE


@app.route('/questions/')
def showQuestions():
    return render_template('questions.html', route=['questions'])

# PROFILE ROUTE


@app.route('/profile/')
def showProfile():
    return render_template("profile.html", route=['profile'])

# REGISTER ROUTE


@app.route('/register/')
def register():
    return render_template("Register.html", route=['register'])

# ROUTES ENDED


if __name__ == "__main__":
    app.run(debug=True)
