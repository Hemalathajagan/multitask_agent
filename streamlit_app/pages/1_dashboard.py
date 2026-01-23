import streamlit as st
import sys
from pathlib import Path
from streamlit_autorefresh import st_autorefresh

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from streamlit_app.utils import (
    init_session_state, is_authenticated,
    sync_get_task, sync_get_tasks, sync_create_task,
    sync_rename_task, sync_rerun_task, sync_continue_task
)
from streamlit_app.components import render_login_form, render_register_form, render_sidebar

st.set_page_config(
    page_title="Dashboard - Multi-Agent Task Assistant",
    page_icon="📊",
    layout="wide"
)

# Professional CSS
st.markdown("""
<style>
    /* Hide default Streamlit page navigation */
    [data-testid="stSidebarNav"] { display: none !important; }

    /* Dashboard Header */
    .dashboard-header {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(30, 58, 95, 0.3);
    }

    .dashboard-header h1 {
        margin: 0 0 0.5rem 0;
        font-size: 1.8rem;
        font-weight: 700;
        letter-spacing: -0.5px;
    }

    .dashboard-header p {
        margin: 0;
        opacity: 0.85;
        font-size: 1rem;
    }

    /* Cards */
    .pro-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 1.75rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid #e8ecf1;
        margin-bottom: 1.5rem;
    }

    .pro-card-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1.25rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid #e8ecf1;
    }

    .pro-card-header h3 {
        margin: 0;
        font-size: 1.1rem;
        font-weight: 600;
        color: #1a202c;
    }

    .pro-card-icon {
        width: 40px;
        height: 40px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.25rem;
    }

    .icon-blue { background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%); }
    .icon-green { background: linear-gradient(135deg, #48bb78 0%, #38a169 100%); }
    .icon-purple { background: linear-gradient(135deg, #9f7aea 0%, #805ad5 100%); }
    .icon-orange { background: linear-gradient(135deg, #ed8936 0%, #dd6b20 100%); }

    /* Task Input Area */
    .task-input-container {
        background: #f8fafc;
        border-radius: 12px;
        padding: 1.25rem;
        border: 2px dashed #cbd5e0;
        transition: all 0.3s ease;
    }

    .task-input-container:hover {
        border-color: #4299e1;
        background: #f0f7ff;
    }

    /* Sample Task Chips */
    .sample-chip {
        display: inline-block;
        background: linear-gradient(135deg, #edf2f7 0%, #e2e8f0 100%);
        padding: 0.6rem 1rem;
        border-radius: 25px;
        font-size: 0.85rem;
        color: #4a5568;
        margin: 0.25rem;
        cursor: pointer;
        transition: all 0.2s ease;
        border: 1px solid #e2e8f0;
    }

    .sample-chip:hover {
        background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(66, 153, 225, 0.4);
    }

    /* Recent Task Item */
    .recent-task-item {
        display: flex;
        align-items: center;
        padding: 0.875rem 1rem;
        background: #f8fafc;
        border-radius: 10px;
        margin-bottom: 0.5rem;
        cursor: pointer;
        transition: all 0.2s ease;
        border: 1px solid transparent;
    }

    .recent-task-item:hover {
        background: #edf2f7;
        border-color: #4299e1;
        transform: translateX(4px);
    }

    .recent-task-status {
        width: 32px;
        height: 32px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 0.75rem;
        font-size: 1rem;
    }

    .recent-task-info {
        flex: 1;
        overflow: hidden;
    }

    .recent-task-title {
        font-size: 0.9rem;
        font-weight: 500;
        color: #2d3748;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .recent-task-meta {
        font-size: 0.75rem;
        color: #718096;
    }

    /* Status Badges */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .status-pending { background: #edf2f7; color: #4a5568; }
    .status-planning { background: #e6fffa; color: #234e52; }
    .status-executing { background: #ebf8ff; color: #2b6cb0; }
    .status-reviewing { background: #fefcbf; color: #975a16; }
    .status-completed { background: #c6f6d5; color: #276749; }
    .status-failed { background: #fed7d7; color: #c53030; }

    /* Progress Steps */
    .progress-container {
        display: flex;
        justify-content: space-between;
        position: relative;
        margin: 1.5rem 0;
    }

    .progress-step {
        display: flex;
        flex-direction: column;
        align-items: center;
        flex: 1;
        position: relative;
        z-index: 1;
    }

    .step-circle {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        transition: all 0.3s ease;
    }

    .step-circle.pending {
        background: #edf2f7;
        color: #a0aec0;
        border: 2px solid #e2e8f0;
    }

    .step-circle.active {
        background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(66, 153, 225, 0.5);
        animation: pulse 2s infinite;
    }

    .step-circle.completed {
        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
        color: white;
    }

    .step-label {
        font-size: 0.8rem;
        font-weight: 500;
        color: #718096;
    }

    .step-label.active {
        color: #3182ce;
        font-weight: 600;
    }

    .step-label.completed {
        color: #38a169;
    }

    @keyframes pulse {
        0%, 100% { box-shadow: 0 4px 15px rgba(66, 153, 225, 0.5); }
        50% { box-shadow: 0 4px 25px rgba(66, 153, 225, 0.8); }
    }

    /* Agent Messages */
    .agent-message {
        padding: 1.25rem;
        margin: 0.75rem 0;
        border-radius: 12px;
        border-left: 4px solid;
        background: #ffffff;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    }

    .agent-message.planner {
        border-left-color: #48bb78;
        background: linear-gradient(135deg, #f0fff4 0%, #c6f6d5 100%);
    }

    .agent-message.executor {
        border-left-color: #4299e1;
        background: linear-gradient(135deg, #ebf8ff 0%, #bee3f8 100%);
    }

    .agent-message.reviewer {
        border-left-color: #ed8936;
        background: linear-gradient(135deg, #fffaf0 0%, #feebc8 100%);
    }

    .agent-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.75rem;
    }

    .agent-name {
        font-weight: 600;
        color: #2d3748;
        font-size: 0.95rem;
    }

    .agent-content {
        color: #4a5568;
        font-size: 0.9rem;
        line-height: 1.6;
        white-space: pre-wrap;
    }

    /* Action Buttons */
    .action-btn-group {
        display: flex;
        gap: 0.75rem;
        margin: 1rem 0;
    }

    /* Output Section */
    .output-section {
        background: linear-gradient(135deg, #f8fafc 0%, #edf2f7 100%);
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #e2e8f0;
    }

    .output-section h4 {
        color: #2d3748;
        margin: 0 0 1rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* Empty State */
    .empty-state {
        text-align: center;
        padding: 4rem 2rem;
        background: linear-gradient(135deg, #f8fafc 0%, #edf2f7 100%);
        border-radius: 16px;
        border: 2px dashed #cbd5e0;
    }

    .empty-state h3 {
        color: #4a5568;
        margin: 1rem 0 0.5rem 0;
    }

    .empty-state p {
        color: #718096;
        margin: 0;
    }

    .empty-icon {
        font-size: 4rem;
        opacity: 0.5;
    }

    /* Modal styles */
    .modal-section {
        background: #f8fafc;
        border-radius: 12px;
        padding: 1.25rem;
        border: 1px solid #e2e8f0;
        margin: 1rem 0;
    }

    .modal-section h5 {
        color: #2d3748;
        margin: 0 0 1rem 0;
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


def render_progress_steps(status: str):
    """Render professional progress steps."""
    steps = [
        ("📋", "Planning"),
        ("⚡", "Executing"),
        ("🔍", "Reviewing"),
        ("✅", "Complete")
    ]

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
    for i, (col, (icon, label)) in enumerate(zip(cols, steps)):
        with col:
            if i < current:
                state = "completed"
                circle_content = "✓"
            elif i == current and status not in ["completed", "failed"]:
                state = "active"
                circle_content = icon
            elif status == "completed" and i == 3:
                state = "completed"
                circle_content = "✓"
            else:
                state = "pending"
                circle_content = str(i + 1)

            st.markdown(f"""
            <div class="progress-step">
                <div class="step-circle {state}">{circle_content}</div>
                <div class="step-label {state}">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    # Progress bar
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
            "Planner": "planner",
            "Executor": "executor",
            "Reviewer": "reviewer"
        }.get(agent, "")

        agent_icon = {
            "Planner": "📋",
            "Executor": "⚡",
            "Reviewer": "✅"
        }.get(agent, "🖥️")

        st.markdown(f"""
        <div class="agent-message {agent_class}">
            <div class="agent-header">
                <span style="font-size: 1.2rem;">{agent_icon}</span>
                <span class="agent-name">{agent}</span>
            </div>
            <div class="agent-content">{content[:1500]}{'...' if len(content) > 1500 else ''}</div>
        </div>
        """, unsafe_allow_html=True)


