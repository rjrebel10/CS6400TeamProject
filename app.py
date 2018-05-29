from flask import Flask, flash, redirect, render_template, request, session, abort, url_for
from socket import gethostname
import os
 
# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'
 
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
    if 'liveconsole' not in gethostname():
        app.run()
