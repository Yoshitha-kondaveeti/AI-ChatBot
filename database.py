import sqlite3
import os

# Resolve the absolute path to users.db relative to this file's location
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "users.db")

def get_connection():
    """Returns a new SQLite connection with WAL mode enabled for thread safety."""
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    # Enable Write-Ahead Logging (WAL) for concurrent reads/writes
    conn.execute("PRAGMA journal_mode=WAL;")
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

    conn.commit()
    cursor.close()
    conn.close()

# Initialize tables on import
init_db()
