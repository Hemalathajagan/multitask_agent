import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from streamlit_app.utils import init_session_state, is_authenticated
from streamlit_app.components import render_sidebar

st.set_page_config(
    page_title="How It Works - Multi-Agent Task Assistant",
    page_icon="📖",
    layout="wide"
)

# Custom CSS - Warm Orange Theme
st.markdown("""
<style>
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

    .stApp {
        background: linear-gradient(180deg, #fffbf5 0%, #fef7ed 100%);
    }

    .guide-header {
        background: linear-gradient(135deg, #ea580c 0%, #f97316 50%, #fb923c 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 20px 40px rgba(234, 88, 12, 0.3);
    }

    .step-card {
        background: white;
        padding: 1.5rem;
        border-radius: 14px;
        box-shadow: 0 4px 12px rgba(234, 88, 12, 0.08);
        margin-bottom: 1rem;
        border-left: 4px solid;
    }

    .step-card h4 {
        color: #1c1917 !important;
        margin-bottom: 0.5rem;
    }

    .step-card p {
        color: #57534e !important;
        margin: 0;
    }

    .step-card.step-1 { border-left-color: #f97316; }
    .step-card.step-2 { border-left-color: #22c55e; }
    .step-card.step-3 { border-left-color: #f59e0b; }
    .step-card.step-4 { border-left-color: #ef4444; }

    .agent-card {
        background: white;
        padding: 1.5rem;
        border-radius: 14px;
        box-shadow: 0 4px 12px rgba(234, 88, 12, 0.08);
        text-align: center;
        height: 100%;
        border: 1px solid rgba(234, 88, 12, 0.08);
    }

    .agent-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }

    .agent-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #1c1917;
        margin-bottom: 0.5rem;
    }

    .agent-desc {
        color: #57534e;
        font-size: 0.95rem;
    }

    .feature-box {
        background: #fff7ed;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border: 1px solid #fed7aa;
    }

    .feature-box strong {
        color: #1c1917;
    }

    .tip-box {
        background: linear-gradient(135deg, #fff7ed, #ffedd5);
        border-left: 4px solid #f97316;
        padding: 1rem;
        border-radius: 0 10px 10px 0;
        margin: 1rem 0;
    }

    .tip-box strong {
        color: #1c1917 !important;
    }

    .tip-box br + * {
        color: #292524 !important;
    }

    .warning-box {
        background: linear-gradient(135deg, #fffbeb, #fef3c7);
        border-left: 4px solid #f59e0b;
        padding: 1rem;
        border-radius: 0 10px 10px 0;
        margin: 1rem 0;
    }

    .warning-box strong {
        color: #1c1917 !important;
    }

    .section-title {
        color: #1c1917;
        border-bottom: 2px solid #fed7aa;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }

    /* Button overrides */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #f97316 0%, #ea580c 100%) !important;
        border: none !important;
        color: white !important;
        box-shadow: 0 4px 14px rgba(249, 115, 22, 0.4) !important;
        border-radius: 12px !important;
    }

    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(249, 115, 22, 0.5) !important;
    }

    /* All text elements */
    p, span, div {
        color: #1c1917;
    }

    .stMarkdown, .stMarkdown p {
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

    /* Table text */
    table, th, td {
        color: #1c1917 !important;
    }

    /* Code blocks */
    code, pre {
        color: #1c1917 !important;
        background-color: #fff7ed !important;
    }
</style>
""", unsafe_allow_html=True)

init_session_state()

# Header
st.markdown("""
<div class="guide-header">
    <h1>📖 How It Works</h1>
    <p>Your complete guide to using the Multi-Agent Task Assistant</p>
</div>
""", unsafe_allow_html=True)

