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

