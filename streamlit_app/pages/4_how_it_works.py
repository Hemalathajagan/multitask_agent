import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from streamlit_app.utils import init_session_state

st.set_page_config(
    page_title="How It Works - Multi-Agent Task Assistant",
    page_icon="📖",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .guide-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
    }

    .step-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
        border-left: 4px solid;
    }

    .step-card.step-1 { border-left-color: #667eea; }
    .step-card.step-2 { border-left-color: #48bb78; }
    .step-card.step-3 { border-left-color: #ed8936; }
    .step-card.step-4 { border-left-color: #e53e3e; }

    .agent-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
        height: 100%;
    }

    .agent-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }

    .agent-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #2d3748;
        margin-bottom: 0.5rem;
    }

    .agent-desc {
        color: #718096;
        font-size: 0.95rem;
    }

    .feature-box {
        background: #f7fafc;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }

    .tip-box {
        background: #ebf8ff;
        border-left: 4px solid #4299e1;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
    }

    .warning-box {
        background: #fffaf0;
        border-left: 4px solid #ed8936;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
    }

    .section-title {
        color: #2d3748;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
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
        <div style="background:#667eea;color:white;padding:0.5rem 1rem;border-radius:8px;text-align:center;font-weight:500;">
            What is this?
        </div>
    </a>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
    <a href="#how-to-use" style="text-decoration:none;">
        <div style="background:#48bb78;color:white;padding:0.5rem 1rem;border-radius:8px;text-align:center;font-weight:500;">
            How to Use
        </div>
    </a>
    """, unsafe_allow_html=True)
with col3:
    st.markdown("""
    <a href="#the-agents" style="text-decoration:none;">
        <div style="background:#ed8936;color:white;padding:0.5rem 1rem;border-radius:8px;text-align:center;font-weight:500;">
            The Agents
        </div>
    </a>
    """, unsafe_allow_html=True)
with col4:
    st.markdown("""
    <a href="#tips-tricks" style="text-decoration:none;">
        <div style="background:#e53e3e;color:white;padding:0.5rem 1rem;border-radius:8px;text-align:center;font-weight:500;">
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
    <strong>🎯 Be Specific</strong><br>
    Instead of "Write a plan", try "Write a 30-day social media marketing plan for a bakery targeting local customers"
</div>

<div class="tip-box">
    <strong>📋 Include Context</strong><br>
    Provide relevant details like target audience, constraints, preferences, or specific requirements.
</div>

<div class="tip-box">
    <strong>🔄 Use Continue</strong><br>
    Build on completed tasks using the "Continue" feature to create follow-up tasks with context.
</div>

<div class="warning-box">
    <strong>⚠️ Session Note</strong><br>
    Avoid refreshing the browser page (F5) while logged in, as this will log you out.
    Use the in-app navigation instead.
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

# Sidebar
with st.sidebar:
    st.markdown("### 📖 Guide")
    st.markdown("---")

    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("app.py")

    if st.button("➕ New Task", use_container_width=True):
        st.switch_page("pages/1_dashboard.py")

    if st.button("📜 History", use_container_width=True):
        st.switch_page("pages/2_history.py")

    if st.button("👤 Profile", use_container_width=True):
        st.switch_page("pages/3_profile.py")
