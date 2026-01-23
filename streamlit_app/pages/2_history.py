import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from streamlit_app.utils import (
    init_session_state, is_authenticated, clear_authentication,
    sync_logout, sync_get_tasks, sync_get_task, sync_get_me
)
from streamlit_app.components import render_login_form, render_register_form

st.set_page_config(
    page_title="History - Multi-Agent Task Assistant",
    page_icon="📜",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    /* Hide default Streamlit page navigation */
    [data-testid="stSidebarNav"] { display: none !important; }

    .history-header {
        background: linear-gradient(135deg, #9f7aea 0%, #667eea 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.5rem;
    }

    .task-item {
        background: white;
        padding: 1.25rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
        margin-bottom: 0.75rem;
        border-left: 4px solid;
        transition: transform 0.2s, box-shadow 0.2s;
    }

    .task-item:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.12);
    }

    .task-item.pending { border-left-color: #718096; }
    .task-item.planning { border-left-color: #48bb78; }
    .task-item.executing { border-left-color: #4299e1; }
    .task-item.reviewing { border-left-color: #ed8936; }
    .task-item.completed { border-left-color: #48bb78; }
    .task-item.failed { border-left-color: #e53e3e; }

    .task-objective {
        font-weight: 600;
        color: #2d3748;
        margin-bottom: 0.5rem;
    }

    .task-meta {
        font-size: 0.85rem;
        color: #718096;
    }

    .status-pill {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
    }

    .status-pill.pending { background: #e2e8f0; color: #4a5568; }
    .status-pill.planning { background: #c6f6d5; color: #276749; }
    .status-pill.executing { background: #bee3f8; color: #2b6cb0; }
    .status-pill.reviewing { background: #feebc8; color: #c05621; }
    .status-pill.completed { background: #c6f6d5; color: #276749; }
    .status-pill.failed { background: #fed7d7; color: #c53030; }

    .filter-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
        margin-bottom: 1rem;
    }

    .stats-row {
        display: flex;
        gap: 1rem;
        margin-bottom: 1.5rem;
    }

    .mini-stat {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        flex: 1;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
    }

    .mini-stat-number {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2d3748;
    }

    .mini-stat-label {
        font-size: 0.75rem;
        color: #718096;
        text-transform: uppercase;
    }

    .empty-state {
        text-align: center;
        padding: 3rem;
        color: #718096;
    }

    .empty-state h3 {
        color: #4a5568;
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

                if task.get("plan"):
                    st.markdown("---")
                    st.markdown("**📋 Plan:**")
                    st.markdown(task["plan"][:500] + "..." if len(task.get("plan", "")) > 500 else task.get("plan", ""))

                if task.get("review_result"):
                    st.markdown("---")
                    st.markdown("**✅ Review:**")
                    st.markdown(task["review_result"][:500] + "..." if len(task.get("review_result", "")) > 500 else task.get("review_result", ""))


# Sidebar
with st.sidebar:
    # User avatar section
    if is_authenticated():
        user_result = sync_get_me()
        user = user_result.get("data") if user_result["success"] else None

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

    st.markdown("### 🤖 Task Assistant")
    st.markdown("---")

    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("app.py")

    if st.button("➕ New Task", use_container_width=True):
        st.switch_page("pages/1_dashboard.py")

    st.markdown("---")

    if is_authenticated():
        if st.button("🚪 Logout", use_container_width=True):
            sync_logout()
            clear_authentication()
            st.rerun()

# Main content
if is_authenticated():
    render_history()
else:
    render_auth_required()