def render_dashboard():
    """Render the main dashboard."""
    # Header
    st.markdown("""
    <div class="dashboard-header">
        <h1>📊 Task Dashboard</h1>
        <p>Create, monitor, and manage your AI-powered tasks</p>
    </div>
    """, unsafe_allow_html=True)

    # Layout
    col1, col2 = st.columns([1, 2], gap="large")

    with col1:
        # Create New Task Card
        st.markdown("""
        <div class="pro-card">
            <div class="pro-card-header">
                <div class="pro-card-icon icon-blue">➕</div>
                <h3>Create New Task</h3>
            </div>
        """, unsafe_allow_html=True)

        # Initialize sample task in session state
        if "selected_sample" not in st.session_state:
            st.session_state.selected_sample = ""

        objective = st.text_area(
            "What would you like to accomplish?",
            value=st.session_state.selected_sample,
            placeholder="Describe your task in detail. Be specific about what you want to achieve...",
            height=100,
            label_visibility="collapsed"
        )

        if st.button("🚀 Create Task", use_container_width=True, type="primary"):
            if objective and len(objective) >= 10:
                with st.spinner("Creating task..."):
                    result = sync_create_task(objective)
                if result["success"]:
                    st.session_state.current_task_id = result["data"]["id"]
                    st.session_state.selected_sample = ""
                    st.success(f"Task #{result['data']['id']} created!")
                    st.rerun()
                else:
                    st.error(result["error"])
            else:
                st.warning("Please enter at least 10 characters")

        st.markdown("</div>", unsafe_allow_html=True)

        # Quick Start Templates
        st.markdown("""
        <div class="pro-card">
            <div class="pro-card-header">
                <div class="pro-card-icon icon-purple">💡</div>
                <h3>Quick Start Templates</h3>
            </div>
        """, unsafe_allow_html=True)

        samples = [
            ("🍽️", "Weekly meal plan for vegetarian diet"),
            ("📱", "Marketing strategy for mobile app"),
            ("💻", "Project proposal for website"),
            ("🏋️", "30-day fitness plan for beginners")
        ]

        for icon, sample in samples:
            if st.button(f"{icon} {sample}", key=f"sample_{hash(sample)}", use_container_width=True):
                st.session_state.selected_sample = sample
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        # Recent Tasks
        st.markdown("""
        <div class="pro-card">
            <div class="pro-card-header">
                <div class="pro-card-icon icon-green">🕐</div>
                <h3>Recent Tasks</h3>
            </div>
        """, unsafe_allow_html=True)

        result = sync_get_tasks(limit=5)
        if result["success"] and result["data"]:
            for task in result["data"]:
                status_colors = {
                    "pending": "#718096",
                    "planning": "#38a169",
                    "executing": "#3182ce",
                    "reviewing": "#d69e2e",
                    "completed": "#38a169",
                    "failed": "#e53e3e"
                }
                status_emoji = {
                    "pending": "⏳",
                    "planning": "📋",
                    "executing": "⚡",
                    "reviewing": "🔍",
                    "completed": "✅",
                    "failed": "❌"
                }.get(task["status"], "❓")

                col_btn, col_status = st.columns([5, 1])
                with col_btn:
                    if st.button(
                        f"{task['objective'][:35]}...",
                        key=f"task_{task['id']}",
                        use_container_width=True
                    ):
                        st.session_state.current_task_id = task["id"]
                        st.rerun()
                with col_status:
                    st.markdown(f"<div style='text-align:center;padding-top:8px;'>{status_emoji}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<p style='color:#718096;text-align:center;'>No tasks yet</p>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        if st.session_state.get("current_task_id"):
            task_id = st.session_state.current_task_id
            result = sync_get_task(task_id)

            if result["success"]:
                task = result["data"]

                # Auto-refresh for active tasks
                if task["status"] in ["planning", "executing", "reviewing", "pending"]:
                    st_autorefresh(interval=5000, limit=None, key="task_autorefresh")

                # Task Details Card
                st.markdown("""
                <div class="pro-card">
                    <div class="pro-card-header">
                        <div class="pro-card-icon icon-orange">📌</div>
                        <h3>Task Details</h3>
                    </div>
                """, unsafe_allow_html=True)

                # Status and ID
                col_id, col_status = st.columns([2, 1])
                with col_id:
                    st.markdown(f"**Task #{task['id']}**")
                with col_status:
                    status_class = f"status-{task['status']}"
                    st.markdown(f'<span class="status-badge {status_class}">{task["status"].upper()}</span>', unsafe_allow_html=True)

                st.markdown(f"<p style='color:#4a5568;margin:1rem 0;'>{task['objective']}</p>", unsafe_allow_html=True)

                # Progress Steps
                st.markdown("---")
                render_progress_steps(task["status"])

                # Refresh button for active tasks
                if task["status"] in ["planning", "executing", "reviewing", "pending"]:
                    if st.button("🔄 Refresh Status", use_container_width=True):
                        st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)

                # Status-specific content
                if task["status"] == "pending":
                    st.info("⏳ Task is queued and will begin processing shortly...")

                elif task["status"] == "planning":
                    st.info("📋 **Planner Agent** is analyzing your objective and creating a detailed plan...")

                elif task["status"] == "executing":
                    st.info("⚡ **Executor Agent** is working on the task...")
                    if task.get("plan"):
                        with st.expander("📋 View Current Plan", expanded=True):
                            st.markdown(task["plan"])

                elif task["status"] == "reviewing":
                    st.info("🔍 **Reviewer Agent** is validating the work and ensuring quality...")

                elif task["status"] == "completed":
                    st.success("🎉 Task completed successfully!")

                    # Task Actions
                    st.markdown("""
                    <div class="pro-card">
                        <div class="pro-card-header">
                            <div class="pro-card-icon icon-blue">⚙️</div>
                            <h3>Task Actions</h3>
                        </div>
                    """, unsafe_allow_html=True)

                    action_col1, action_col2, action_col3 = st.columns(3)

                    with action_col1:
                        if st.button("✏️ Rename", use_container_width=True, key="rename_btn"):
                            st.session_state.show_rename_modal = True
                            st.session_state.show_rerun_confirm = False
                            st.session_state.show_continue_modal = False

                    with action_col2:
                        if st.button("🔄 Re-run", use_container_width=True, key="rerun_btn"):
                            st.session_state.show_rerun_confirm = True
                            st.session_state.show_rename_modal = False
                            st.session_state.show_continue_modal = False

                    with action_col3:
                        if st.button("➕ Continue", use_container_width=True, key="continue_btn"):
                            st.session_state.show_continue_modal = True
                            st.session_state.show_rename_modal = False
                            st.session_state.show_rerun_confirm = False

                    # Rename Modal
                    if st.session_state.get("show_rename_modal"):
                        st.markdown('<div class="modal-section">', unsafe_allow_html=True)
                        st.markdown("##### ✏️ Rename Task")
                        new_name = st.text_input("New task name", value=task["objective"], key="new_task_name")
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("💾 Save", use_container_width=True, key="save_rename", type="primary"):
                                if new_name and len(new_name) >= 10:
                                    result = sync_rename_task(task["id"], new_name)
                                    if result["success"]:
                                        st.success("Task renamed!")
                                        st.session_state.show_rename_modal = False
                                        st.rerun()
                                    else:
                                        st.error(result["error"])
                                else:
                                    st.warning("Name must be at least 10 characters")
                        with col2:
                            if st.button("Cancel", use_container_width=True, key="cancel_rename"):
                                st.session_state.show_rename_modal = False
                                st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)

                    # Rerun Confirmation
                    if st.session_state.get("show_rerun_confirm"):
                        st.markdown('<div class="modal-section">', unsafe_allow_html=True)
                        st.markdown("##### 🔄 Re-run Task")
                        st.warning("This will clear previous results and run the task again.")
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("✅ Confirm Re-run", use_container_width=True, key="confirm_rerun", type="primary"):
                                result = sync_rerun_task(task["id"])
                                if result["success"]:
                                    st.success("Task is being re-run!")
                                    st.session_state.show_rerun_confirm = False
                                    st.rerun()
                                else:
                                    st.error(result["error"])
                        with col2:
                            if st.button("Cancel", use_container_width=True, key="cancel_rerun"):
                                st.session_state.show_rerun_confirm = False
                                st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)

                    # Continue Modal
                    if st.session_state.get("show_continue_modal"):
                        st.markdown('<div class="modal-section">', unsafe_allow_html=True)
                        st.markdown("##### ➕ Create Follow-up Task")
                        continue_objective = st.text_area(
                            "What would you like to do next?",
                            placeholder="Describe the follow-up task...",
                            height=80,
                            key="continue_objective"
                        )
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("🚀 Create", use_container_width=True, key="create_continue", type="primary"):
                                if continue_objective and len(continue_objective) >= 10:
                                    result = sync_continue_task(task["id"], continue_objective)
                                    if result["success"]:
                                        st.success(f"Follow-up task #{result['data']['id']} created!")
                                        st.session_state.current_task_id = result["data"]["id"]
                                        st.session_state.show_continue_modal = False
                                        st.rerun()
                                    else:
                                        st.error(result["error"])
                                else:
                                    st.warning("Please enter at least 10 characters")
                        with col2:
                            if st.button("Cancel", use_container_width=True, key="cancel_continue"):
                                st.session_state.show_continue_modal = False
                                st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)

                    st.markdown("</div>", unsafe_allow_html=True)

                    # Output Section
                    st.markdown("""
                    <div class="pro-card">
                        <div class="pro-card-header">
                            <div class="pro-card-icon icon-green">📊</div>
                            <h3>Task Output</h3>
                        </div>
                    """, unsafe_allow_html=True)

                    if task.get("review_result"):
                        st.markdown(task["review_result"])

                    st.markdown("</div>", unsafe_allow_html=True)

                    # Detailed Results
                    st.markdown("##### 📁 Detailed Results")

                    if task.get("plan"):
                        with st.expander("📋 View Plan", expanded=False):
                            st.markdown(task["plan"])

                    if task.get("execution_result"):
                        with st.expander("⚡ View Execution Details", expanded=False):
                            st.markdown(task["execution_result"])

                    if task.get("messages"):
                        with st.expander("💬 View Agent Conversation", expanded=False):
                            render_agent_messages(task["messages"])

                elif task["status"] == "failed":
                    st.error("❌ Task failed to complete")
                    if task.get("messages"):
                        with st.expander("💬 View Details", expanded=True):
                            render_agent_messages(task["messages"])
            else:
                st.error("Failed to load task details")
        else:
            # No task selected - Empty State
            st.markdown("""
            <div class="empty-state">
                <div class="empty-icon">📋</div>
                <h3>No Task Selected</h3>
                <p>Create a new task or select one from your recent tasks to get started.</p>
            </div>
            """, unsafe_allow_html=True)


# Render shared sidebar
if is_authenticated():
    render_sidebar(current_page="dashboard")

# Main content
if is_authenticated():
    render_dashboard()
else:
    render_auth_required()
