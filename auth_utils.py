import bcrypt
from database import conn, cursor

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

    except Exception:
        return False


# -----------------------------
# Login
# -----------------------------
def login(email, password):

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


# -----------------------------
# User Account
# -----------------------------
def get_user_by_email(email):
    cursor.execute(
        """
        SELECT id, username, email
        FROM users
        WHERE email = ?
        """,
        (email,)
    )

    return cursor.fetchone()


def update_username(email, username):
    cursor.execute(
        """
        UPDATE users
        SET username = ?
        WHERE email = ?
        """,
        (username, email)
    )

    conn.commit()


def change_password(email, current_password, new_password):
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


# -----------------------------
# User Summaries
# -----------------------------
def get_user_summaries():
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


# -----------------------------
# App Owner
# -----------------------------
def get_first_user_email():
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

