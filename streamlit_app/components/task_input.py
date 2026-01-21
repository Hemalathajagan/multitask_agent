import streamlit as st
from streamlit_app.utils import sync_create_task


def render_task_input():
    """Render the task input form."""
    st.subheader("New Task")

    with st.form("task_form", clear_on_submit=True):
        objective = st.text_area(
            "Task Objective",
            placeholder="Describe what you want to accomplish...\n\nExample: Create a marketing plan for launching a new mobile fitness app targeting young professionals.",
            height=150
        )
        submitted = st.form_submit_button("Submit Task", use_container_width=True, type="primary")

        if submitted:
            if not objective or len(objective) < 10:
                st.error("Please provide a more detailed objective (at least 10 characters)")
                return

            with st.spinner("Creating task..."):
                result = sync_create_task(objective)

            if result["success"]:
                st.session_state.current_task_id = result["data"]["id"]
                st.session_state.messages = []
                st.success(f"Task created! ID: {result['data']['id']}")
                st.rerun()
            else:
                st.error(result["error"])
