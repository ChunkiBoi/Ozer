# Ozer

A Python/Flask based AI chatbot platform featuring multi-model free-tier support (Groq/OpenAI/Gemini), customizable bot personas, other personalization features, temporal message retrieval, and secure user authentication. Created as my Final Project for Harvard's CS50x course.

## AI Assistance Disclosure

GitHub Copilot was used during development as a learning and development assistant. I remain responsible for understanding, testing, editing, and integrating the submitted code.

The assistance used in this project included:

- Explaining Flask application-context teardown, SQLite connections and cursors, Flask redirects, form access, regular expressions, password validation, and database cleanup.
- Reviewing the Flask authentication and database code and pointing out implementation issues, including route flow, schema/application column consistency, commits, and protected routes.
- Suggesting and applying edits to Flask routes, authentication flow, password validation, database initialization, and Jinja templates.
- Helping debug template rendering and HTTP responses with Flask test-client checks and Python compilation checks.
- Suggesting HTML, Tailwind CSS, and DaisyUI layouts for the login, registration, navigation drawer, theme selector, flash messages, favicon/logo use, and home-page carousel.
- Iterating on the responsive home-page card and carousel based on my visual feedback. I rejected or reverted several proposed frontend changes and directed the final design.

Copilot was not used as a substitute for understanding the project. I asked questions about the suggested code, made the final decisions, reviewed changes in the editor, and tested the application. This disclosure summarizes the recorded Copilot session and is not a claim that it captures every inline autocomplete suggestion; any additional autocomplete usage should be added here before submission.

File-level disclosure comments identify files where AI assistance was materially involved. They describe the type of assistance rather than claiming that Copilot authored the entire file.

## Third-Party Software and Services

- **Python**: programming language and standard-library modules, including `sqlite3`, `os`, `re`, and `pathlib`.
- **Flask**: web framework used for routing, rendering, redirects, sessions, and application context management.
- **Flask-Login**: user-session and authentication helpers such as `login_required`, `login_user`, and `logout_user`.
- **Werkzeug**: password hashing and verification through `generate_password_hash` and `check_password_hash`.
- **python-dotenv**: loads the application's `SECRET_KEY` from environment configuration.
- **SQLite**: local database engine used for users, bots, and messages.
- **Groq, OpenAI, and Google GenAI Python packages**: imported in the project for planned or implemented multi-model chatbot functionality.
- **Tailwind CSS browser build**: loaded from jsDelivr in `templates/layout.html` for utility classes.
- **DaisyUI**: loaded from jsDelivr in `templates/layout.html` for components, themes, drawer behavior, alerts, cards, and carousel styling.
- **Inline SVG icons and the existing Ozer logo assets**: used in the templates and `static/` directory.

Third-party libraries and CDN assets remain subject to their own licenses and terms. Their documentation and package/CDN sources should be cited or linked according to the course submission requirements.

## Academic Honesty Note

This project includes substantial Copilot-assisted explanation, debugging, code suggestions, and frontend implementation. Whether that use complies with CS50x depends on the course's current Final Project policy and the instructor's interpretation of permitted AI assistance. The disclosure above is necessary for transparency, but it does not by itself make prohibited assistance permissible. Before submitting, compare the complete interaction history and your use of autocomplete with the current CS50 policy. If the policy prohibits generated code or requires a more specific attribution format, ask the course staff how to report this work and follow their direction.
