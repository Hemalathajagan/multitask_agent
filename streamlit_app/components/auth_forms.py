import streamlit as st
from streamlit_app.utils import sync_login, sync_register, set_authenticated


def render_login_form():
    """Render the login form."""
    st.subheader("Login")

    with st.form("login_form"):
        email = st.text_input("Email", placeholder="your@email.com")
        password = st.text_input("Password", type="password", placeholder="Your password")
        submitted = st.form_submit_button("Login", use_container_width=True)

        if submitted:
            if not email or not password:
                st.error("Please fill in all fields")
                return

            with st.spinner("Logging in..."):
                result = sync_login(email, password)

            if result["success"]:
                set_authenticated({"email": email}, result["data"]["access_token"])
                st.success("Login successful!")
                st.rerun()
            else:
                st.error(result["error"])


def render_register_form():
    """Render the registration form."""
    st.subheader("Register")

    with st.form("register_form"):
        email = st.text_input("Email", placeholder="your@email.com")
        username = st.text_input("Username", placeholder="Choose a username")
        password = st.text_input("Password", type="password", placeholder="Min 8 characters")
        confirm_password = st.text_input("Confirm Password", type="password")
        submitted = st.form_submit_button("Register", use_container_width=True)

        if submitted:
            if not email or not username or not password:
                st.error("Please fill in all fields")
                return

            if password != confirm_password:
                st.error("Passwords do not match")
                return

            if len(password) < 8:
                st.error("Password must be at least 8 characters")
                return

            with st.spinner("Creating account..."):
                result = sync_register(email, username, password)

            if result["success"]:
                st.success("Account created! Please login.")
            else:
                st.error(result["error"])
