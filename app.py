import os
import re
import sqlite3
from dotenv import load_dotenv
from flask import (
    Flask, 
    jsonify,
    render_template, 
    request, 
    redirect, 
    url_for, 
    flash, 
    g, 
    Response
    )
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
from helpers import (
    GroqHandler,
    groq_client,
    save_chat,
    get_sys_prompt
)

# AI assistance disclosure: GitHub Copilot and Google Gemini were used to explain,
# review, and debug the common Flask patterns used here. This included the app
# setup, environment-variable handling, database connection/teardown, and
# Flask-Login user-loader flow. I reviewed and adjusted the final code to match
# the project requirements and requirements of this app.

app = Flask(__name__)

# Ensure instance directory exists on app startup
os.makedirs(app.instance_path, exist_ok=True)

load_dotenv()
secret_key = os.environ.get("SECRET_KEY")

if not secret_key:
    # If the key is missing, crash the app immediately with error message
    raise ValueError("CRITICAL ERROR: SECRET_KEY is not defined in the environment.")

# Safely assign the verified key
app.secret_key = secret_key

app.config["SESSION_COOKIE_NAME"] = "ozer_session"


# AI-assisted: Copilot helped confirm the standard Flask pattern for a per-request
# SQLite connection and teardown. I adapted the pattern to this project and kept
# the final database lifecycle logic consistent with the app's use of g and SQL.
def get_db():
    if "db" not in g:
        db_path = os.path.join(app.instance_path, "ozer.db")
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def get_user_theme():
    db = get_db()
    theme = db.execute(
        "SELECT default_theme FROM settings WHERE user_id = ?",
        (current_user.id,),
    ).fetchone()

    return theme["default_theme"] if theme else "light"


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
    numeric_id = int(user_id)
    id_match = db.execute("SELECT * FROM users WHERE id = ?", (numeric_id,))
    user = id_match.fetchone()
    if user is not None:
        return User(id=user["id"], username=user["username"])
    else:
        print("ERROR LOADING USER")
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
            (username, hashed_password)
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
    return render_template(
        "home.html",
        user=current_user,
        theme=get_user_theme(),
    )


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
            "light",
            "dark",
            "wireframe",
            "cupcake",
            "bumblebee",
            "emerald",
            "corporate",
            "garden",
            "lemonade",
            "winter",
            "nord",
            "pastel",
            "valentine",
            "fantasy",
            "retro",
            "autumn",
            "caramellatte",
            "silk",
            "acid",
            "cmyk",
            "lofi",
            "cyberpunk",
            "aqua",
            "abyss",
            "black",
            "business",
            "coffee",
            "dim",
            "dracula",
            "forest",
            "halloween",
            "luxury",
            "night",
            "sunset",
            "synthwave"
        ]
        MODELS = [
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b",
            "qwen/qwen3.8-27b"
        ]

        theme = request.form.get("saved_theme")
        model = request.form.get("model-dropdown")
        sys_prompt = request.form.get("sys_prompt")

        if theme:
            if theme not in THEMES:
                flash("Invalid Theme", "error")
                return redirect(url_for("settings"))
            else:
                # Update user settings in settings table of db
                db = get_db()

                update_result = db.execute(
                    "UPDATE settings SET default_theme = ? WHERE user_id = ?",
                    (theme, current_user.id)
                )

                if update_result.rowcount == 0:
                    db.execute(
                        "INSERT INTO settings (user_id, default_theme) VALUES (?, ?)",
                        (current_user.id, theme)
                    )

                db.commit()
                flash("Theme Saved", "success")
                return render_template("settings.html", theme=theme, sys_prompt=sys_prompt)
        elif model:
            if model not in MODELS:
                flash("Invalid Model", "error")
                return redirect(url_for("settings"))
            else:
                # Update user settings in settings table of db
                db = get_db()

                update_result = db.execute(
                    "UPDATE settings SET default_model = ? WHERE user_id = ?",
                    (model, current_user.id)
                )

                if update_result.rowcount == 0:
                    db.execute(
                        "INSERT INTO settings (user_id, default_theme, default_model) VALUES (?, ?, ?)",
                        (current_user.id, get_user_theme(), model)
                    )

                db.commit()
                flash("Model Saved", "success")

                sys_prompt = get_sys_prompt()
                return render_template("settings.html", theme=get_user_theme(), sys_prompt=sys_prompt)
            
        elif not model and not theme and not sys_prompt:
            flash("Invalid Input: Unable to Save Settings", "error")
            return redirect(url_for("settings"))
        
        else:
            if sys_prompt is None:
                sys_prompt = ""
            # Update user settings in settings table of db
            db = get_db()

            update_result = db.execute(
                "UPDATE settings SET default_sys_prompt = ? WHERE user_id = ?",
                (sys_prompt, current_user.id)
            )

            if update_result.rowcount == 0:
                db.execute(
                    "INSERT INTO settings (user_id, default_theme, default_sys_prompt) VALUES (?, ?, ?)",
                    (current_user.id, get_user_theme(), sys_prompt)
                )

            db.commit()
            flash("System Prompt Saved", "success")
            return render_template("settings.html", theme=get_user_theme(), sys_prompt=sys_prompt)

    else:
        db = get_db()
        sys_prompt = get_sys_prompt()

        return render_template("settings.html", theme=get_user_theme(), sys_prompt=sys_prompt)


@app.route("/quick-chat", methods=["GET"])
@login_required
def quick_chat():
    db= get_db()

    model = db.execute(
        """
        SELECT default_model FROM settings
        WHERE user_id = ?
        """,
        (current_user.id,)
    ).fetchone()

    sys_prompt = db.execute(
        """
        SELECT default_sys_prompt FROM settings
        WHERE user_id = ?
        """,
        (current_user.id,)
    ).fetchone()
    if model is None or sys_prompt is None:
        sys_prompt = ""
        db.execute(
            "INSERT INTO settings (user_id, default_theme, default_sys_prompt) VALUES (?, ?, ?)",
            (current_user.id, get_user_theme(), sys_prompt)
        )
    print(current_user["username"], model[0], sys_prompt[0])
    return render_template("chat.html", user=current_user, theme=get_user_theme(), model=model[0], sys_prompt=sys_prompt[0])


# TODO: Needs to be removed when possible
@app.route("/chat", methods=["GET"])
@login_required
def chat_page():
    return render_template("chat.html", theme=get_user_theme())


@app.route("/chat", methods=["POST"])
@login_required
def chat_stream():
    payload = request.get_json()
    print(payload)
    if payload:
        # SQL helper for saving chat in db
        if not payload["existing_chat"]:
            save_chat(payload)
        groq_bot = GroqHandler(client=groq_client, settings=payload["settings"])
        return Response(groq_bot.stream(payload["message"]), mimetype="text/plain")
    else:
        return jsonify({"error" : "Invalid message payload"}), 400
