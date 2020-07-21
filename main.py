from flask import Flask , redirect, render_template
app = Flask(__name__)

@app.route('/')
def r():
    redirect('/home')

@app.route('/home')
def ShowHome():
    return render_template('Home.html')


if __name__ == "__main__":
    app.run(debug = True)