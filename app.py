from database import conn, cursor
from chat_db import (
    create_chat,
    save_message,
    load_chat,
    get_all_chats,
    delete_chat
)

def save_message(user_email, role, message):
    chat_id = create_chat()
    save_message(chat_id, user_email, role, message)


def load_messages(user_email):
    cursor.execute(
        """
        SELECT role, message
        FROM chats
        WHERE user_email=?
        ORDER BY id
        """,
        (user_email,)
    )

    rows = cursor.fetchall()

    messages = []

    for role, message in rows:

        messages.append(
            {
                "role": role,
                "content": message
            }
        )

    return messages


def clear_messages(user_email):
    cursor.execute(
        """
        DELETE FROM chats
        WHERE user_email=?
        """,
        (user_email,)
    )

    conn.commit()
