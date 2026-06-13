import hashlib
import secrets

from database import conn, cursor


def hash_password(password: str, salt: str | None = None) -> str:
    """Hash a password with a random salt using SHA-256."""
    if salt is None:
        salt = secrets.token_hex(16)
    pwd_hash = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return f"{salt}${pwd_hash}"


def verify_password(password: str, stored: str) -> bool:
    """Check a plaintext password against a stored salt$hash value."""
    try:
        salt, pwd_hash = stored.split("$", 1)
    except ValueError:
        return False

    candidate = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return secrets.compare_digest(candidate, pwd_hash)


def signup_user(username: str, email: str, password: str):
    """Create a new user account. Returns (success, message)."""
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        return False, "An account with that email already exists."

    hashed = hash_password(password)
    cursor.execute(
        "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
        (username, email, hashed),
    )
    conn.commit()
    return True, "Account created successfully! You can now log in."


def login_user(email: str, password: str):
    """Validate login credentials. Returns (success, username_or_error)."""
    cursor.execute("SELECT username, password FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()

    if not row:
        return False, "No account found with that email."

    username, stored_hash = row
    if verify_password(password, stored_hash):
        return True, username

    return False, "Incorrect password."
