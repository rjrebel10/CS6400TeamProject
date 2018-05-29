from flask import Flask, flash, redirect, render_template, request, session, abort, url_for
import os
 
app = Flask(__name__)
 
@app.route('/', methods=['GET', 'POST'])
def home():
    return redirect(url_for('index'))

@app.route('/index', methods=['GET'])
def index(username=None):
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('index.html', username=session['username'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['password'] == 'password' and request.form['username'] == 'admin':
            session['logged_in'] = True
            session['username'] = request.form['username']
            return redirect(url_for('index'))
        else:
            flash('Invalid Credentials')
            return render_template('login.html')
    else:
        if not session.get('logged_in'):
            return render_template('login.html')
        else:
            return redirect(url_for('index'))

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session['logged_in'] = False
    session['username'] = None
    return render_template('loggedout.html')

if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True)