import streamlit as st
from auth import signup, login

st.set_page_config(page_title="YM Bot", page_icon="🤖")

st.title("🤖 YM Bot")

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

    if st.button("Sign Up"):

        if signup(username, email, password):

            st.success("Account created successfully!")

        else:

            st.error("Email already exists.")

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

            st.success("Login Successful!")

        else:

            st.error("Invalid Email or Password")

# ---------------- HOME ----------------

if st.session_state.get("logged_in"):

    st.write(f"## Welcome {st.session_state.username} 👋")

    if st.button("Logout"):

        st.session_state.logged_in = False

        st.rerun()
