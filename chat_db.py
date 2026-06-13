from database import conn, cursor

# Save a message to the database
def save_message(user_email, role, message):
    cursor.execute(
        """
        INSERT INTO chats (user_email, role, message)
        VALUES (?, ?, ?)
        """,
        (user_email, role, message)
    )
    conn.commit()

# Load all messages for a user
def load_messages(user_email):
    cursor.execute(
        """
        SELECT role, message
        FROM chats
        WHERE user_email = ?
        ORDER BY id ASC
        """,
        (user_email,)
    )

    rows = cursor.fetchall()

    messages = []

    for role, message in rows:
        messages.append({
            "role": role,
            "content": message
        })

    return messages

# Delete all messages for a user
def clear_messages(user_email):
    cursor.execute(
        """
        DELETE FROM chats
        WHERE user_email = ?
        """,
        (user_email,)
    )
    conn.commit()
