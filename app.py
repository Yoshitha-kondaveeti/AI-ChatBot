import os
import streamlit as st
from dotenv import load_dotenv
from groq import Groq

# ----------------------------
# Load API Key
# ----------------------------
load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# ----------------------------
# Page Configuration
# ----------------------------
st.set_page_config(
    page_title="YM Bot",
    page_icon="🤖",
    layout="wide"
)

# ----------------------------
# Custom CSS
# ----------------------------
st.markdown("""
<style>

.stApp{
    background: linear-gradient(135deg,#0f172a,#1e293b,#0f766e);
}

.main-title{
    text-align:center;
    color:white;
    font-size:55px;
    font-weight:bold;
}

.sub-title{
    text-align:center;
    color:#d1d5db;
    font-size:20px;
}

.stChatMessage{
    border-radius:15px;
    padding:10px;
}

.stButton>button{
    width:100%;
    border-radius:10px;
}

</style>
""", unsafe_allow_html=True)

# ----------------------------
# Sidebar
# ----------------------------

with st.sidebar:

    st.title("🤖 YM Bot")

    st.write("### Your Personal AI Assistant")

    st.markdown("---")

    st.write("### Features")

    st.write("✅ AI Chat")

    st.write("✅ Coding Help")

    st.write("✅ Study Assistant")

    st.write("✅ Resume Help")

    st.write("✅ General Knowledge")

    st.markdown("---")

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")

    st.write("Made with ❤️ by Yoshitha")

# ----------------------------
# Main Heading
# ----------------------------

st.markdown(
"""
<div class='main-title'>
 YM Bot
</div>

<div class='sub-title'>
Your Smart AI Assistant
</div>
""",
unsafe_allow_html=True
)

st.info("""
 Welcome to YM Bot!

You can ask me anything about:

💻 Programming

📚 Studies

🤖 Artificial Intelligence

📝 Resume

🌍 General Knowledge
""")

# ----------------------------
# Chat History
# ----------------------------

if "messages" not in st.session_state:
    st.session_state.messages=[]

for message in st.session_state.messages:

    avatar="👤" if message["role"]=="user" else "🤖"

    with st.chat_message(message["role"],avatar=avatar):

        st.write(message["content"])

# ----------------------------
# Chat Input
# ----------------------------

prompt=st.chat_input(" Message YM Bot...")

if prompt:

    st.session_state.messages.append(
        {
            "role":"user",
            "content":prompt
        }
    )

    with st.chat_message("user",avatar="👤"):

        st.write(prompt)

    with st.spinner(" YM Bot is thinking..."):

        response=client.chat.completions.create(

            model="llama-3.1-8b-instant",

            messages=st.session_state.messages

        )

    reply=response.choices[0].message.content

    st.session_state.messages.append(

        {
            "role":"assistant",
            "content":reply
        }

    )

    with st.chat_message("assistant",avatar="🤖"):

        st.write(reply)

# ----------------------------
# Footer
# ----------------------------

st.markdown("---")

st.markdown(
"""
<center>

YM Bot | done by Yoshitha

</center>
""",
unsafe_allow_html=True
)
