import sqlite3
import sys

import bcrypt

from database import get_connection


def normalize_email(email):
    return (email or "").strip().lower()


def hash_password(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())


def check_password(password, hashed):
    if isinstance(hashed, str):
        hashed = hashed.encode("utf-8")
    return bcrypt.checkpw(password.encode("utf-8"), hashed)


def signup(username, email, password):
    username = (username or "").strip()
    email = normalize_email(email)

    if not username or not email or not password:
        return False

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO users(username, email, password)
            VALUES (?, ?, ?)
            """,
            (username, email, hash_password(password)),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    except Exception as exc:
        print(f"Signup database error for {email}: {exc}", file=sys.stderr)
        return False
    finally:
        cursor.close()
        conn.close()


def login(email, password):
    email = normalize_email(email)

    if not email or not password:
        return None

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT id, username, email, password
            FROM users
            WHERE email = ?
            """,
            (email,),
        )
        user = cursor.fetchone()

        if user and check_password(password, user[3]):
            return user

        return None
    except Exception as exc:
        print(f"Login database error for {email}: {exc}", file=sys.stderr)
        return None
    finally:
        cursor.close()
        conn.close()


def get_user_by_email(email):
    email = normalize_email(email)
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT id, username, email
            FROM users
            WHERE email = ?
            """,
            (email,),
        )
        return cursor.fetchone()
    except Exception as exc:
        print(f"Error fetching user {email}: {exc}", file=sys.stderr)
        return None
    finally:
        cursor.close()
        conn.close()


def user_exists(email):
    return get_user_by_email(email) is not None


def update_username(email, username):
    email = normalize_email(email)
    username = (username or "").strip()

    if not email or not username:
        return False

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            UPDATE users
            SET username = ?
            WHERE email = ?
            """,
            (username, email),
        )
        conn.commit()
        return cursor.rowcount > 0
    except Exception as exc:
        print(f"Error updating username for {email}: {exc}", file=sys.stderr)
        return False
    finally:
        cursor.close()
        conn.close()


def change_password(email, current_password, new_password):
    email = normalize_email(email)

    if not email or not current_password or not new_password:
        return False

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT password
            FROM users
            WHERE email = ?
            """,
            (email,),
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
            (hash_password(new_password), email),
        )
        conn.commit()
        return cursor.rowcount > 0
    except Exception as exc:
        print(f"Error changing password for {email}: {exc}", file=sys.stderr)
        return False
    finally:
        cursor.close()
        conn.close()


def reset_password(email, new_password):
    email = normalize_email(email)

    if not email or not new_password:
        return False

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            UPDATE users
            SET password = ?
            WHERE email = ?
            """,
            (hash_password(new_password), email),
        )
        conn.commit()
        return cursor.rowcount > 0
    except Exception as exc:
        print(f"Error resetting password for {email}: {exc}", file=sys.stderr)
        return False
    finally:
        cursor.close()
        conn.close()


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
    except Exception as exc:
        print(f"Error fetching user summaries: {exc}", file=sys.stderr)
        return []
    finally:
        cursor.close()
        conn.close()


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
    except Exception as exc:
        print(f"Error getting first user email: {exc}", file=sys.stderr)
        return None
    finally:
        cursor.close()
        conn.close()
