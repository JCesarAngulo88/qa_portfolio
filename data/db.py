from __future__ import annotations
import sqlite3
from pathlib import Path

from flask import current_app as app, g

def get_db() -> sqlite3.Connection:
    db = getattr(g, "db", None)
    if db is None:
        Path(app.instance_path).mkdir(parents=True, exist_ok=True)
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

def close_db(error: Exception | None = None) -> None:
    db = getattr(g, "db", None)
    if db is not None:
        db.close()

def contact_to_dict(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "full_name": row["full_name"],
        "email": row["email"],
        "phone": row["phone"],
        "company": row["company"],
        "subject": row["subject"],
        "message": row["message"],
        "created_at": row["created_at"],
    }
