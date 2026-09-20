import os
import re
import sqlite3
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, g
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash
import helpers

# AI assistance disclosure: GitHub Copilot and Google Gemini were used to explain,
# review, and debug the common Flask patterns used here. This included the app
# setup, environment-variable handling, database connection/teardown, and
# Flask-Login user-loader flow. I reviewed and adjusted the final code to match
# the project requirements and requirements of this app.

app = Flask(__name__)

load_dotenv()
secret_key = os.environ.get("SECRET_KEY")

if not secret_key:
    # If the key is missing, crash the app immediately with error message
    raise ValueError("CRITICAL ERROR: SECRET_KEY is not defined in the environment.")

# Safely assign the verified key
app.secret_key = secret_key


# AI-assisted: Copilot helped confirm the standard Flask pattern for a per-request
# SQLite connection and teardown. I adapted the pattern to this project and kept
# the final database lifecycle logic consistent with the app's use of g and SQL.
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect("ozer.db")
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    attr = g.pop("db", None)  # Remove the 'db' attribute from g if it exists
    if attr is not None:
        attr.close()  # Close the database connection if it exists


# AI-assisted: Copilot was used to confirm the standard Flask-Login setup and
# user-loader pattern. I reviewed the final implementation and applied the user
# model and session flow to this app.
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
        return User(id=row["id"], username=row["username"])
    else:
        return None


# AI-assisted: Copilot suggested the overall registration flow and password
# validation structure, including redirect handling and pattern checks. I
# reviewed and adapted those choices to fit this project's requirements.
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if not username or not password:
            flash("Username and password are required.", "warning")
            return redirect(url_for("register"))

        db = get_db()
        # Check if the username is already taken
        existing_user = db.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        )
        if existing_user.fetchone() is not None:
            flash("Username already exists.", "warning")
            return redirect(url_for("register"))

        password_pattern = re.compile(
            r"(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z\d]).{8,}"
        )

        if not password_pattern.fullmatch(password):
            flash(
                "Password must be at least 8 characters and include at least one of each of the "
                + "following: uppercase letter, lowercase letter, number, and special character.",
                "error",
            )
            return redirect(url_for("register"))

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Insert the new user into the database
        db.execute(
            "INSERT INTO users (username, hash) VALUES (?, ?)",
            (username, hashed_password),
        )
        db.commit()

        flash("Registration Successful!", "success")
        return redirect(url_for("login"))

    else:
        return render_template("register.html")


# AI-assisted: Copilot helped confirm the password verification and session-login
# pattern used here. I adjusted the final logic to match the project's database
# schema and user model.
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if not username or not password:
            flash("Username and password are required.", "warning")
            return redirect(url_for("login"))

        db = get_db()
        # Check if the username and password match
        existing_user = db.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        )
        user = existing_user.fetchone()
        if user is None or not check_password_hash(user["hash"], password):
            flash("Invalid username or password.", "warning")
            return redirect(url_for("login"))

        else:
            # Create a User object and log the user in
            user_obj = User(id=user["id"], username=user["username"])
            login_user(user_obj)
            flash("Login Successful!", "success")
            return redirect(url_for("home"))

    else:
        return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route("/home", methods=["GET", "POST"])
@login_required
def home():
    return render_template("home.html", user=current_user)


@app.route("/", methods=["GET"])
def index():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    else:
        return render_template("index.html")


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    if request.method == "POST":
        THEMES = [
            "light", "dark", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
            "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
        ]
        theme = request.form.get("saved_theme")
        if not theme:
            flash("")
    else:
        return render_template("settings.html")