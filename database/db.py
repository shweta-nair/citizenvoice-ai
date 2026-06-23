"""
CitizenVoice AI - Database Setup

Creates database/sqlite.db with a `conversations` table populated from
data/conversations.csv. Also provides helper functions used by the app to
insert newly-analyzed conversations (from the Upload / AI Analysis pages).

Run:  python database/db.py
"""

import os
import sqlite3
import pandas as pd

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
DB_PATH = os.path.join(BASE_DIR, "database", "sqlite.db")
DATA_PATH = os.path.join(BASE_DIR, "data", "conversations.csv")

SCHEMA = """
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    district TEXT NOT NULL,
    locality TEXT,
    category TEXT,
    department TEXT NOT NULL,
    transcript TEXT NOT NULL,
    sentiment TEXT NOT NULL,
    sentiment_score REAL,
    priority TEXT NOT NULL,
    confidence REAL,
    source TEXT DEFAULT 'seed'
);
"""


def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def init_db(reset=False):
    conn = get_connection()
    cur = conn.cursor()
    if reset:
        cur.execute("DROP TABLE IF EXISTS conversations")
    cur.execute(SCHEMA)
    conn.commit()
    return conn


def seed_from_csv(conn):
    df = pd.read_csv(DATA_PATH)
    df = df.rename(columns={"id": "source_id"})
    df["confidence"] = 0.95
    df["source"] = "seed"
    cols = ["date", "district", "locality", "category", "department",
            "transcript", "sentiment", "sentiment_score", "priority",
            "confidence", "source"]
    df[cols].to_sql("conversations", conn, if_exists="append", index=False)
    conn.commit()


def insert_conversation(conn, record):
    """Insert a single new analyzed conversation (used by Upload/AI Analysis pages)."""
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO conversations
        (date, district, locality, category, department, transcript,
         sentiment, sentiment_score, priority, confidence, source)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        record.get("date"), record.get("district"), record.get("locality"),
        record.get("category"), record.get("department"), record.get("transcript"),
        record.get("sentiment"), record.get("sentiment_score"), record.get("priority"),
        record.get("confidence"), record.get("source", "upload"),
    ))
    conn.commit()
    return cur.lastrowid


def fetch_all(conn):
    return pd.read_sql_query("SELECT * FROM conversations", conn)


if __name__ == "__main__":
    conn = init_db(reset=True)
    seed_from_csv(conn)
    count = conn.execute("SELECT COUNT(*) FROM conversations").fetchone()[0]
    print(f"Database initialized at {DB_PATH} with {count} records.")
    conn.close()
