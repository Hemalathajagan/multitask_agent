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
from streamlit_app.components import render_login_form, render_register_form, render_sidebar

st.set_page_config(
    page_title="Profile - Multi-Agent Task Assistant",
    page_icon="👤",
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
       PROFILE HEADER - WARM CORAL
       ============================================ */
    .profile-header {
        background: linear-gradient(135deg, #dc2626 0%, #ef4444 50%, #f87171 100%);
        padding: 2.5rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
        position: relative;
        overflow: hidden;
        box-shadow:
            0 20px 40px rgba(220, 38, 38, 0.3),
            0 0 0 1px rgba(255, 255, 255, 0.1) inset;
    }

    .profile-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 60%;
        height: 200%;
        background: radial-gradient(ellipse, rgba(255,255,255,0.15) 0%, transparent 70%);
        pointer-events: none;
    }

    .profile-avatar-large {
        width: 100px;
        height: 100px;
        border-radius: 50%;
        background: white;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 1rem auto;
        font-size: 2.5rem;
        color: #ef4444;
        font-weight: bold;
        overflow: hidden;
        border: 4px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        position: relative;
    }

    .profile-avatar-large img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    .profile-header h1 {
        margin: 0 0 0.25rem 0;
        font-size: 1.75rem;
        font-weight: 800;
        position: relative;
        letter-spacing: -0.03em;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .profile-header p {
        margin: 0;
        opacity: 0.95;
        font-size: 0.95rem;
        position: relative;
    }

    /* ============================================
       STAT BOXES
       ============================================ */
    .stat-box {
        background: white;
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        border: 1px solid rgba(234, 88, 12, 0.08);
        box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(234, 88, 12, 0.06);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .stat-box:hover {
        box-shadow: 0 8px 24px rgba(234, 88, 12, 0.12);
        transform: translateY(-4px);
    }

    .stat-box h2 {
        margin: 0;
        font-size: 2.25rem;
        font-weight: 800;
        color: #1c1917;
        letter-spacing: -0.03em;
    }

    .stat-box p {
        margin: 0.5rem 0 0 0;
        color: #78716c;
        font-size: 0.85rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .stat-box.accent {
        background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
        box-shadow: 0 8px 24px rgba(249, 115, 22, 0.3);
    }

    .stat-box.accent h2,
    .stat-box.accent p {
        color: white;
    }

    .stat-box.success {
        background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
        box-shadow: 0 8px 24px rgba(34, 197, 94, 0.3);
    }

    .stat-box.success h2,
    .stat-box.success p {
        color: white;
    }

    .stat-box.warning {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        box-shadow: 0 8px 24px rgba(245, 158, 11, 0.3);
    }

    .stat-box.warning h2,
    .stat-box.warning p {
        color: white;
    }

    /* ============================================
       INFO ITEMS
       ============================================ */
    .info-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 0;
        border-bottom: 1px solid #fed7aa;
    }

    .info-item:last-child {
        border-bottom: none;
    }

    .info-label {
        font-weight: 500;
        color: #78716c;
        font-size: 0.9rem;
    }

    .info-value {
        color: #1c1917;
        font-weight: 600;
        font-size: 0.9rem;
    }

    /* ============================================
       SECURITY TIP
       ============================================ */
    .security-tip {
        background: linear-gradient(135deg, #fff7ed, #ffedd5);
        border-left: 4px solid #f97316;
        padding: 1.25rem;
        border-radius: 0 14px 14px 0;
        margin-top: 1rem;
    }

    .security-tip h4 {
        color: #c2410c;
        margin: 0 0 0.5rem 0;
        font-size: 0.9rem;
        font-weight: 600;
    }

    .security-tip p {
        color: #57534e;
        margin: 0;
        font-size: 0.85rem;
        line-height: 1.6;
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
        border-color: #f97316 !important;
        box-shadow: 0 0 0 3px rgba(249, 115, 22, 0.15) !important;
        background-color: #ffffff !important;
    }

    .stTextInput > div > div > input::placeholder {
        color: #a8a29e !important;
    }

    /* Labels */
    .stTextInput > label,
    .stFileUploader > label {
        color: #1c1917 !important;
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

    /* ============================================
       FILE UPLOADER
       ============================================ */
    .stFileUploader > div {
        border-radius: 14px !important;
        background-color: #fffbf5 !important;
        border: 2px dashed #fed7aa !important;
    }

    .stFileUploader > div > div {
        color: #1c1917 !important;
    }

    /* Hide file uploader preview (filename and image) */
    .stFileUploader [data-testid="stFileUploaderFile"] {
        display: none !important;
    }

    /* Form submit button text */
    .stFormSubmitButton > button {
        background: linear-gradient(135deg, #f97316 0%, #ea580c 100%) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(249, 115, 22, 0.4) !important;
    }

    .stFormSubmitButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(249, 115, 22, 0.5) !important;
    }

    /* Links */
    a {
        color: #ea580c !important;
    }

    /* Progress bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #f97316, #ea580c) !important;
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
        <div class="stat-box accent">
            <h2>{total_tasks}</h2>
            <p>Total Tasks</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="stat-box success">
            <h2>{completed_tasks}</h2>
            <p>Completed</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        success_rate = int((completed_tasks / total_tasks * 100)) if total_tasks > 0 else 0
        st.markdown(f"""
        <div class="stat-box warning">
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
                background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
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
                help="Your email address",
                disabled=True
            )

            submitted = st.form_submit_button("💾 Save Changes", use_container_width=True)

            if submitted:
                username_changed = new_username != user["username"]

                if not username_changed:
                    st.info("No changes to save")
                else:
                    with st.spinner("Updating profile..."):
                        result = sync_update_profile(
                            username=new_username if username_changed else None,
                            email=None
                        )

                    if result["success"]:
                        st.success("Profile updated!")
                        st.rerun()
                    else:
                        st.error(result["error"])


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

    # Logout Button
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            sync_logout()
            clear_authentication()
            st.success("Logged out!")
            st.rerun()


# Render shared sidebar
if is_authenticated():
    render_sidebar(current_page="profile")

# Main content
if is_authenticated():
    render_profile()
else:
    render_auth_required()
