import os

import streamlit as st
from dotenv import load_dotenv
from groq import Groq

from auth_utils import login, signup
from chat_db import create_chat, delete_chat, get_chat_summaries, load_chat, save_message


load_dotenv()


def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    return Groq(api_key=api_key)


client = get_groq_client()


st.set_page_config(
    page_title="YM Bot",
    page_icon="YM",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root {
        --page: #09111f;
        --panel: #101827;
        --panel-soft: #172033;
        --line: #273449;
        --text: #eef3fb;
        --muted: #9ca8bb;
        --brand: #38bdf8;
        --brand-strong: #2563eb;
        --good: #22c55e;
        --danger: #ef4444;
    }

    .stApp {
        color: var(--text);
        background:
            radial-gradient(circle at top left, rgba(56, 189, 248, 0.15), transparent 34rem),
            linear-gradient(135deg, #09111f 0%, #111827 48%, #182033 100%);
    }

    .block-container {
        max-width: 1160px;
        padding-top: 2.2rem;
        padding-bottom: 6rem;
    }

    section[data-testid="stSidebar"] {
        background: #0b1220;
        border-right: 1px solid var(--line);
    }

    section[data-testid="stSidebar"] .block-container {
        padding-top: 1.4rem;
    }

    h1, h2, h3, label, p, span {
        color: inherit;
    }

    [data-testid="stMarkdownContainer"] p {
        color: var(--muted);
    }

    .ym-shell {
        border: 1px solid var(--line);
        border-radius: 8px;
        background: rgba(16, 24, 39, 0.82);
        padding: 1.5rem;
    }

    .ym-auth-hero {
        min-height: 72vh;
        display: flex;
        align-items: center;
    }

    .ym-kicker {
        color: var(--brand);
        font-weight: 700;
        letter-spacing: 0;
        margin-bottom: .6rem;
    }

    .ym-title {
        font-size: 2.7rem;
        line-height: 1.05;
        font-weight: 800;
        color: white;
        margin-bottom: .8rem;
    }

    .ym-copy {
        color: var(--muted);
        font-size: 1rem;
        line-height: 1.65;
        max-width: 34rem;
    }

    .ym-stat-row {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: .75rem;
        margin-top: 1.4rem;
    }

    .ym-stat {
        border: 1px solid var(--line);
        border-radius: 8px;
        background: rgba(23, 32, 51, .78);
        padding: .85rem;
    }

    .ym-stat strong {
        display: block;
        color: white;
        font-size: 1.25rem;
    }

    .ym-stat span {
        color: var(--muted);
        font-size: .82rem;
    }

    .ym-user {
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: .9rem;
        background: var(--panel);
        margin-bottom: .9rem;
    }

    .ym-user strong {
        color: white;
        display: block;
    }

    .ym-user span {
        color: var(--muted);
        font-size: .82rem;
    }

    .ym-empty {
        border: 1px solid var(--line);
        border-radius: 8px;
        background: rgba(16, 24, 39, 0.72);
        padding: 1.2rem;
        margin: 1.2rem 0;
    }

    .ym-empty h3 {
        margin-top: 0;
        color: white;
    }

    div[data-testid="stChatMessage"] {
        border: 1px solid var(--line);
        border-radius: 8px;
        background: rgba(16, 24, 39, .74);
        padding: .7rem;
        margin-bottom: .75rem;
    }

    .stButton > button {
        width: 100%;
        border-radius: 8px;
        border: 1px solid var(--line);
        background: var(--panel-soft);
        color: white;
        min-height: 2.55rem;
        transition: border-color .15s ease, background .15s ease;
    }

    .stButton > button:hover {
        border-color: var(--brand);
        background: #1d2a42;
        color: white;
    }

    .stTextInput input, .stTextArea textarea {
        border-radius: 8px;
    }

    div[data-testid="stTabs"] button {
        color: var(--muted);
    }

    div[data-testid="stTabs"] button[aria-selected="true"] {
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
        "draft_prompt": "",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def short_title(text, limit=46):
    clean = " ".join((text or "New chat").split())
    if len(clean) <= limit:
        return clean
    return clean[: limit - 3] + "..."


def start_new_chat():
    st.session_state.chat_id = create_chat()
    st.session_state.messages = []
    st.session_state.draft_prompt = ""


def logout():
    st.session_state.logged_in = False
    st.session_state.email = ""
    st.session_state.username = ""
    start_new_chat()


def use_prompt_template(text):
    st.session_state.draft_prompt = text


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
            temperature=0.7,
        )
        reply = response.choices[0].message.content
    except Exception as exc:
        reply = f"Sorry, I could not get a response right now. Error: {exc}"

    st.session_state.messages.append({"role": "assistant", "content": reply})
    save_message(st.session_state.chat_id, st.session_state.email, "assistant", reply)
    st.session_state.draft_prompt = ""


def render_auth_page():
    left, right = st.columns([1.1, .9], gap="large")

    with left:
        st.markdown(
            """
            <div class="ym-auth-hero">
                <div>
                    <div class="ym-kicker">YM BOT</div>
                    <div class="ym-title">A cleaner workspace for fast AI chats.</div>
                    <div class="ym-copy">
                        Sign in to keep your conversations, search old chats from the sidebar,
                        and start focused prompts for code, study, resumes, and daily work.
                    </div>
                    <div class="ym-stat-row">
                        <div class="ym-stat"><strong>Fast</strong><span>Groq responses</span></div>
                        <div class="ym-stat"><strong>Saved</strong><span>Chat history</span></div>
                        <div class="ym-stat"><strong>Simple</strong><span>Email login</span></div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown('<div class="ym-shell">', unsafe_allow_html=True)
        st.subheader("Welcome")
        login_tab, signup_tab = st.tabs(["Login", "Create account"])

        with login_tab:
            email = st.text_input("Email", key="login_email").strip().lower()
            password = st.text_input("Password", type="password", key="login_password")

            if st.button("Login", type="primary"):
                user = login(email, password)

                if user:
                    st.session_state.logged_in = True
                    st.session_state.email = email
                    st.session_state.username = user[1]
                    start_new_chat()
                    st.rerun()

                st.error("Invalid email or password.")

        with signup_tab:
            username = st.text_input("Username", key="signup_username").strip()
            email = st.text_input("Email", key="signup_email").strip().lower()
            password = st.text_input("Password", type="password", key="signup_password")

            if st.button("Create account"):
                if not username or not email or not password:
                    st.error("Please fill in username, email, and password.")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters.")
                elif signup(username, email, password):
                    st.success("Account created. Use the Login tab to continue.")
                else:
                    st.error("That email is already registered.")

        st.markdown("</div>", unsafe_allow_html=True)


def render_sidebar():
    st.sidebar.title("YM Bot")
    st.sidebar.markdown(
        f"""
        <div class="ym-user">
            <strong>{st.session_state.username}</strong>
            <span>{st.session_state.email}</span><br>
            <span>Status: Online</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.sidebar.button("New chat", type="primary"):
        start_new_chat()
        st.rerun()

    st.sidebar.divider()
    st.sidebar.markdown("### Chat history")

    search = st.sidebar.text_input("Search chats", placeholder="Search by message text")
    chats = get_chat_summaries(st.session_state.email)

    if search:
        query = search.casefold()
        chats = [chat for chat in chats if query in (chat[1] or "").casefold()]

    if not chats:
        st.sidebar.caption("No matching chats yet.")

    for chat_id, title, message_count, updated_at in chats:
        is_current = chat_id == st.session_state.chat_id
        label = short_title(title)
        if is_current:
            label = f"> {label}"

        col1, col2 = st.sidebar.columns([5, 1])
        with col1:
            if st.button(label, key=f"open-{chat_id}", help=f"{message_count} messages"):
                st.session_state.chat_id = chat_id
                st.session_state.messages = load_chat(chat_id)
                st.session_state.draft_prompt = ""
                st.rerun()

            st.caption(f"{message_count} messages | {updated_at or 'just now'}")

        with col2:
            if st.button("X", key=f"delete-{chat_id}", help="Delete chat"):
                delete_chat(chat_id)
                if st.session_state.chat_id == chat_id:
                    start_new_chat()
                st.rerun()

    st.sidebar.divider()

    if st.sidebar.button("Logout"):
        logout()
        st.rerun()


def render_prompt_starters():
    st.markdown(
        """
        <div class="ym-empty">
            <h3>Start with a useful prompt</h3>
            <p>Pick a starter, edit it, or type your own message below.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    starters = [
        ("Code helper", "Review this code and explain the bug clearly: "),
        ("Study guide", "Teach me this topic step by step with examples: "),
        ("Resume", "Improve this resume bullet and make it stronger: "),
        ("Plan", "Create a simple action plan for: "),
    ]

    cols = st.columns(4)
    for index, (label, prompt) in enumerate(starters):
        with cols[index]:
            if st.button(label):
                use_prompt_template(prompt)
                st.rerun()


def render_chat_page():
    render_sidebar()

    top_left, top_right = st.columns([.72, .28], gap="large")
    with top_left:
        st.title("YM Bot")
        st.caption("Ask, save, search, and continue your AI conversations.")

    with top_right:
        if st.button("Clear current draft"):
            st.session_state.draft_prompt = ""
            st.rerun()

    for message in st.session_state.messages:
        avatar = "user" if message["role"] == "user" else "assistant"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    if not st.session_state.messages:
        render_prompt_starters()

    draft = st.text_area(
        "Message",
        value=st.session_state.draft_prompt,
        placeholder="Ask YM Bot anything...",
        height=110,
    )

    col1, col2 = st.columns([.78, .22])
    with col1:
        st.caption("Tip: use the sidebar search to find old conversations by their first message.")

    with col2:
        if st.button("Send", type="primary"):
            prompt = draft.strip()
            if prompt:
                with st.spinner("YM Bot is thinking..."):
                    send_prompt(prompt)
                st.rerun()
            else:
                st.warning("Please type a message first.")

    prompt = st.chat_input("Quick message")
    if prompt:
        with st.spinner("YM Bot is thinking..."):
            send_prompt(prompt)
        st.rerun()


init_session_state()

if st.session_state.logged_in:
    render_chat_page()
else:
    render_auth_page()