# Quick Navigation using buttons
st.markdown("### 🧭 Quick Navigation")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("""
    <a href="#what-is-this" style="text-decoration:none;">
        <div style="background:linear-gradient(135deg, #f97316, #ea580c);color:white;padding:0.5rem 1rem;border-radius:10px;text-align:center;font-weight:500;box-shadow:0 4px 12px rgba(249,115,22,0.3);">
            What is this?
        </div>
    </a>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
    <a href="#how-to-use" style="text-decoration:none;">
        <div style="background:linear-gradient(135deg, #22c55e, #16a34a);color:white;padding:0.5rem 1rem;border-radius:10px;text-align:center;font-weight:500;box-shadow:0 4px 12px rgba(34,197,94,0.3);">
            How to Use
        </div>
    </a>
    """, unsafe_allow_html=True)
with col3:
    st.markdown("""
    <a href="#the-agents" style="text-decoration:none;">
        <div style="background:linear-gradient(135deg, #f59e0b, #d97706);color:white;padding:0.5rem 1rem;border-radius:10px;text-align:center;font-weight:500;box-shadow:0 4px 12px rgba(245,158,11,0.3);">
            The Agents
        </div>
    </a>
    """, unsafe_allow_html=True)
with col4:
    st.markdown("""
    <a href="#tips-tricks" style="text-decoration:none;">
        <div style="background:linear-gradient(135deg, #ef4444, #dc2626);color:white;padding:0.5rem 1rem;border-radius:10px;text-align:center;font-weight:500;box-shadow:0 4px 12px rgba(239,68,68,0.3);">
            Tips & Tricks
        </div>
    </a>
    """, unsafe_allow_html=True)

st.markdown("---")

# What is this?
st.markdown('<h2 class="section-title" id="what-is-this">🤖 What is the Multi-Agent Task Assistant?</h2>', unsafe_allow_html=True)

st.markdown("""
The **Multi-Agent Task Assistant** is an AI-powered system that helps you accomplish complex tasks by breaking them down
and processing them through three specialized AI agents that work together.

Think of it as having a team of three AI experts:
- One that **plans** your task
- One that **executes** the plan
- One that **reviews** the work

This collaborative approach ensures higher quality results than a single AI working alone.
""")

