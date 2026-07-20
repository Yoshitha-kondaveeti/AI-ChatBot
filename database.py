import sqlite3
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), "users.db")


def get_connection():
    """Return a configured SQLite connection for the app database."""
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=5000")
    return conn


# -------------------------
# Database Initialization
# -------------------------
def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password BLOB NOT NULL
    )
    """)

    # Chats Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id TEXT NOT NULL,
        user_email TEXT NOT NULL,
        role TEXT NOT NULL,
        message TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_users_email
    ON users(email)
    """)

    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_chats_user_email
    ON chats(user_email)
    """)

    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_chats_chat_id
    ON chats(chat_id)
    """)

    conn.commit()
    cursor.close()
    conn.close()


init_db()
