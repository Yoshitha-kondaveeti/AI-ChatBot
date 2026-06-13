import bcrypt
from database import conn, cursor

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed)

def signup(username, email, password):
    hashed = hash_password(password)

    try:
        cursor.execute(
            "INSERT INTO users(username,email,password) VALUES(?,?,?)",
            (username, email, hashed)
        )
        conn.commit()
        return True
    except:
        return False

def login(email, password):
    cursor.execute(
        "SELECT * FROM users WHERE email=?",
        (email,)
    )

    user = cursor.fetchone()

    if user:
        if check_password(password, user[3]):
            return user

    return None
