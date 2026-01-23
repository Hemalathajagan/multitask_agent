import streamlit as st
import sys
import base64
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from streamlit_app.utils import (
    init_session_state, is_authenticated, clear_authentication,
    sync_logout, sync_get_me, sync_update_profile, sync_change_password,
    sync_get_tasks, sync_update_photo
)
from streamlit_app.components import render_login_form, render_register_form

st.set_page_config(
    page_title="Profile - Multi-Agent Task Assistant",
    page_icon="👤",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    /* Hide default Streamlit page navigation */
    [data-testid="stSidebarNav"] { display: none !important; }

    .profile-header {
        background: linear-gradient(135deg, #ed8936 0%, #dd6b20 100%);
        padding: 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.5rem;
        text-align: center;
    }

    .profile-avatar-large {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        background: white;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 1rem auto;
        font-size: 3rem;
        color: #ed8936;
        font-weight: bold;
        overflow: hidden;
        border: 4px solid white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }

    .profile-avatar-large img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    .profile-card {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
    }

    .profile-card h3 {
        color: #2d3748;
        margin-bottom: 1.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e2e8f0;
    }

    .stat-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }

    .stat-box h2 {
        margin: 0;
        font-size: 2.5rem;
    }

    .stat-box p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }

    .info-item {
        display: flex;
        justify-content: space-between;
        padding: 0.75rem 0;
        border-bottom: 1px solid #e2e8f0;
    }

    .info-item:last-child {
        border-bottom: none;
    }

    .info-label {
        font-weight: 600;
        color: #4a5568;
    }

    .info-value {
        color: #2d3748;
    }

    .photo-upload-area {
        border: 2px dashed #cbd5e0;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        background: #f7fafc;
        cursor: pointer;
        transition: all 0.2s;
    }

    .photo-upload-area:hover {
        border-color: #667eea;
        background: #ebf4ff;
    }

    .security-tip {
        background: #ebf8ff;
        border-left: 4px solid #4299e1;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        margin-top: 1rem;
    }

    .security-tip h4 {
        color: #2b6cb0;
        margin: 0 0 0.5rem 0;
    }

    .security-tip p {
        color: #4a5568;
        margin: 0;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

init_session_state()


def render_auth_required():
    """Show login required message."""
    st.warning("Please login to view your profile.")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["Login", "Register"])
        with tab1:
            render_login_form()
        with tab2:
            render_register_form()