# The Agents
st.markdown('<h2 class="section-title" id="the-agents">👥 Meet the Agents</h2>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="agent-card">
        <div class="agent-icon">📋</div>
        <div class="agent-title">Planner Agent</div>
        <div class="agent-desc">
            Analyzes your objective and creates a detailed, step-by-step plan.
            Identifies subtasks, priorities, and dependencies.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="agent-card">
        <div class="agent-icon">⚡</div>
        <div class="agent-title">Executor Agent</div>
        <div class="agent-desc">
            Takes the plan and executes each subtask thoroughly.
            Produces detailed outputs and documentation.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="agent-card">
        <div class="agent-icon">✅</div>
        <div class="agent-title">Reviewer Agent</div>
        <div class="agent-desc">
            Validates the work against the original plan.
            Checks quality and provides final approval.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Workflow Diagram
st.markdown("### 🔄 How They Work Together")
st.markdown("""
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   You       │────►│   Planner   │────►│   Executor  │────►│   Reviewer  │
│ (Objective) │     │  (Plan)     │     │  (Execute)  │     │  (Verify)   │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                                                                    │
                                                                    ▼
                                                            ┌─────────────┐
                                                            │   Final     │
                                                            │   Output    │
                                                            └─────────────┘
```
""")

# How to Use
st.markdown('<h2 class="section-title" id="how-to-use">📝 How to Use</h2>', unsafe_allow_html=True)

st.markdown("""
<div class="step-card step-1">
    <h4>Step 1: Create an Account</h4>
    <p>Register with your email and create a password. This keeps your tasks private and secure.</p>
</div>

<div class="step-card step-2">
    <h4>Step 2: Go to Dashboard</h4>
    <p>Navigate to the Dashboard page where you can create and manage your tasks.</p>
</div>

<div class="step-card step-3">
    <h4>Step 3: Enter Your Task</h4>
    <p>Describe what you want to accomplish in the text box. Be specific and detailed for best results.</p>
</div>

<div class="step-card step-4">
    <h4>Step 4: Submit & Wait</h4>
    <p>Click "Submit Task" and watch the agents work. The page auto-refreshes until completion.</p>
</div>
""", unsafe_allow_html=True)

# Example Tasks
st.markdown("### 💡 Example Tasks You Can Create")

examples = [
    ("📊 Business", "Create a marketing strategy for launching a new mobile fitness app targeting millennials"),
    ("📚 Education", "Develop a 4-week study plan for learning Python programming from scratch"),
    ("🍳 Lifestyle", "Design a weekly meal plan for a vegetarian diet with shopping list"),
    ("💼 Career", "Write a project proposal for implementing a customer feedback system"),
    ("🏋️ Health", "Create a 30-day fitness plan for beginners with home exercises"),
    ("✍️ Writing", "Outline a blog post series about sustainable living practices"),
]

col1, col2 = st.columns(2)
for i, (category, example) in enumerate(examples):
    with col1 if i % 2 == 0 else col2:
        st.markdown(f"""
        <div class="feature-box">
            <strong>{category}</strong><br>
            <span style="color: #4a5568;">{example}</span>
        </div>
        """, unsafe_allow_html=True)

# Task Actions
st.markdown("### ⚙️ Task Actions (After Completion)")

st.markdown("""
Once a task is completed, you have three options:

| Action | What it does |
|--------|--------------|
| **✏️ Rename** | Change the task name/objective for better organization |
| **🔄 Re-run** | Clear results and run the same task again for a fresh perspective |
| **➕ Continue** | Create a follow-up task that builds on the completed work |
""")

# Tips & Tricks
st.markdown('<h2 class="section-title" id="tips-tricks">💡 Tips & Tricks</h2>', unsafe_allow_html=True)

st.markdown("""
<div class="tip-box">
    <strong style="color:#1a202c;">🎯 Be Specific</strong><br>
    <span style="color:#2d3748;">Instead of "Write a plan", try "Write a 30-day social media marketing plan for a bakery targeting local customers"</span>
</div>

<div class="tip-box">
    <strong style="color:#1a202c;">📋 Include Context</strong><br>
    <span style="color:#2d3748;">Provide relevant details like target audience, constraints, preferences, or specific requirements.</span>
</div>

<div class="tip-box">
    <strong style="color:#1a202c;">🔄 Use Continue</strong><br>
    <span style="color:#2d3748;">Build on completed tasks using the "Continue" feature to create follow-up tasks with context.</span>
</div>

<div class="warning-box">
    <strong style="color:#1a202c;">⚠️ Session Note</strong><br>
    <span style="color:#2d3748;">Avoid refreshing the browser page (F5) while logged in, as this will log you out.
    Use the in-app navigation instead.</span>
</div>
""", unsafe_allow_html=True)

# FAQ
st.markdown('<h2 class="section-title">❓ Frequently Asked Questions</h2>', unsafe_allow_html=True)

with st.expander("How long does a task take?"):
    st.write("""
    Task completion time varies based on complexity:
    - Simple tasks: 30 seconds - 1 minute
    - Medium tasks: 1-3 minutes
    - Complex tasks: 3-5 minutes

    The page auto-refreshes, so you'll see the progress in real-time.
    """)

with st.expander("Can I edit a task while it's running?"):
    st.write("""
    No, you cannot edit a task while it's being processed. Wait for it to complete,
    then use the "Re-run" or "Rename" options.
    """)

with st.expander("What happens to my data?"):
    st.write("""
    Your tasks and data are stored securely in the database. Only you can access your tasks
    when logged into your account. Passwords are encrypted using industry-standard security.
    """)

with st.expander("Why did my task fail?"):
    st.write("""
    Tasks can fail due to:
    - Network connectivity issues
    - API rate limits
    - Very complex or unclear objectives

    Try re-running the task or simplifying your objective.
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #718096; padding: 1rem;">
    <p>Ready to get started? Head to the <strong>Dashboard</strong> and create your first task!</p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🚀 Go to Dashboard", use_container_width=True, type="primary"):
        st.switch_page("pages/1_dashboard.py")

# Render shared sidebar
if is_authenticated():
    render_sidebar(current_page="guide")
