import os

import streamlit as st
from dotenv import load_dotenv
from groq import Groq

from auth_utils import login, signup
from chat_db import create_chat, delete_chat, get_all_chats, load_chat, save_message


load_dotenv()


def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    return Groq(api_key=api_key)


client = get_groq_client()


st.set_page_config(
    page_title="YM Bot",
    page_icon="🤖",
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f172a, #1e293b, #0f172a);
    }

    .block-container {
        padding-top: 2rem;
    }

    section[data-testid="stSidebar"] {
        background: #111827;
    }

    div[data-testid="stChatMessage"] {
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 10px;
        border: 1px solid #374151;
    }

    .stButton > button {
        width: 100%;
        border-radius: 10px;
        background: #2563eb;
        color: white;
        border: none;
    }

    .stButton > button:hover {
        background: #1d4ed8;
        color: white;
    }

    h1, h2, h3 {
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def init_session_state():
    defaults = {
        "logged_in": False,
        "messages": [],
        "chat_id": create_chat(),
        "email": "",
        "username": "",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def start_new_chat():
    st.session_state.chat_id = create_chat()
    st.session_state.messages = []


def logout():
    st.session_state.logged_in = False
    st.session_state.email = ""
    st.session_state.username = ""
    start_new_chat()


def send_prompt(prompt):
 if client is None:
        st.error("GROQ_API_KEY is missing. Add it to your .env file and restart Streamlit.")
        return

st.session_state.messages.append({"role": "user", "content": prompt})
save_message(st.session_state.chat_id, st.session_state.email, "user", prompt)

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=st.session_state.messages,
        )
        reply = response.choices[0].message.content
    except Exception as exc:
        reply = f"Sorry, I could not get a response right now. Error: {exc}"

    st.session_state.messages.append({"role": "assistant", "content": reply})
    save_message(st.session_state.chat_id, st.session_state.email, "assistant", reply)


def render_auth_page():
    st.title("🤖 YM Bot AI Assistant")
    st.caption("Powered by Groq • Fast • Smart • Secure")

    menu = st.sidebar.selectbox("Menu", ["Login", "Sign Up"])

    if menu == "Sign Up":
        st.subheader("Create Account")

        username = st.text_input("Username").strip()
        email = st.text_input("Email").strip().lower()
        password = st.text_input("Password", type="password")

        if st.button("Create Account"):
            if not username or not email or not password:
                st.error("Please fill in username, email, and password.")
            elif signup(username, email, password):
                st.success("Account created successfully. You can log in now.")
            else:
                st.error("That email is already registered.")

    else:
        st.subheader("Login")

        email = st.text_input("Email").strip().lower()
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            user = login(email, password)

            if user:
                st.session_state.logged_in = True
                st.session_state.email = email
                st.session_state.username = user[1]
                start_new_chat()
                st.rerun()

            st.error("Invalid email or password.")


def render_sidebar():
    st.sidebar.title("🤖 YM Bot")
    st.sidebar.markdown(
        f"""
        ### 👤 {st.session_state.username}

        🟢 Online

        📧 {st.session_state.email}
        """
    )
    st.sidebar.divider()

    if st.sidebar.button("➕ New Chat"):
        start_new_chat()
        st.rerun()

    st.sidebar.markdown("### Chat History")
    chats = get_all_chats(st.session_state.email)

    if not chats:
        st.sidebar.caption("No saved chats yet.")

    for (chat_id,) in chats:
        col1, col2 = st.sidebar.columns([4, 1])

        with col1:
            if st.button(chat_id[:8], key=f"open-{chat_id}"):
                st.session_state.chat_id = chat_id
                st.session_state.messages = load_chat(chat_id)
                st.rerun()

        with col2:
            if st.button("🗑", key=f"delete-{chat_id}", help="Delete chat"):
                delete_chat(chat_id)
                if st.session_state.chat_id == chat_id:
                    start_new_chat()
                st.rerun()

    st.sidebar.divider()

    if st.sidebar.button("🚪 Logout"):
        logout()
        st.rerun()


def render_chat_page():
    render_sidebar()

    st.title("🤖 YM Bot")
    st.caption("Your Smart AI Assistant")

    for message in st.session_state.messages:
        avatar = "👤" if message["role"] == "user" else "🤖"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    if not st.session_state.messages:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.button("💻 Code")
        with col2:
            st.button("📚 AI")
        with col3:
            st.button("📝 Resume")

    prompt = st.chat_input("💬 Ask YM Bot anything...")
    if prompt:
        with st.spinner("🤖 YM Bot is thinking..."):
            send_prompt(prompt)
        st.rerun()


init_session_state()

if st.session_state.logged_in:
    render_chat_page()
else:
    render_auth_page()
