import streamlit as st
from typing import List, Dict, Any


AGENT_COLORS = {
    "Planner": "#4CAF50",
    "Executor": "#2196F3",
    "Reviewer": "#FF9800",
    "System": "#9E9E9E",
}

AGENT_ICONS = {
    "Planner": "📋",
    "Executor": "⚡",
    "Reviewer": "✅",
    "System": "🖥️",
}

STATUS_PROGRESS = {
    "pending": 0,
    "planning": 25,
    "executing": 50,
    "reviewing": 75,
    "completed": 100,
    "failed": 100,
}


def render_progress_bar(status: str):
    """Render a progress bar based on task status."""
    progress = STATUS_PROGRESS.get(status, 0)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if status in ["planning", "executing", "reviewing", "completed"]:
            st.markdown("**📋 Planning** ✓")
        else:
            st.markdown("📋 Planning")

    with col2:
        if status in ["executing", "reviewing", "completed"]:
            st.markdown("**⚡ Executing** ✓")
        elif status == "planning":
            st.markdown("⚡ Executing")
        else:
            st.markdown("⚡ Executing")

    with col3:
        if status in ["reviewing", "completed"]:
            st.markdown("**✅ Reviewing** ✓")
        else:
            st.markdown("✅ Reviewing")

    with col4:
        if status == "completed":
            st.markdown("**🎉 Complete** ✓")
        elif status == "failed":
            st.markdown("**❌ Failed**")
        else:
            st.markdown("🎉 Complete")

    st.progress(progress / 100)


def render_agent_message(agent_name: str, content: str, timestamp: str = None):
    """Render a single agent message."""
    color = AGENT_COLORS.get(agent_name, "#666666")
    icon = AGENT_ICONS.get(agent_name, "🤖")

    st.markdown(
        f"""
        <div style="
            border-left: 4px solid {color};
            padding: 10px 15px;
            margin: 10px 0;
            background-color: rgba(0,0,0,0.05);
            border-radius: 0 8px 8px 0;
        ">
            <div style="font-weight: bold; color: {color}; margin-bottom: 5px;">
                {icon} {agent_name}
                {f'<span style="font-size: 0.8em; color: #888; margin-left: 10px;">{timestamp}</span>' if timestamp else ''}
            </div>
            <div style="white-space: pre-wrap;">{content}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_agent_chat(messages: List[Dict[str, Any]]):
    """Render the agent conversation."""
    if not messages:
        st.info("No messages yet. Submit a task to start the agent conversation.")
        return

    st.subheader("Agent Conversation")

    for msg in messages:
        agent_name = msg.get("agent_name", "Unknown")
        content = msg.get("content", "")
        timestamp = msg.get("timestamp", None)
        render_agent_message(agent_name, content, timestamp)
