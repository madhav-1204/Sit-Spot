import sqlite3
import os
from datetime import datetime

DB_PATH = os.environ.get("SITSPOT_DB", "sitspot.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                target_minutes INTEGER NOT NULL,
                outside_seconds INTEGER NOT NULL,
                screen_seconds INTEGER NOT NULL,
                prompt TEXT NOT NULL,
                raw_notes TEXT NOT NULL,
                tidy_entry TEXT,
                follow_up TEXT,
                is_raw_only INTEGER DEFAULT 0
            )
        """)
    conn.close()

def get_entry_count():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM entries")
    count = cur.fetchone()[0]
    conn.close()
    return count

def get_last_entry():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM entries ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def get_recent_entries(limit=3):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM entries ORDER BY id DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_entries():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM entries ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_entry(entry_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM entries WHERE id = ?", (entry_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def save_entry(target_minutes, outside_seconds, screen_seconds, prompt, raw_notes, tidy_entry=None, follow_up=None, is_raw_only=0):
    created_at = datetime.now().isoformat()
    conn = get_connection()
    with conn:
        cur = conn.execute("""
            INSERT INTO entries (
                created_at, target_minutes, outside_seconds, screen_seconds,
                prompt, raw_notes, tidy_entry, follow_up, is_raw_only
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            created_at, target_minutes, outside_seconds, screen_seconds,
            prompt, raw_notes, tidy_entry, follow_up, is_raw_only
        ))
        entry_id = cur.lastrowid
    conn.close()
    return entry_id

def update_entry(entry_id, raw_notes, tidy_entry, follow_up, is_raw_only=0):
    conn = get_connection()
    with conn:
        conn.execute("""
            UPDATE entries
            SET raw_notes = ?, tidy_entry = ?, follow_up = ?, is_raw_only = ?
            WHERE id = ?
        """, (raw_notes, tidy_entry, follow_up, is_raw_only, entry_id))
    conn.close()
