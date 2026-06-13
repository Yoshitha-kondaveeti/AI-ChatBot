from database import conn, cursor
import uuid

# Create a new chat ID
def create_chat():
    return str(uuid.uuid4())

# Save a message
def save_message(chat_id, user_email, role, message):
    cursor.execute(
        """
        INSERT INTO chats (chat_id, user_email, role, message)
        VALUES (?, ?, ?, ?)
        """,
        (chat_id, user_email, role, message)
    )
    conn.commit()

# Load messages for one chat
def load_chat(chat_id):
    cursor.execute(
        """
        SELECT role, message
        FROM chats
        WHERE chat_id = ?
        ORDER BY id
        """,
        (chat_id,)
    )

    rows = cursor.fetchall()

    return [
        {
            "role": role,
            "content": message
        }
        for role, message in rows
    ]

# Get all chat IDs for a user
def get_all_chats(user_email):
    cursor.execute(
        """
        SELECT DISTINCT chat_id
        FROM chats
        WHERE user_email = ?
        ORDER BY id DESC
        """,
        (user_email,)
    )

    return cursor.fetchall()

# Delete a chat
def delete_chat(chat_id):
    cursor.execute(
        """
        DELETE FROM chats
        WHERE chat_id = ?
        """,
        (chat_id,)
    )

    conn.commit()
