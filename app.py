import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from auth_utils import login_user, signup_user
from chat_db import (
    create_chat,
    save_message,
    load_chat,
    get_all_chats,
    delete_chat,
)

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="AI Chat", page_icon="💬", layout="wide")


# ---------- Session state ----------
defaults = {
    "logged_in": False,
    "user_email": None,
    "username": None,
    "current_chat_id": None,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ---------- Auth screen ----------
def auth_screen():
    st.title("💬 Welcome")

    tab_login, tab_signup = st.tabs(["Log in", "Sign up"])

    with tab_login:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Log in")

            if submitted:
                if not email or not password:
                    st.error("Please enter your email and password.")
                else:
                    success, result = login_user(email, password)
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.user_email = email
                        st.session_state.username = result
                        st.rerun()
                    else:
                        st.error(result)

    with tab_signup:
        with st.form("signup_form"):
            username = st.text_input("Username")
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Password", type="password", key="signup_password")
            confirm = st.text_input("Confirm password", type="password", key="signup_confirm")
            submitted = st.form_submit_button("Sign up")

            if submitted:
                if not username or not email or not password:
                    st.error("Please fill in all fields.")
                elif password != confirm:
                    st.error("Passwords do not match.")
                else:
                    success, message = signup_user(username, email, password)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)


# ---------- Chat screen ----------
def chat_screen():
    with st.sidebar:
        st.title(f"Hi, {st.session_state.username} 👋")

        if st.button("➕ New chat", use_container_width=True):
            st.session_state.current_chat_id = create_chat()
            st.rerun()

        st.divider()
        st.subheader("Your chats")

        chats = get_all_chats(st.session_state.user_email)

        if not chats:
            st.caption("No chats yet. Start a new one!")

        for (chat_id,) in chats:
            col1, col2 = st.columns([4, 1])
            is_current = chat_id == st.session_state.current_chat_id
            label = ("🟢 " if is_current else "") + chat_id[:8]

            with col1:
                if st.button(label, key=f"select_{chat_id}", use_container_width=True):
                    st.session_state.current_chat_id = chat_id
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"delete_{chat_id}"):
                    delete_chat(chat_id)
                    if st.session_state.current_chat_id == chat_id:
                        st.session_state.current_chat_id = None
                    st.rerun()

        st.divider()
        if st.button("Log out", use_container_width=True):
            for key, value in defaults.items():
                st.session_state[key] = value
            st.rerun()

    st.title("💬 AI Chat")

    if not os.getenv("OPENAI_API_KEY"):
        st.warning(
            "No OPENAI_API_KEY found. Add it to a .env file in the project "
            "root to enable AI responses."
        )

    if st.session_state.current_chat_id is None:
        st.session_state.current_chat_id = create_chat()

    chat_id = st.session_state.current_chat_id
    messages = load_chat(chat_id)

    for msg in messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Type your message...")

    if prompt:
        save_message(chat_id, st.session_state.user_email, "user", prompt)
        with st.chat_message("user"):
            st.markdown(prompt)

        history = load_chat(chat_id)

        with st.chat_message("assistant"):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=history,
                )
                reply = response.choices[0].message.content
            except Exception as e:
                reply = f"Sorry, something went wrong while contacting the AI: {e}"

            st.markdown(reply)

        save_message(chat_id, st.session_state.user_email, "assistant", reply)


# ---------- Main ----------
if st.session_state.logged_in:
    chat_screen()
else:
    auth_screen()
