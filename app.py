from __future__ import annotations
import os
from functools import wraps

from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from itsdangerous import BadData, URLSafeTimedSerializer
from werkzeug.security import check_password_hash, generate_password_hash
from data.db import close_db, contact_to_dict, get_db, init_db
from data.projects import PROJECTS

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")
if not app.secret_key:
    raise RuntimeError("Missing FLASK_SECRET_KEY. Add it to .env or set it in your environment.")

app.config["DATABASE"] = os.path.join(app.instance_path, "portfolio.db")
app.config["API_TOKEN_EXPIRATION"] = int(os.environ.get("API_TOKEN_EXPIRATION", "3600"))
app.config["API_REFRESH_TOKEN_EXPIRATION"] = int(os.environ.get("API_REFRESH_TOKEN_EXPIRATION", "86400"))
app.config["API_USERNAME"] = os.environ.get("USERNAME", "admin")
app.config["API_PASSWORD_HASH"] = os.environ.get("API_PASSWORD_HASH")
app.config["API_PASSWORD"] = os.environ.get("PASSWORD", "password")
app.config["API_ACCESS_TOKEN_SALT"] = "portfolio-api-access"
app.config["API_REFRESH_TOKEN_SALT"] = "portfolio-api-refresh"
Path(app.instance_path).mkdir(parents=True, exist_ok=True)

if not app.config["API_PASSWORD_HASH"]:
    app.config["API_PASSWORD_HASH"] = generate_password_hash(app.config["API_PASSWORD"])

access_serializer = URLSafeTimedSerializer(app.secret_key, salt=app.config["API_ACCESS_TOKEN_SALT"])
refresh_serializer = URLSafeTimedSerializer(app.secret_key, salt=app.config["API_REFRESH_TOKEN_SALT"])

def generate_api_token(username: str) -> str:
    return access_serializer.dumps({"username": username})


def generate_refresh_token(username: str) -> str:
    return refresh_serializer.dumps({"username": username})


def verify_api_token(token: str) -> bool:
    try:
        data = access_serializer.loads(token, max_age=app.config["API_TOKEN_EXPIRATION"])
        return data.get("username") == app.config["API_USERNAME"]
    except BadData:
        return False


def verify_refresh_token(token: str) -> bool:
    try:
        data = refresh_serializer.loads(token, max_age=app.config["API_REFRESH_TOKEN_EXPIRATION"])
        return data.get("username") == app.config["API_USERNAME"]
    except BadData:
        return False

def require_api_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Authentication credentials were not provided."}), 401

        token = auth_header.split(" ", 1)[1]
        if not verify_api_token(token):
            return jsonify({"error": "Invalid or expired token."}), 401
        return f(*args, **kwargs)

    return decorated

app.teardown_appcontext(close_db)


@app.before_request
def ensure_database() -> None:
    init_db()

# ++ API Endpoints ++
@app.route("/ping", methods=["GET"])
def ping() -> tuple[dict, int]:
    return {"status": "ok", "message": "Portfolio API is available."}, 200

def verify_user_credentials(username: str, password: str) -> bool:
    if username != app.config["API_USERNAME"]:
        return False
    return check_password_hash(app.config["API_PASSWORD_HASH"], password)


@app.route("/login", methods=["POST"])
def login() -> tuple[dict, int]:
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password or not verify_user_credentials(username, password):
        return {"error": "Invalid credentials."}, 401

    access_token = generate_api_token(username)
    refresh_token = generate_refresh_token(username)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
        "expires_in": app.config["API_TOKEN_EXPIRATION"],
    }, 200


@app.route("/refresh", methods=["POST"])
def refresh_token() -> tuple[dict, int]:
    data = request.get_json(silent=True) or {}
    refresh_token_value = data.get("refresh_token")
    if not refresh_token_value or not verify_refresh_token(refresh_token_value):
        return {"error": "Invalid or expired refresh token."}, 401

    new_access_token = generate_api_token(app.config["API_USERNAME"])
    new_refresh_token = generate_refresh_token(app.config["API_USERNAME"])
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "Bearer",
        "expires_in": app.config["API_TOKEN_EXPIRATION"],
    }, 200


