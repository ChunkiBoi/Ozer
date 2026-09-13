import os
import sqlite3
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, g
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import helpers


app = Flask(__name__)

load_dotenv()
secret_key = os.environ.get("SECRET_KEY")

if not secret_key:
    # If the key is missing, crash the app immediately with error message
    raise ValueError("CRITICAL ERROR: SECRET_KEY is not defined in the environment.")

# Safely assign the verified key
app.secret_key = secret_key

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('ozer.db')
        g.db.row_factory = sqlite3.Row
        g.db.execute('PRAGMA foreign_keys = ON')
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    attr = g.pop('db', None)  # Remove the 'db' attribute from g if it exists
    if attr is not None:
        attr.close()  # Close the database connection if it exists

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username


@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    # Query the 'users' table to find the row where id matches user_id
    id_match = db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = id_match.fetchone()
    if row is not None:
        return User(id=row['id'], username=row['username'])
    else:
        return None


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            flash("Username and password are required.")
            return redirect(url_for('register'))

        db = get_db()
        # Check if the username is already taken
        existing_user = db.execute("SELECT * FROM users WHERE username = ?", (username,))
        if existing_user.fetchone() is not None:
            flash('Username already exists.')
            return redirect(url_for('register'))

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Insert the new user into the database
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (username, hashed_password))
        db.commit()

        flash('Registration Successful!')
        return redirect(url_for('login'))

    else:
        return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')