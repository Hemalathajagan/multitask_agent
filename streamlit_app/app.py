import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from streamlit_app.utils import (
    init_session_state, is_authenticated, clear_authentication,
    sync_logout, sync_get_tasks, sync_get_me
)
from streamlit_app.components import render_login_form, render_register_form, get_avatar_html

# Initialize session state first to check auth
from streamlit_app.utils import init_session_state as _init
_init()

# Check if authenticated for sidebar state
_is_auth = st.session_state.get("authenticated", False) and st.session_state.get("token") is not None

# Page config - hide sidebar on login page
st.set_page_config(
    page_title="Multi-Agent Task Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded" if _is_auth else "collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main container styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }

    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
    }

    .main-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }

    /* Stats cards */
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
        border-left: 4px solid;
    }

    .stat-card.purple { border-left-color: #667eea; }
    .stat-card.green { border-left-color: #48bb78; }
    .stat-card.orange { border-left-color: #ed8936; }
    .stat-card.blue { border-left-color: #4299e1; }

    .stat-number {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2d3748;
    }

    .stat-label {
        color: #718096;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Feature cards */
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        height: 100%;
    }

    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }

    .feature-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #2d3748;
        margin-bottom: 0.5rem;
    }

    .feature-desc {
        color: #718096;
        font-size: 0.9rem;
    }

    /* Sidebar styling */
    .sidebar-header {
        text-align: center;
        padding: 1rem 0;
        border-bottom: 1px solid #e2e8f0;
        margin-bottom: 1rem;
    }

    /* Auth form styling */
    .auth-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        background: white;
        border-radius: 15px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
    }

    /* Button styling */
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
init_session_state()


def render_auth_page():
    """Render the authentication page."""
    # Hide sidebar completely on auth page
    st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none; }
        [data-testid="stSidebarNav"] { display: none; }
        [data-testid="collapsedControl"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="main-header">
        <h1>🤖 Multi-Agent Task Assistant</h1>
        <p>Powered by AI agents that plan, execute, and review your tasks</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

        with tab1:
            render_login_form()

        with tab2:
            render_register_form()

        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #718096; font-size: 0.85rem;">
            <p><strong>How it works:</strong></p>
            <p>📋 Planner Agent → ⚡ Executor Agent → ✅ Reviewer Agent</p>
        </div>
        """, unsafe_allow_html=True)


def render_home():
    """Render the home page with stats and overview."""
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 Multi-Agent Task Assistant</h1>
        <p>Your AI-powered team for planning, executing, and reviewing tasks</p>
    </div>
    """, unsafe_allow_html=True)

    # Get tasks for stats
    result = sync_get_tasks(limit=100)
    tasks = result.get("data", []) if result["success"] else []

    # Calculate stats
    total_tasks = len(tasks)
    completed = len([t for t in tasks if t["status"] == "completed"])
    in_progress = len([t for t in tasks if t["status"] in ["planning", "executing", "reviewing"]])
    pending = len([t for t in tasks if t["status"] == "pending"])

    # Stats row
    st.subheader("📊 Your Statistics")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="stat-card purple">
            <div class="stat-number">{total_tasks}</div>
            <div class="stat-label">Total Tasks</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="stat-card green">
            <div class="stat-number">{completed}</div>
            <div class="stat-label">Completed</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="stat-card orange">
            <div class="stat-number">{in_progress}</div>
            <div class="stat-label">In Progress</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="stat-card blue">
            <div class="stat-number">{pending}</div>
            <div class="stat-label">Pending</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Quick actions
    st.subheader("🚀 Quick Actions")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("➕ Create New Task", use_container_width=True, type="primary"):
            st.switch_page("pages/1_dashboard.py")

    with col2:
        if st.button("📜 View Task History", use_container_width=True):
            st.switch_page("pages/2_history.py")

    # Recent activity
    if tasks:
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("🕐 Recent Activity")

        for task in tasks[:3]:
            status_emoji = {
                "pending": "⏳",
                "planning": "📋",
                "executing": "⚡",
                "reviewing": "🔍",
                "completed": "✅",
                "failed": "❌"
            }.get(task["status"], "❓")

            status_color = {
                "pending": "#718096",
                "planning": "#667eea",
                "executing": "#4299e1",
                "reviewing": "#ed8936",
                "completed": "#48bb78",
                "failed": "#e53e3e"
            }.get(task["status"], "#718096")

            st.markdown(f"""
            <div style="
                background: white;
                padding: 1rem;
                border-radius: 8px;
                margin-bottom: 0.5rem;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                border-left: 3px solid {status_color};
            ">
                <strong style="color: #1a202c; font-size: 1rem;">{status_emoji} {task['objective'][:60]}{'...' if len(task['objective']) > 60 else ''}</strong>
                <br>
                <small style="color: #718096;">Status: {task['status'].title()}</small>
            </div>
            """, unsafe_allow_html=True)


def render_main_app():
    """Render the main application."""
    # Get user info for avatar
    user_result = sync_get_me()
    user = user_result.get("data") if user_result["success"] else None

    # Sidebar
    with st.sidebar:
        # User avatar section at top
        if user:
            username = user.get("username", "User")
            first_letter = username[0].upper()
            profile_photo = user.get("profile_photo")

            if profile_photo:
                avatar_html = f'<img src="data:image/png;base64,{profile_photo}" style="width:50px;height:50px;border-radius:50%;object-fit:cover;">'
            else:
                avatar_html = f'''
                <div style="
                    width:50px;height:50px;border-radius:50%;
                    background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    display:flex;align-items:center;justify-content:center;
                    color:white;font-weight:bold;font-size:1.5rem;
                ">{first_letter}</div>
                '''

            st.markdown(f"""
            <div style="text-align:center;padding:1rem 0;border-bottom:1px solid #e2e8f0;margin-bottom:1rem;">
                <div style="display:flex;justify-content:center;margin-bottom:0.5rem;">
                    {avatar_html}
                </div>
                <div style="font-weight:600;color:#2d3748;">{username}</div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("👤 View Profile", use_container_width=True, key="avatar_profile_btn"):
                st.switch_page("pages/3_profile.py")

        st.markdown("### Navigation")

        if st.button("🏠 Home", use_container_width=True):
            st.session_state.current_page = "home"
            st.rerun()

        if st.button("➕ New Task", use_container_width=True):
            st.switch_page("pages/1_dashboard.py")

        if st.button("📜 History", use_container_width=True):
            st.switch_page("pages/2_history.py")

        if st.button("📖 How It Works", use_container_width=True):
            st.switch_page("pages/4_how_it_works.py")

        st.markdown("---")

        if st.button("🚪 Logout", use_container_width=True):
            sync_logout()
            clear_authentication()
            st.rerun()

    # Main content
    render_home()


# Main app logic
if is_authenticated():
    render_main_app()
else:
    render_auth_page()
