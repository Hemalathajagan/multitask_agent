import streamlit as st
from typing import Optional


def init_session_state():
    """Initialize session state variables."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user" not in st.session_state:
        st.session_state.user = None
    if "token" not in st.session_state:
        st.session_state.token = None
    if "current_task_id" not in st.session_state:
        st.session_state.current_task_id = None
    if "messages" not in st.session_state:
        st.session_state.messages = []


def is_authenticated() -> bool:
    """Check if user is authenticated."""
    return st.session_state.get("authenticated", False) and st.session_state.get("token") is not None


def set_authenticated(user: dict, token: str):
    """Set authenticated state."""
    st.session_state.authenticated = True
    st.session_state.user = user
    st.session_state.token = token


def clear_authentication():
    """Clear authentication state."""
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.token = None
    st.session_state.current_task_id = None
    st.session_state.messages = []


def get_current_user() -> Optional[dict]:
    """Get current user information."""
    return st.session_state.get("user")


def get_token() -> Optional[str]:
    """Get current JWT token."""
    return st.session_state.get("token")
