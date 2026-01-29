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
       DASHBOARD HEADER - WARM ORANGE
       ============================================ */
    .dashboard-header {
        background: linear-gradient(135deg, #ea580c 0%, #f97316 50%, #fb923c 100%);
        padding: 2.5rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
        box-shadow:
            0 20px 40px rgba(234, 88, 12, 0.3),
            0 0 0 1px rgba(255, 255, 255, 0.1) inset;
    }

    .dashboard-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 60%;
        height: 200%;
        background: radial-gradient(ellipse, rgba(255,255,255,0.15) 0%, transparent 70%);
        pointer-events: none;
    }

    .dashboard-header h1 {
        margin: 0 0 0.5rem 0;
        font-size: 1.75rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        position: relative;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .dashboard-header p {
        margin: 0;
        opacity: 0.95;
        font-size: 1rem;
        position: relative;
    }

    /* ============================================
       PROFESSIONAL CARDS
       ============================================ */
    .pro-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(234, 88, 12, 0.08);
        box-shadow:
            0 1px 3px rgba(0,0,0,0.04),
            0 4px 12px rgba(234, 88, 12, 0.06);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .pro-card:hover {
        box-shadow:
            0 8px 24px rgba(234, 88, 12, 0.12),
            0 4px 8px rgba(0,0,0,0.04);
    }

    .pro-card-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1.25rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid #fed7aa;
    }

    .pro-card-header h3 {
        margin: 0;
        font-size: 1rem;
        font-weight: 700;
        color: #1c1917;
        letter-spacing: -0.02em;
    }

    .pro-card-icon {
        width: 42px;
        height: 42px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
        color: white;
    }

    .icon-blue { background: linear-gradient(135deg, #f97316 0%, #ea580c 100%); box-shadow: 0 4px 12px rgba(249, 115, 22, 0.3); }
    .icon-green { background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%); box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3); }
    .icon-purple { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3); }
    .icon-orange { background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3); }

    /* ============================================
       STATUS BADGES
       ============================================ */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.375rem;
        padding: 0.375rem 0.875rem;
        border-radius: 9999px;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .status-pending { background: #e7e5e4; color: #57534e; }
    .status-planning { background: #fed7aa; color: #c2410c; }
    .status-executing { background: #fde68a; color: #b45309; }
    .status-reviewing { background: #fecaca; color: #b91c1c; }
    .status-completed { background: #bbf7d0; color: #166534; }
    .status-failed { background: #fecaca; color: #b91c1c; }

    /* ============================================
       PROGRESS STEPS
       ============================================ */
    .progress-step {
        display: flex;
        flex-direction: column;
        align-items: center;
        flex: 1;
        position: relative;
    }

    .step-circle {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .step-circle.pending {
        background: #fafaf9;
        color: #a8a29e;
        border: 2px solid #e7e5e4;
    }

    .step-circle.active {
        background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
        color: white;
        box-shadow: 0 6px 20px rgba(249, 115, 22, 0.5);
        animation: pulse 2s infinite;
    }

    .step-circle.completed {
        background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
        color: white;
        box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3);
    }

    .step-label {
        font-size: 0.8rem;
        font-weight: 500;
        color: #a8a29e;
    }

    .step-label.active { color: #ea580c; font-weight: 600; }
    .step-label.completed { color: #16a34a; font-weight: 600; }

    @keyframes pulse {
        0%, 100% { box-shadow: 0 6px 20px rgba(249, 115, 22, 0.5); }
        50% { box-shadow: 0 8px 30px rgba(249, 115, 22, 0.7); }
    }

    /* ============================================
       AGENT MESSAGES
       ============================================ */
    .agent-message {
        padding: 1.25rem;
        margin: 0.75rem 0;
        border-radius: 14px;
        border-left: 4px solid;
        background: white;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }

    .agent-message.planner {
        border-left-color: #22c55e;
        background: linear-gradient(135deg, #f0fdf4 0%, #bbf7d0 100%);
    }

    .agent-message.executor {
        border-left-color: #f97316;
        background: linear-gradient(135deg, #fff7ed 0%, #fed7aa 100%);
    }

    .agent-message.reviewer {
        border-left-color: #f59e0b;
        background: linear-gradient(135deg, #fffbeb 0%, #fde68a 100%);
    }

    .agent-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.75rem;
    }

    .agent-name {
        font-weight: 700;
        color: #1c1917;
        font-size: 0.9rem;
        letter-spacing: -0.01em;
    }

    .agent-content {
        color: #57534e;
        font-size: 0.875rem;
        line-height: 1.7;
        white-space: pre-wrap;
    }

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

    .empty-icon {
        font-size: 4rem;
        opacity: 0.4;
    }

    /* ============================================
       MODAL SECTION
       ============================================ */
    .modal-section {
        background: #fffbf5;
        border-radius: 14px;
        padding: 1.5rem;
        border: 1px solid #fed7aa;
        margin: 1rem 0;
    }

    .modal-section h5 {
        color: #1c1917;
        margin: 0 0 1rem 0;
        font-size: 1rem;
        font-weight: 600;
    }

    /* ============================================
       BUTTON OVERRIDES - ORANGE THEME
       ============================================ */
    .stButton > button {
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 0.75rem 1.5rem !important;
        font-size: 0.95rem !important;
        transition: all 0.2s ease !important;
        border: none !important;
        letter-spacing: -0.01em !important;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #f97316 0%, #ea580c 100%) !important;
        color: white !important;
        box-shadow: 0 4px 14px rgba(249, 115, 22, 0.4) !important;
    }

    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(249, 115, 22, 0.5) !important;
    }

    .stButton > button[kind="secondary"] {
        background: #fafaf9 !important;
        color: #57534e !important;
        border: 1px solid #e7e5e4 !important;
    }

    .stButton > button[kind="secondary"]:hover {
        background: #f5f5f4 !important;
    }

    /* ============================================
       INPUT OVERRIDES
       ============================================ */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 12px !important;
        border: 2px solid #fed7aa !important;
        padding: 0.875rem 1rem !important;
        font-size: 0.95rem !important;
        transition: all 0.2s ease !important;
        background-color: #fffbf5 !important;
        color: #1c1917 !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #f97316 !important;
        box-shadow: 0 0 0 3px rgba(249, 115, 22, 0.15) !important;
        background-color: #ffffff !important;
    }

    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: #a8a29e !important;
    }

    /* Labels */
    .stTextInput > label,
    .stTextArea > label,
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

    /* Info/Warning/Error boxes */
    .stAlert {
        color: #1c1917 !important;
    }

    /* Progress bar */
    .stProgress > div > div > div {
        background-color: #fed7aa !important;
    }

    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #f97316, #ea580c) !important;
    }

    /* Spinner */
    .stSpinner > div {
        border-top-color: #f97316 !important;
    }

    /* Links */
    a {
        color: #ea580c !important;
    }

    /* Info/Warning boxes */
    .stAlert {
        border-radius: 12px !important;
    }

    div[data-testid="stAlert"] {
        background-color: #fff7ed !important;
        color: #1c1917 !important;
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
        border-radius: 12px !important;
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


def clean_task_output(review_result: str, execution_result: str = None) -> str:
    """Parse and clean the task output to show only the final polished content."""
    if not review_result and not execution_result:
        return None

    # Use execution_result as the main content
    content = execution_result or ""

    # If no execution result, try to extract useful content from review
    if not content and review_result:
        # Only use review if it has actual content beyond status markers
        if "APPROVED" in review_result or "TASK_COMPLETE" in review_result:
            content = execution_result or ""
        else:
            content = review_result

    if not content:
        return None

    # Markers that indicate backend/internal content to remove
    backend_markers = [
        "TASK_COMPLETE", "EXECUTION_COMPLETE", "PLAN_COMPLETE", "NEEDS_REVISION",
        "APPROVED", "Status: Complete", "Status: Incomplete", "Quality: Excellent",
        "Quality: Good", "Quality: Fair", "Quality: Poor", "Final Verdict",
        "Issues Found", "Detailed Review", "Review Summary", "Plan Coverage:",
        "Original Objective:", "Task Analysis", "Subtasks Completion Summary",
        "Execution Order", "Dependencies:", "Expected Output:", "Priority:",
        "### Executing:", "**Approach:**", "Approach:"
    ]

    # Section headers to skip entirely
    skip_sections = [
        "Review Summary", "Detailed Review", "Issues Found", "Final Verdict",
        "Task Analysis", "Subtasks Completion Summary", "Execution Order"
    ]

    cleaned_lines = []
    skip_until_next_section = False
    in_notes_section = False

    lines = content.split('\n')

    for i, line in enumerate(lines):
        line_stripped = line.strip()

        # Skip empty lines at the start
        if not cleaned_lines and not line_stripped:
            continue

        # Check if we should skip this section entirely
        should_skip_section = False
        for section in skip_sections:
            if section in line_stripped and (line_stripped.startswith('#') or line_stripped.startswith('**')):
                skip_until_next_section = True
                should_skip_section = True
                break

        if should_skip_section:
            continue

        # Reset skip flag on new major section
        if line_stripped.startswith('## ') or line_stripped.startswith('### '):
            skip_until_next_section = False

        if skip_until_next_section:
            continue

        # Skip lines with backend markers
        should_skip = False
        for marker in backend_markers:
            if marker in line_stripped:
                should_skip = True
                break

        # Skip subtask metadata lines
        if line_stripped.startswith("Subtask ") and any(x in line_stripped for x in ["Status:", "Quality:", "Priority:", "Dependencies:"]):
            should_skip = True

        # Skip "Notes:" lines that look internal
        if line_stripped.startswith("Notes:") or line_stripped == "**Notes:**":
            in_notes_section = True
            should_skip = True

        # Skip lines in notes sections that are short (internal notes)
        if in_notes_section:
            if line_stripped.startswith('-') and len(line_stripped) < 150:
                should_skip = True
            elif line_stripped == "" or line_stripped.startswith('#') or line_stripped.startswith('**'):
                in_notes_section = False

        # Skip "---" separators
        if line_stripped == "---":
            should_skip = True

        # Skip repeated completion markers
        if line_stripped in ["EXECUTION_COMPLETE", "PLAN_COMPLETE", "TASK_COMPLETE"]:
            should_skip = True

        if not should_skip:
            cleaned_lines.append(line)

    # Join and clean up
    result = '\n'.join(cleaned_lines).strip()

    # Remove multiple consecutive newlines
    while '\n\n\n' in result:
        result = result.replace('\n\n\n', '\n\n')

    # Remove any remaining backend markers that might have slipped through
    for marker in ["EXECUTION_COMPLETE", "PLAN_COMPLETE", "TASK_COMPLETE", "APPROVED", "NEEDS_REVISION"]:
        result = result.replace(marker, "")

    # Clean up any leftover artifacts
    result = result.strip()

    # If result is too short or empty, return None
    if not result or len(result) < 50:
        return None

    return result


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
                    "pending": "#78716c",
                    "planning": "#f97316",
                    "executing": "#f59e0b",
                    "reviewing": "#ef4444",
                    "completed": "#22c55e",
                    "failed": "#dc2626"
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

                    # Output Section - Clean Final Result Only
                    st.markdown("""
                    <div class="pro-card">
                        <div class="pro-card-header">
                            <div class="pro-card-icon icon-green">📊</div>
                            <h3>Your Results</h3>
                        </div>
                    """, unsafe_allow_html=True)

                    # Get clean output - prioritize execution result
                    clean_output = clean_task_output(
                        task.get("review_result", ""),
                        task.get("execution_result", "")
                    )

                    if clean_output:
                        # Display clean output with nice formatting
                        st.markdown(clean_output)
                    else:
                        # Fallback - show a summary message
                        st.markdown(f"""
                        <div style="
                            background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
                            border: 1px solid #bbf7d0;
                            border-radius: 12px;
                            padding: 1.25rem;
                            color: #1c1917;
                            text-align: center;
                        ">
                            <p style="font-size: 1.1rem; margin: 0;">✅ Task completed successfully!</p>
                            <p style="color: #57534e; margin: 0.5rem 0 0 0;">Your task "{task['objective'][:50]}..." has been processed.</p>
                        </div>
                        """, unsafe_allow_html=True)

                    st.markdown("</div>", unsafe_allow_html=True)

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
