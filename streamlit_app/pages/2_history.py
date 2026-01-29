import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from streamlit_app.utils import (
    init_session_state, is_authenticated,
    sync_get_tasks, sync_get_task
)
from streamlit_app.components import render_login_form, render_register_form, render_sidebar

st.set_page_config(
    page_title="History - Multi-Agent Task Assistant",
    page_icon="📜",
    layout="wide"
)

# Professional CSS - Warm Orange Theme
st.markdown("""
<style>
    /* ============================================
       RESET & BASE STYLES - WARM ORANGE THEME
       ============================================ */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* Hide Streamlit defaults but keep sidebar toggle */
    [data-testid="stSidebarNav"] { display: none !important; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    [data-testid="stToolbar"] { visibility: hidden; }
    header[data-testid="stHeader"] {
        background: transparent !important;
        height: 0 !important;
        min-height: 0 !important;
    }

    /* Hide sidebar collapse/expand buttons */
    [data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebar"] button[kind="header"],
    [data-testid="collapsedControl"] {
        display: none !important;
    }

    /* Base font */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    .stApp {
        background: linear-gradient(180deg, #fffbf5 0%, #fef7ed 100%);
    }

    /* ============================================
       HISTORY HEADER - WARM AMBER
       ============================================ */
    .history-header {
        background: linear-gradient(135deg, #d97706 0%, #f59e0b 50%, #fbbf24 100%);
        padding: 2.5rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
        box-shadow:
            0 20px 40px rgba(217, 119, 6, 0.3),
            0 0 0 1px rgba(255, 255, 255, 0.1) inset;
    }

    .history-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 60%;
        height: 200%;
        background: radial-gradient(ellipse, rgba(255,255,255,0.15) 0%, transparent 70%);
        pointer-events: none;
    }

    .history-header h2 {
        margin: 0 0 0.5rem 0;
        font-size: 1.75rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        position: relative;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .history-header p {
        margin: 0;
        opacity: 0.95;
        position: relative;
    }

    /* ============================================
       TASK ITEMS
       ============================================ */
    .task-item {
        background: white;
        padding: 1.25rem;
        border-radius: 14px;
        border: 1px solid rgba(234, 88, 12, 0.08);
        margin-bottom: 0.75rem;
        border-left: 4px solid;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }

    .task-item:hover {
        transform: translateX(6px);
        box-shadow: 0 4px 12px rgba(234, 88, 12, 0.12);
    }

    .task-item.pending { border-left-color: #a8a29e; }
    .task-item.planning { border-left-color: #f97316; }
    .task-item.executing { border-left-color: #f59e0b; }
    .task-item.reviewing { border-left-color: #ef4444; }
    .task-item.completed { border-left-color: #22c55e; }
    .task-item.failed { border-left-color: #dc2626; }

    .task-objective {
        font-weight: 600;
        color: #1c1917;
        margin-bottom: 0.5rem;
        font-size: 0.95rem;
        letter-spacing: -0.01em;
    }

    .task-meta {
        font-size: 0.8rem;
        color: #78716c;
    }

    /* ============================================
       STATUS PILLS
       ============================================ */
    .status-pill {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .status-pill.pending { background: #e7e5e4; color: #57534e; }
    .status-pill.planning { background: #fed7aa; color: #c2410c; }
    .status-pill.executing { background: #fde68a; color: #b45309; }
    .status-pill.reviewing { background: #fecaca; color: #b91c1c; }
    .status-pill.completed { background: #bbf7d0; color: #166534; }
    .status-pill.failed { background: #fecaca; color: #b91c1c; }

    /* ============================================
       EMPTY STATE
       ============================================ */
    .empty-state {
        text-align: center;
        padding: 4rem 2rem;
        background: white;
        border-radius: 20px;
        border: 2px dashed #fed7aa;
    }

    .empty-state h3 {
        color: #292524;
        margin: 1rem 0 0.5rem 0;
        font-size: 1.25rem;
        font-weight: 700;
        letter-spacing: -0.02em;
    }

    .empty-state p {
        color: #78716c;
        margin: 0;
        font-size: 0.95rem;
    }

    /* ============================================
       BUTTON OVERRIDES - ORANGE THEME
       ============================================ */
    .stButton > button {
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 0.75rem 1.5rem !important;
        transition: all 0.2s ease !important;
        letter-spacing: -0.01em !important;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
        border: none !important;
        color: white !important;
        box-shadow: 0 4px 14px rgba(245, 158, 11, 0.4) !important;
    }

    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(245, 158, 11, 0.5) !important;
    }

    .stButton > button[kind="secondary"] {
        background: #fafaf9 !important;
        color: #57534e !important;
        border: 1px solid #e7e5e4 !important;
    }

    /* ============================================
       INPUT OVERRIDES
       ============================================ */
    .stTextInput > div > div > input {
        border-radius: 12px !important;
        border: 2px solid #fed7aa !important;
        padding: 0.875rem 1rem !important;
        transition: all 0.2s ease !important;
        background-color: #fffbf5 !important;
        color: #1c1917 !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: #f59e0b !important;
        box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.15) !important;
        background-color: #ffffff !important;
    }

    .stTextInput > div > div > input::placeholder {
        color: #a8a29e !important;
    }

    .stMultiSelect > div > div {
        border-radius: 12px !important;
        background-color: #fffbf5 !important;
        border: 2px solid #fed7aa !important;
        color: #1c1917 !important;
    }

    /* Labels */
    .stTextInput > label,
    .stSelectbox > label,
    .stMultiSelect > label {
        color: #1c1917 !important;
    }

    /* All text elements */
    p, span, div {
        color: #1c1917;
    }

    .stMarkdown, .stMarkdown p {
        color: #1c1917 !important;
    }

    /* Metric values */
    [data-testid="stMetricValue"] {
        color: #1c1917 !important;
    }

    [data-testid="stMetricLabel"] {
        color: #57534e !important;
    }

    [data-testid="stMetricDelta"] {
        color: #16a34a !important;
    }

    /* Select boxes */
    .stSelectbox > div > div {
        background-color: #fffbf5 !important;
        border: 2px solid #fed7aa !important;
        border-radius: 12px !important;
        color: #1c1917 !important;
    }

    /* Expander */
    .streamlit-expanderHeader {
        color: #1c1917 !important;
        background-color: #fff7ed !important;
    }

    .streamlit-expanderContent {
        color: #1c1917 !important;
    }

    /* Progress bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #f59e0b, #d97706) !important;
    }

    /* Links */
    a {
        color: #ea580c !important;
    }

    /* Selectbox */
    [data-baseweb="select"] > div {
        background-color: #fffbf5 !important;
        border-color: #fed7aa !important;
        border-radius: 12px !important;
    }

    [data-baseweb="popover"],
    [data-baseweb="menu"] {
        background-color: #fffbf5 !important;
    }

    [data-baseweb="menu"] li {
        color: #1c1917 !important;
    }

    [data-baseweb="menu"] li:hover {
        background-color: #fff7ed !important;
    }
</style>
""", unsafe_allow_html=True)

