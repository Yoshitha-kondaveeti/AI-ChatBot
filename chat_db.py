import uuid
import sys
from database import get_connection

# Create a new chat ID
def create_chat():
    return str(uuid.uuid4())

# Save a message
def save_message(chat_id, user_email, role, message):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO chats (chat_id, user_email, role, message)
            VALUES (?, ?, ?, ?)
            """,
            (chat_id, user_email, role, message)
        )
        conn.commit()
    except Exception as e:
        print(f"Error saving message: {e}", file=sys.stderr)
    finally:
        cursor.close()
        conn.close()

# Load messages for one chat
def load_chat(chat_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
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
    except Exception as e:
        print(f"Error loading chat {chat_id}: {e}", file=sys.stderr)
        return []
    finally:
        cursor.close()
        conn.close()

# Get all chat IDs for a user
def get_all_chats(user_email):
    conn = get_connection()
    cursor = conn.cursor()
    try:
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
    except Exception as e:
        print(f"Error getting all chats for {user_email}: {e}", file=sys.stderr)
        return []
    finally:
        cursor.close()
        conn.close()

# Get chat history with readable titles
def get_chat_summaries(user_email):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT
                chat_id,
                COALESCE(
                    MIN(CASE WHEN role = 'user' THEN message END),
                    'New chat'
                ) AS title,
                COUNT(*) AS message_count,
                MAX(timestamp) AS updated_at
            FROM chats
            WHERE user_email = ?
            GROUP BY chat_id
            ORDER BY MAX(id) DESC
            """,
            (user_email,)
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"Error getting chat summaries for {user_email}: {e}", file=sys.stderr)
        return []
    finally:
        cursor.close()
        conn.close()

# Delete a chat
def delete_chat(chat_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            DELETE FROM chats
            WHERE chat_id = ?
            """,
            (chat_id,)
        )
        conn.commit()
    except Exception as e:
        print(f"Error deleting chat {chat_id}: {e}", file=sys.stderr)
    finally:
        cursor.close()
        conn.close()

# Get the latest chat ID for a user
def get_latest_chat(user_email):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT chat_id
            FROM chats
            WHERE user_email = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (user_email,)
        )
        row = cursor.fetchone()
        return row[0] if row else None
    except Exception as e:
        print(f"Error getting latest chat for {user_email}: {e}", file=sys.stderr)
        return None
    finally:
        cursor.close()
        conn.close()
