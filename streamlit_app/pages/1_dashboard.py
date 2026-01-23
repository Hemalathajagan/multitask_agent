import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from streamlit_app.utils import (
    init_session_state, is_authenticated, clear_authentication,
    sync_logout, sync_get_task, sync_get_tasks, sync_create_task, sync_get_me
)
from streamlit_app.components import render_login_form, render_register_form

st.set_page_config(
    page_title="Dashboard - Multi-Agent Task Assistant",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .dashboard-header {
        background: linear-gradient(135deg, #4299e1 0%, #667eea 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.5rem;
    }

    .task-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }

    .agent-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        border-left: 4px solid;
        color: #1a202c !important;
    }

    .agent-message strong {
        color: #2d3748 !important;
    }

    .agent-message div {
        color: #1a202c !important;
    }

    .agent-planner { border-left-color: #48bb78; background: #f0fff4 !important; }
    .agent-executor { border-left-color: #4299e1; background: #ebf8ff !important; }
    .agent-reviewer { border-left-color: #ed8936; background: #fffaf0 !important; }
    .agent-system { border-left-color: #718096; background: #f7fafc !important; }

    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    .status-pending { background: #e2e8f0; color: #4a5568; }
    .status-planning { background: #c6f6d5; color: #276749; }
    .status-executing { background: #bee3f8; color: #2b6cb0; }
    .status-reviewing { background: #feebc8; color: #c05621; }
    .status-completed { background: #c6f6d5; color: #276749; }
    .status-failed { background: #fed7d7; color: #c53030; }

    .progress-step {
        text-align: center;
        padding: 0.5rem;
    }

    .progress-step.active {
        font-weight: bold;
    }

    .progress-step.completed {
        color: #48bb78;
    }

    .sample-task {
        background: #f7fafc;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        margin: 0.25rem 0;
        cursor: pointer;
        border: 1px solid #e2e8f0;
        transition: all 0.2s;
    }

    .sample-task:hover {
        background: #edf2f7;
        border-color: #cbd5e0;
    }
</style>
""", unsafe_allow_html=True)

init_session_state()


def render_auth_required():
    """Show login required message."""
    st.warning("Please login to access the dashboard.")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["Login", "Register"])
        with tab1:
            render_login_form()
        with tab2:
            render_register_form()


def render_progress_bar(status: str):
    """Render a visual progress bar."""
    steps = ["Planning", "Executing", "Reviewing", "Complete"]
    status_map = {
        "pending": 0,
        "planning": 1,
        "executing": 2,
        "reviewing": 3,
        "completed": 4,
        "failed": 4
    }
    current = status_map.get(status, 0)

    cols = st.columns(4)
    for i, (col, step) in enumerate(zip(cols, steps)):
        with col:
            if i < current:
                st.markdown(f"<div class='progress-step completed'>✅ {step}</div>", unsafe_allow_html=True)
            elif i == current and status != "completed":
                st.markdown(f"<div class='progress-step active'>🔄 {step}</div>", unsafe_allow_html=True)
            elif status == "completed" and i == 3:
                st.markdown(f"<div class='progress-step completed'>✅ {step}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='progress-step'>⬜ {step}</div>", unsafe_allow_html=True)

    progress = min(current / 4, 1.0) if status != "failed" else 1.0
    st.progress(progress)


def render_agent_messages(messages):
    """Render agent conversation messages."""
    if not messages:
        st.info("Waiting for agent responses...")
        return

    for msg in messages:
        agent = msg.get("agent_name", "System")
        content = msg.get("content", "")

        agent_class = {
            "Planner": "agent-planner",
            "Executor": "agent-executor",
            "Reviewer": "agent-reviewer"
        }.get(agent, "agent-system")

        agent_icon = {
            "Planner": "📋",
            "Executor": "⚡",
            "Reviewer": "✅"
        }.get(agent, "🖥️")

        # Define colors for each agent
        bg_colors = {
            "Planner": "#f0fff4",
            "Executor": "#ebf8ff",
            "Reviewer": "#fffaf0",
            "System": "#f7fafc"
        }
        border_colors = {
            "Planner": "#48bb78",
            "Executor": "#4299e1",
            "Reviewer": "#ed8936",
            "System": "#718096"
        }

        bg_color = bg_colors.get(agent, "#f7fafc")
        border_color = border_colors.get(agent, "#718096")

        st.markdown(f"""
        <div style="
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 8px;
            border-left: 4px solid {border_color};
            background-color: {bg_color};
        ">
            <strong style="color: #2d3748;">{agent_icon} {agent}</strong>
            <div style="margin-top: 0.5rem; white-space: pre-wrap; color: #1a202c;">{content[:1000]}{'...' if len(content) > 1000 else ''}</div>
        </div>
        """, unsafe_allow_html=True)


def render_dashboard():
    """Render the main dashboard."""
    # Header
    st.markdown("""
    <div class="dashboard-header">
        <h2>📊 Task Dashboard</h2>
        <p>Create and monitor your AI-powered tasks</p>
    </div>
    """, unsafe_allow_html=True)

    # Layout
    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("### ➕ Create New Task")

        # Initialize sample task in session state if not exists
        if "selected_sample" not in st.session_state:
            st.session_state.selected_sample = ""

        # Task input - use value parameter instead of key for pre-filling
        objective = st.text_area(
            "What would you like to accomplish?",
            value=st.session_state.selected_sample,
            placeholder="Describe your task objective in detail...",
            height=120
        )

        if st.button("🚀 Submit Task", use_container_width=True, type="primary"):
            if objective and len(objective) >= 10:
                with st.spinner("Creating task..."):
                    result = sync_create_task(objective)
                if result["success"]:
                    st.session_state.current_task_id = result["data"]["id"]
                    st.session_state.selected_sample = ""  # Clear after submit
                    st.success(f"Task #{result['data']['id']} created!")
                    st.rerun()
                else:
                    st.error(result["error"])
            else:
                st.warning("Please enter at least 10 characters")

        # Sample tasks
        st.markdown("---")
        st.markdown("##### 💡 Sample Tasks")

        samples = [
            "Create a weekly meal plan for a vegetarian diet",
            "Design a marketing strategy for a mobile app",
            "Write a project proposal for a new website",
            "Develop a 30-day fitness plan for beginners"
        ]

        for sample in samples:
            if st.button(f"📝 {sample[:40]}...", key=f"sample_{hash(sample)}", use_container_width=True):
                st.session_state.selected_sample = sample
                st.rerun()

        # Recent tasks
        st.markdown("---")
        st.markdown("##### 🕐 Recent Tasks")

        result = sync_get_tasks(limit=5)
        if result["success"] and result["data"]:
            for task in result["data"]:
                status_emoji = {"pending": "⏳", "planning": "📋", "executing": "⚡",
                              "reviewing": "🔍", "completed": "✅", "failed": "❌"}.get(task["status"], "❓")

                if st.button(f"{status_emoji} {task['objective'][:35]}...", key=f"task_{task['id']}", use_container_width=True):
                    st.session_state.current_task_id = task["id"]
                    st.rerun()

    with col2:
        if st.session_state.get("current_task_id"):
            task_id = st.session_state.current_task_id
            result = sync_get_task(task_id)

            if result["success"]:
                task = result["data"]

                # Task header
                st.markdown(f"### 📌 Task #{task['id']}")

                # Status badge
                status_class = f"status-{task['status']}"
                st.markdown(f"""
                <span class="status-badge {status_class}">{task['status'].upper()}</span>
                """, unsafe_allow_html=True)

                st.markdown(f"**Objective:** {task['objective']}")

                # Progress bar
                st.markdown("---")
                render_progress_bar(task["status"])

                # Refresh button for active tasks
                if task["status"] in ["planning", "executing", "reviewing", "pending"]:
                    if st.button("🔄 Refresh Status", use_container_width=True):
                        st.rerun()

                # Agent messages
                st.markdown("---")
                st.markdown("#### 💬 Agent Conversation")

                if task.get("messages"):
                    render_agent_messages(task["messages"])
                else:
                    if task["status"] == "pending":
                        st.info("⏳ Task is queued. Processing will begin shortly...")
                    else:
                        st.info("🔄 Agents are working on your task...")

                # Results expandables
                if task.get("plan"):
                    with st.expander("📋 View Plan", expanded=False):
                        st.markdown(task["plan"])

                if task.get("execution_result"):
                    with st.expander("⚡ View Execution Result", expanded=False):
                        st.markdown(task["execution_result"])

                if task.get("review_result"):
                    with st.expander("✅ View Review Result", expanded=True):
                        st.markdown(task["review_result"])
            else:
                st.error("Failed to load task details")
        else:
            # No task selected
            st.markdown("""
            <div class="task-card" style="text-align: center; padding: 3rem;">
                <h3>👈 Create or select a task</h3>
                <p style="color: #718096;">
                    Enter your objective on the left to create a new task,<br>
                    or select a recent task to view its progress.
                </p>
            </div>
            """, unsafe_allow_html=True)


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

    if st.button("📜 History", use_container_width=True):
        st.switch_page("pages/2_history.py")

    st.markdown("---")

    if is_authenticated():
        if st.button("🚪 Logout", use_container_width=True):
            sync_logout()
            clear_authentication()
            st.rerun()

# Main content
if is_authenticated():
    render_dashboard()
else:
    render_auth_required()