init_session_state()


def render_auth_required():
    """Show login required message."""
    st.warning("Please login to view task history.")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["Login", "Register"])
        with tab1:
            render_login_form()
        with tab2:
            render_register_form()


def render_history():
    """Render the task history page."""
    # Header
    st.markdown("""
    <div class="history-header">
        <h2>📜 Task History</h2>
        <p>View and manage all your past tasks</p>
    </div>
    """, unsafe_allow_html=True)

    # Get all tasks
    result = sync_get_tasks(limit=100)
    tasks = result.get("data", []) if result["success"] else []

    if not tasks:
        st.markdown("""
        <div class="empty-state">
            <h3>📭 No tasks yet</h3>
            <p>Create your first task from the Dashboard to get started!</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("➕ Create Your First Task", type="primary"):
            st.switch_page("pages/1_dashboard.py")
        return

    # Stats row
    total = len(tasks)
    completed = len([t for t in tasks if t["status"] == "completed"])
    failed = len([t for t in tasks if t["status"] == "failed"])
    in_progress = len([t for t in tasks if t["status"] in ["planning", "executing", "reviewing"]])

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Tasks", total)
    with col2:
        st.metric("Completed", completed, delta=f"{int(completed/total*100)}%" if total > 0 else "0%")
    with col3:
        st.metric("In Progress", in_progress)
    with col4:
        st.metric("Failed", failed)

    st.markdown("---")

    # Filters
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        search = st.text_input("🔍 Search tasks", placeholder="Search by objective...")

    with col2:
        status_filter = st.multiselect(
            "Filter by status",
            ["pending", "planning", "executing", "reviewing", "completed", "failed"],
            default=[]
        )

    with col3:
        sort_order = st.selectbox("Sort by", ["Newest", "Oldest"])

    # Filter tasks
    filtered_tasks = tasks

    if search:
        filtered_tasks = [t for t in filtered_tasks if search.lower() in t["objective"].lower()]

    if status_filter:
        filtered_tasks = [t for t in filtered_tasks if t["status"] in status_filter]

    if sort_order == "Oldest":
        filtered_tasks = list(reversed(filtered_tasks))

    st.markdown(f"**Showing {len(filtered_tasks)} of {total} tasks**")
    st.markdown("")

    # Task list
    for task in filtered_tasks:
        status = task["status"]
        status_emoji = {
            "pending": "⏳",
            "planning": "📋",
            "executing": "⚡",
            "reviewing": "🔍",
            "completed": "✅",
            "failed": "❌"
        }.get(status, "❓")

        col1, col2 = st.columns([5, 1])

        with col1:
            st.markdown(f"""
            <div class="task-item {status}">
                <div class="task-objective">{status_emoji} {task['objective']}</div>
                <div class="task-meta">
                    <span class="status-pill {status}">{status}</span>
                    &nbsp;&bull;&nbsp;
                    Task #{task['id']}
                    &nbsp;&bull;&nbsp;
                    {task['created_at'][:10] if task.get('created_at') else 'N/A'}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            if st.button("View", key=f"view_{task['id']}", use_container_width=True):
                st.session_state.current_task_id = task["id"]
                st.switch_page("pages/1_dashboard.py")

    # Show selected task details in expander
    if st.session_state.get("selected_history_task"):
        task_id = st.session_state.selected_history_task
        result = sync_get_task(task_id)

        if result["success"]:
            task = result["data"]
            with st.expander(f"📌 Task #{task['id']} Details", expanded=True):
                st.markdown(f"**Objective:** {task['objective']}")
                st.markdown(f"**Status:** {task['status'].title()}")

                if task["status"] == "completed":
                    st.markdown("---")
                    st.markdown("**✅ Summary:**")
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
                        border: 1px solid #bbf7d0;
                        border-radius: 10px;
                        padding: 1rem;
                        color: #1c1917;
                        font-size: 0.9rem;
                    ">
                        Task completed successfully. Click "View" to see full results in the dashboard.
                    </div>
                    """, unsafe_allow_html=True)
                elif task.get("plan"):
                    st.markdown("---")
                    st.markdown("**📋 Plan Preview:**")
                    # Show only first 300 chars of plan
                    plan_preview = task["plan"][:300] + "..." if len(task.get("plan", "")) > 300 else task.get("plan", "")
                    st.markdown(plan_preview)


# Render shared sidebar
if is_authenticated():
    render_sidebar(current_page="history")

# Main content
if is_authenticated():
    render_history()
else:
    render_auth_required()
