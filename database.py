import sqlite3

conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

# Users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password BLOB NOT NULL
)
""")

# Chats table
cursor.execute("""
CREATE TABLE IF NOT EXISTS chats(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id TEXT,
    user_email TEXT,
    role TEXT,
    message TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
