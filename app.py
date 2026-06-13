import streamlit as st
from auth_utils import signup, login
from chat_db import (
    create_chat,
    save_message,
    load_chat,
    get_all_chats,
    delete_chat
)
from groq import Groq
from dotenv import load_dotenv
import os

# -----------------------------
# Load Environment Variables
# -----------------------------
load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="YM Bot",
    page_icon="🤖",
    layout="wide"
)
st.markdown("""
<style>

.stApp {
    background: linear-gradient(to right, #141E30, #243B55);
}

h1,h2,h3,p,label {
    color: white !important;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# Session State
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_id" not in st.session_state:
    st.session_state.chat_id = create_chat()

# ===================================================
# LOGIN / SIGNUP
# ===================================================

if not st.session_state.logged_in:

    st.title("🤖 YM Bot AI Assistant")
    st.caption("Powered by Groq • Fast • Smart • Secure")

    menu = st.sidebar.selectbox(
        "Menu",
        ["Login", "Sign Up"]
    )

    # ---------------- SIGN UP ----------------

    if menu == "Sign Up":

        st.subheader("Create Account")

        username = st.text_input("Username")

        email = st.text_input("Email")

        password = st.text_input(
            "Password",
            type="password"
        )

        if st.button("Create Account"):

            if signup(username, email, password):

                st.success("Account Created Successfully!")

            else:

                st.error("Email already exists!")

    # ---------------- LOGIN ----------------

    elif menu == "Login":

        st.subheader("Login")

        email = st.text_input("Email")

        password = st.text_input(
            "Password",
            type="password"
        )

        if st.button("Login"):

            user = login(email, password)

            if user:

                st.session_state.logged_in = True

                st.session_state.email = email

                st.session_state.username = user[1]

                # Create first chat only if needed
                if "chat_id" not in st.session_state:
                    st.session_state.chat_id = create_chat()

                # Load existing chat
                st.session_state.messages = load_chat(
                    st.session_state.chat_id
                )

                st.rerun()

            else:

                st.error("Invalid Email or Password")

# ===================================================
# CHAT PAGE
# ===================================================

else:

    # ---------------- Sidebar ----------------

    with st.sidebar:

        st.title("🤖 YM Bot")

        st.write(f"👤 {st.session_state.username}")

        st.markdown("---")

        if st.button("➕ New Chat"):

            st.session_state.chat_id = create_chat()

            st.session_state.messages = []

            st.rerun()

        st.markdown("## Chat History")

        chats = get_all_chats(
            st.session_state.email
        )

        for chat in chats:

            chat_id = chat[0]

            if st.button(chat_id[:8]):

                st.session_state.chat_id = chat_id

                st.session_state.messages = load_chat(chat_id)

                st.rerun()

        st.markdown("---")

        if st.button("🚪 Logout"):

            st.session_state.logged_in = False

            st.session_state.messages = []

            st.session_state.chat_id = create_chat()

            st.rerun()

    st.title("🤖 YM Bot")

    st.caption("Your Smart AI Assistant")
          # ---------------------------------
    # Display Previous Messages
    # ---------------------------------

    for message in st.session_state.messages:

        avatar = "👤" if message["role"] == "user" else "🤖"

        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    # ---------------------------------
    # Chat Input
    # ---------------------------------

    prompt = st.chat_input("💬 Ask YM Bot anything...")

    if prompt:

        # -----------------------------
        # Show User Message
        # -----------------------------

        st.session_state.messages.append(
            {
                "role": "user",
                "content": prompt
            }
        )

        save_message(
            st.session_state.chat_id,
            st.session_state.email,
            "user",
            prompt
        )

        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        # -----------------------------
        # Get AI Response
        # -----------------------------

        with st.spinner("🤖 YM Bot is thinking..."):

            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=st.session_state.messages
            )

            reply = response.choices[0].message.content

        # -----------------------------
        # Save AI Response
        # -----------------------------

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": reply
            }
        )

        save_message(
            st.session_state.chat_id,
            st.session_state.email,
            "assistant",
            reply
        )

        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(reply)
