import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from streamlit_app.utils import (
    init_session_state, is_authenticated,
    sync_get_tasks
)
from streamlit_app.components import render_login_form, render_register_form, render_sidebar

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
    /* Hide default Streamlit page navigation */
    [data-testid="stSidebarNav"] { display: none !important; }

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

    /* Sidebar nav button styling */
    .nav-link {
        display: block;
        padding: 0.6rem 1rem;
        margin: 0.25rem 0;
        border-radius: 8px;
        color: #4a5568;
        text-decoration: none;
        transition: all 0.2s;
    }
    .nav-link:hover {
        background: #f7fafc;
        color: #667eea;
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
    # Render shared sidebar
    render_sidebar(current_page="home")

    # Main content
    render_home()


# Main app logic
if is_authenticated():
    render_main_app()
else:
    render_auth_page()