def render_profile():
    """Render the profile page."""
    # Get user info
    user_result = sync_get_me()
    if not user_result["success"]:
        st.error("Failed to load profile")
        return

    user = user_result["data"]

    # Get task stats
    tasks_result = sync_get_tasks(limit=100)
    tasks = tasks_result.get("data", []) if tasks_result["success"] else []
    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t["status"] == "completed"])

    # Get profile photo or first letter
    profile_photo = user.get("profile_photo")
    first_letter = user["username"][0].upper() if user.get("username") else "U"

    # Header with avatar
    if profile_photo:
        avatar_html = f'<img src="data:image/png;base64,{profile_photo}" alt="Profile Photo">'
    else:
        avatar_html = first_letter

    st.markdown(f"""
    <div class="profile-header">
        <div class="profile-avatar-large">{avatar_html}</div>
        <h1>{user['username']}</h1>
        <p>{user['email']}</p>
    </div>
    """, unsafe_allow_html=True)

    # Stats row
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="stat-box">
            <h2>{total_tasks}</h2>
            <p>Total Tasks</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="stat-box" style="background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);">
            <h2>{completed_tasks}</h2>
            <p>Completed</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        success_rate = int((completed_tasks / total_tasks * 100)) if total_tasks > 0 else 0
        st.markdown(f"""
        <div class="stat-box" style="background: linear-gradient(135deg, #ed8936 0%, #dd6b20 100%);">
            <h2>{success_rate}%</h2>
            <p>Success Rate</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Three column layout
    col1, col2, col3 = st.columns(3)

    with col1:
        # Profile Photo Card
        st.markdown("### 📷 Profile Photo")

        # Show current photo or placeholder
        if profile_photo:
            st.image(f"data:image/png;base64,{profile_photo}", width=150)
        else:
            st.markdown(f"""
            <div style="
                width: 150px;
                height: 150px;
                border-radius: 50%;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 4rem;
                font-weight: bold;
                margin: 0 auto;
            ">
                {first_letter}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Photo upload
        uploaded_file = st.file_uploader(
            "Upload new photo",
            type=["png", "jpg", "jpeg"],
            help="Max 2MB, PNG or JPG format"
        )

        if uploaded_file is not None:
            # Check file size (2MB limit)
            if uploaded_file.size > 2 * 1024 * 1024:
                st.error("File too large. Max size is 2MB")
            else:
                # Preview
                st.image(uploaded_file, width=100, caption="Preview")

                if st.button("💾 Save Photo", use_container_width=True):
                    with st.spinner("Uploading..."):
                        # Convert to base64
                        bytes_data = uploaded_file.getvalue()
                        base64_photo = base64.b64encode(bytes_data).decode()

                        result = sync_update_photo(base64_photo)

                    if result["success"]:
                        st.success("Photo updated!")
                        st.rerun()
                    else:
                        st.error(result["error"])

        if profile_photo:
            if st.button("🗑️ Remove Photo", use_container_width=True):
                result = sync_update_photo("")
                if result["success"]:
                    st.success("Photo removed!")
                    st.rerun()

    with col2:
        # Profile Information Card
        st.markdown("### 👤 Profile Settings")

        with st.form("profile_form"):
            new_username = st.text_input(
                "Username",
                value=user["username"],
                help="Your display name"
            )
            new_email = st.text_input(
                "Email",
                value=user["email"],
                help="Your email address"
            )

            submitted = st.form_submit_button("💾 Save Changes", use_container_width=True)

            if submitted:
                username_changed = new_username != user["username"]
                email_changed = new_email != user["email"]

                if not username_changed and not email_changed:
                    st.info("No changes to save")
                else:
                    with st.spinner("Updating profile..."):
                        result = sync_update_profile(
                            username=new_username if username_changed else None,
                            email=new_email if email_changed else None
                        )

                    if result["success"]:
                        st.success("Profile updated!")
                        st.rerun()
                    else:
                        st.error(result["error"])

        # Account Details
        st.markdown("---")
        st.markdown("##### 📋 Account Details")

        created_date = user.get('created_at', '')
        if created_date:
            created_date = created_date[:10] if isinstance(created_date, str) else str(created_date)[:10]

        st.markdown(f"""
        <div class="info-item">
            <span class="info-label">User ID</span>
            <span class="info-value">#{user['id']}</span>
        </div>
        <div class="info-item">
            <span class="info-label">Member Since</span>
            <span class="info-value">{created_date or 'N/A'}</span>
        </div>
        <div class="info-item">
            <span class="info-label">Tasks Created</span>
            <span class="info-value">{total_tasks}</span>
        </div>
        <div class="info-item">
            <span class="info-label">Tasks Completed</span>
            <span class="info-value">{completed_tasks}</span>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        # Change Password Card
        st.markdown("### 🔒 Security")

        with st.form("password_form"):
            current_password = st.text_input(
                "Current Password",
                type="password"
            )
            new_password = st.text_input(
                "New Password",
                type="password",
                help="Minimum 8 characters"
            )
            confirm_password = st.text_input(
                "Confirm Password",
                type="password"
            )

            submitted = st.form_submit_button("🔐 Change Password", use_container_width=True)

            if submitted:
                if not current_password or not new_password or not confirm_password:
                    st.error("Please fill all fields")
                elif len(new_password) < 8:
                    st.error("Password must be at least 8 characters")
                elif new_password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    with st.spinner("Changing password..."):
                        result = sync_change_password(current_password, new_password, confirm_password)

                    if result["success"]:
                        st.success("Password changed!")
                    else:
                        st.error(result["error"])

        # Security Tips
        st.markdown("""
        <div class="security-tip">
            <h4>🛡️ Security Tips</h4>
            <p>
                • Use a strong password<br>
                • Don't share credentials<br>
                • Change password regularly
            </p>
        </div>
        """, unsafe_allow_html=True)

    # Danger Zone
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

    with st.expander("⚠️ Danger Zone", expanded=False):
        st.warning("These actions are irreversible.")

        if st.button("🚪 Logout", use_container_width=True):
            sync_logout()
            clear_authentication()
            st.success("Logged out!")
            st.rerun()


# Sidebar
with st.sidebar:
    st.markdown("### 🤖 Task Assistant")
    st.markdown("---")

    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("app.py")

    if st.button("➕ New Task", use_container_width=True):
        st.switch_page("pages/1_dashboard.py")

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
    render_profile()
else:
    render_auth_required()
