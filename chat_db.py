import sys
import uuid

from auth_utils import normalize_email
from database import get_connection


VALID_ROLES = {"user", "assistant", "system"}


def create_chat():
    return str(uuid.uuid4())


def save_message(chat_id, user_email, role, message):
    user_email = normalize_email(user_email)
    message = (message or "").strip()

    if not chat_id or not user_email or role not in VALID_ROLES or not message:
        return False

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO chats (chat_id, user_email, role, message)
            VALUES (?, ?, ?, ?)
            """,
            (chat_id, user_email, role, message),
        )
        conn.commit()
        return True
    except Exception as exc:
        print(f"Error saving message for {user_email}: {exc}", file=sys.stderr)
        return False
    finally:
        cursor.close()
        conn.close()


def load_chat(chat_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT role, message
            FROM chats
            WHERE chat_id = ?
            ORDER BY id ASC
            """,
            (chat_id,),
        )
        return [
            {"role": role, "content": message}
            for role, message in cursor.fetchall()
        ]
    except Exception as exc:
        print(f"Error loading chat {chat_id}: {exc}", file=sys.stderr)
        return []
    finally:
        cursor.close()
        conn.close()


def get_all_chats(user_email):
    user_email = normalize_email(user_email)
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT chat_id
            FROM chats
            WHERE user_email = ?
            GROUP BY chat_id
            ORDER BY MAX(id) DESC
            """,
            (user_email,),
        )
        return cursor.fetchall()
    except Exception as exc:
        print(f"Error getting chats for {user_email}: {exc}", file=sys.stderr)
        return []
    finally:
        cursor.close()
        conn.close()


def get_chat_summaries(user_email):
    user_email = normalize_email(user_email)
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            WITH chat_stats AS (
                SELECT
                    chat_id,
                    COUNT(*) AS message_count,
                    MAX(timestamp) AS updated_at,
                    MAX(id) AS latest_id
                FROM chats
                WHERE user_email = ?
                GROUP BY chat_id
            ),
            first_user_messages AS (
                SELECT chats.chat_id, chats.message
                FROM chats
                INNER JOIN (
                    SELECT chat_id, MIN(id) AS first_user_id
                    FROM chats
                    WHERE user_email = ? AND role = 'user'
                    GROUP BY chat_id
                ) firsts
                    ON chats.chat_id = firsts.chat_id
                    AND chats.id = firsts.first_user_id
            )
            SELECT
                chat_stats.chat_id,
                COALESCE(first_user_messages.message, 'New chat') AS title,
                chat_stats.message_count,
                chat_stats.updated_at
            FROM chat_stats
            LEFT JOIN first_user_messages
                ON first_user_messages.chat_id = chat_stats.chat_id
            ORDER BY chat_stats.latest_id DESC
            """,
            (user_email, user_email),
        )
        return cursor.fetchall()
    except Exception as exc:
        print(f"Error getting chat summaries for {user_email}: {exc}", file=sys.stderr)
        return []
    finally:
        cursor.close()
        conn.close()


def delete_chat(chat_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            DELETE FROM chats
            WHERE chat_id = ?
            """,
            (chat_id,),
        )
        conn.commit()
        return cursor.rowcount > 0
    except Exception as exc:
        print(f"Error deleting chat {chat_id}: {exc}", file=sys.stderr)
        return False
    finally:
        cursor.close()
        conn.close()


def get_latest_chat(user_email):
    user_email = normalize_email(user_email)
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
            (user_email,),
        )
        row = cursor.fetchone()
        return row[0] if row else None
    except Exception as exc:
        print(f"Error getting latest chat for {user_email}: {exc}", file=sys.stderr)
        return None
    finally:
        cursor.close()
        conn.close()
