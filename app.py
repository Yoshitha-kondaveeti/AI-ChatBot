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