@app.route("/contacts", methods=["GET", "POST"])
@require_api_auth
def contacts_collection() -> tuple[dict, int]:
    db = get_db()

    if request.method == "GET":
        rows = db.execute("SELECT * FROM contacts ORDER BY created_at DESC").fetchall()
        return {"contacts": [contact_to_dict(row) for row in rows]}, 200

    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        full_name = (data.get("full_name") or "").strip()
        email = (data.get("email") or "").strip()
        phone = (data.get("phone") or "").strip()
        company = (data.get("company") or "").strip()
        subject = (data.get("subject") or "").strip()
        message = (data.get("message") or "").strip()

        if not full_name or not email or not message:
            return {"error": "Required fields: full_name, email, message."}, 400

        cursor = db.execute(
            "INSERT INTO contacts (full_name, email, phone, company, subject, message) VALUES (?, ?, ?, ?, ?, ?)",
            (full_name, email, phone, company, subject, message),
        )
        db.commit()
        contact_id = cursor.lastrowid
        row = db.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,)).fetchone()
        return {"contact": contact_to_dict(row)}, 201


@app.route("/contacts/<int:contact_id>", methods=["GET", "PUT", "DELETE"])
@require_api_auth
def contact_item(contact_id: int) -> tuple[dict, int]:
    db = get_db()
    row = db.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,)).fetchone()
    if row is None:
        return {"error": "Contact record not found."}, 404

    if request.method == "GET":
        return {"contact": contact_to_dict(row)}, 200

    if request.method == "PUT":
        data = request.get_json(silent=True) or {}
        full_name = (data.get("full_name") or row["full_name"]).strip()
        email = (data.get("email") or row["email"]).strip()
        phone = (data.get("phone") or row["phone"]).strip()
        company = (data.get("company") or row["company"]).strip()
        subject = (data.get("subject") or row["subject"]).strip()
        message = (data.get("message") or row["message"]).strip()

        if not full_name or not email or not message:
            return {"error": "Required fields: full_name, email, message."}, 400

        db.execute(
            "UPDATE contacts SET full_name = ?, email = ?, phone = ?, company = ?, subject = ?, message = ? WHERE id = ?",
            (full_name, email, phone, company, subject, message, contact_id),
        )
        db.commit()
        row = db.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,)).fetchone()
        return {"contact": contact_to_dict(row)}, 200

    if request.method == "DELETE":
        db.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
        db.commit()
        return {"message": "Contact deleted successfully."}, 200

# ++ Web Routes ++
@app.route("/")
def home() -> str:
    return render_template("home.html", title="Home | Julio Angulo", body_class="home-page")

@app.route("/about")
def about() -> str:
    return render_template("about.html", title="About | Julio Angulo", body_class="about-page")

@app.route("/projects")
def projects() -> str:
    return render_template("projects.html", title="Projects | Julio Angulo", body_class="projects-page", projects=PROJECTS)

@app.route("/contact", methods=["GET", "POST"])
def contact() -> str:
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        company = request.form.get("company", "").strip()
        subject = request.form.get("subject", "").strip()
        message = request.form.get("message", "").strip()

        if not full_name or not email or not message:
            flash("Please complete the required fields: Name, Email, and Message.", "error")
            return redirect(url_for("contact"))

        db = get_db()
        db.execute(
            "INSERT INTO contacts (full_name, email, phone, company, subject, message) VALUES (?, ?, ?, ?, ?, ?)",
            (full_name, email, phone, company, subject, message),
        )
        db.commit()
        flash("Message received! I will review it soon.", "success")
        return redirect(url_for("contact"))

    contact_info = {
        "phone": "+1 555 123 4567",
        "email": "julio.angulo@example.com",
        "linkedin": "https://www.linkedin.com/in/julioangulo",
    }
    return render_template("contact.html", contact_info=contact_info)

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=os.getenv("FLASK_DEBUG", "false").lower() == "true",
    )
