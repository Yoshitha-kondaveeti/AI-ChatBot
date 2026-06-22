import bcrypt
import sys
from database import get_connection

# -----------------------------
# Hash Password
# -----------------------------
def hash_password(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())


# -----------------------------
# Check Password
# -----------------------------
def check_password(password, hashed):
    return bcrypt.checkpw(password.encode("utf-8"), hashed)


# -----------------------------
# Sign Up
# -----------------------------
def signup(username, email, password):
    hashed = hash_password(password)
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO users(username, email, password)
            VALUES (?, ?, ?)
            """,
            (username, email, hashed)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Signup database error for email {email}: {e}", file=sys.stderr)
        return False
    finally:
        cursor.close()
        conn.close()


# -----------------------------
# Login
# -----------------------------
def login(email, password):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE email = ?
            """,
            (email,)
        )
        user = cursor.fetchone()
        if user:
            if check_password(password, user[3]):
                return user
        return None
    except Exception as e:
        print(f"Login database error for email {email}: {e}", file=sys.stderr)
        return None
    finally:
        cursor.close()
        conn.close()


# -----------------------------
# User Account
# -----------------------------
def get_user_by_email(email):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT id, username, email
            FROM users
            WHERE email = ?
            """,
            (email,)
        )
        return cursor.fetchone()
    except Exception as e:
        print(f"Error fetching user by email {email}: {e}", file=sys.stderr)
        return None
    finally:
        cursor.close()
        conn.close()


def update_username(email, username):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE users
            SET username = ?
            WHERE email = ?
            """,
            (username, email)
        )
        conn.commit()
    except Exception as e:
        print(f"Error updating username for {email}: {e}", file=sys.stderr)
    finally:
        cursor.close()
        conn.close()


def change_password(email, current_password, new_password):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT password
            FROM users
            WHERE email = ?
            """,
            (email,)
        )
        row = cursor.fetchone()
        if not row or not check_password(current_password, row[0]):
            return False

        cursor.execute(
            """
            UPDATE users
            SET password = ?
            WHERE email = ?
            """,
            (hash_password(new_password), email)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Error changing password for {email}: {e}", file=sys.stderr)
        return False
    finally:
        cursor.close()
        conn.close()


# -----------------------------
# User Summaries
# -----------------------------
def get_user_summaries():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT
                users.id,
                users.username,
                users.email,
                COUNT(DISTINCT chats.chat_id) AS chat_count,
                COUNT(chats.id) AS message_count,
                MAX(chats.timestamp) AS last_active
            FROM users
            LEFT JOIN chats
                ON chats.user_email = users.email
            GROUP BY users.id, users.username, users.email
            ORDER BY users.id DESC
            """
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching user summaries: {e}", file=sys.stderr)
        return []
    finally:
        cursor.close()
        conn.close()


# -----------------------------
# App Owner
# -----------------------------
def get_first_user_email():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT email
            FROM users
            ORDER BY id ASC
            LIMIT 1
            """
        )
        row = cursor.fetchone()
        return row[0] if row else None
    except Exception as e:
        print(f"Error getting first user email: {e}", file=sys.stderr)
        return None
    finally:
        cursor.close()
        conn.close()
