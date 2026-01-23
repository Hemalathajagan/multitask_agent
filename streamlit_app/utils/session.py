import streamlit as st
from typing import Optional
import streamlit.components.v1 as components


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
    if "token_checked" not in st.session_state:
        st.session_state.token_checked = False


def is_authenticated() -> bool:
    """Check if user is authenticated."""
    return st.session_state.get("authenticated", False) and st.session_state.get("token") is not None


def set_authenticated(user: dict, token: str):
    """Set authenticated state and store token."""
    st.session_state.authenticated = True
    st.session_state.user = user
    st.session_state.token = token
    # Store token in localStorage via JavaScript
    store_token_js(token)


def clear_authentication():
    """Clear authentication state and remove stored token."""
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.token = None
    st.session_state.current_task_id = None
    st.session_state.messages = []
    # Clear token from localStorage
    clear_token_js()


def get_current_user() -> Optional[dict]:
    """Get current user information."""
    return st.session_state.get("user")


def get_token() -> Optional[str]:
    """Get current JWT token."""
    return st.session_state.get("token")


def store_token_js(token: str):
    """Store token in browser localStorage."""
    js_code = f"""
    <script>
        localStorage.setItem('auth_token', '{token}');
    </script>
    """
    components.html(js_code, height=0)


def clear_token_js():
    """Clear token from browser localStorage."""
    js_code = """
    <script>
        localStorage.removeItem('auth_token');
    </script>
    """
    components.html(js_code, height=0)


def inject_auto_refresh(interval_seconds: int = 3):
    """Inject JavaScript for auto-refresh without full page reload."""
    js_code = f"""
    <script>
        // Auto-refresh by clicking Streamlit's rerun
        function triggerRerun() {{
            // Find and click any element that triggers rerun
            const refreshBtn = window.parent.document.querySelector('[data-testid="stButton"] button');
            if (refreshBtn && refreshBtn.textContent.includes('Refresh')) {{
                refreshBtn.click();
            }} else {{
                // Alternative: dispatch a custom event
                window.parent.postMessage({{type: 'streamlit:rerun'}}, '*');
            }}
        }}

        // Set interval for auto-refresh
        if (!window.autoRefreshInterval) {{
            window.autoRefreshInterval = setInterval(triggerRerun, {interval_seconds * 1000});
        }}
    </script>
    """
    components.html(js_code, height=0)


def stop_auto_refresh():
    """Stop auto-refresh."""
    js_code = """
    <script>
        if (window.autoRefreshInterval) {
            clearInterval(window.autoRefreshInterval);
            window.autoRefreshInterval = null;
        }
    </script>
    """
    components.html(js_code, height=0)
