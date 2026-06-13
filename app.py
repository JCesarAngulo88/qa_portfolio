from __future__ import annotations
import os
import sqlite3

from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, g, render_template, request, redirect, url_for, flash
from data.projects import PROJECTS

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")
if not app.secret_key:
    raise RuntimeError("Missing FLASK_SECRET_KEY. Add it to .env or set it in your environment.")
app.config["DATABASE"] = os.path.join(app.instance_path, "portfolio.db")
Path(app.instance_path).mkdir(parents=True, exist_ok=True)

def get_db() -> sqlite3.Connection:
    db = getattr(g, "db", None)
    if db is None:
        db = sqlite3.connect(app.config["DATABASE"])
        db.row_factory = sqlite3.Row
        g.db = db
    return db


def init_db() -> None:
    db = get_db()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            company TEXT,
            subject TEXT,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    db.commit()


@app.teardown_appcontext
def close_db(error: Exception | None = None) -> None:
    db = getattr(g, "db", None)
    if db is not None:
        db.close()


@app.before_request
def ensure_database() -> None:
    init_db()


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
    app.run(debug=True, port=5000)
