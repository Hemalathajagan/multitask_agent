import streamlit as st
from streamlit_app.utils import sync_get_me, sync_logout, clear_authentication


def render_sidebar(current_page: str = "home"):
    """Render consistent sidebar navigation across all pages.

    Args:
        current_page: The current page identifier ('home', 'dashboard', 'history', 'profile', 'guide')
    """
    # Get user info for avatar
    user_result = sync_get_me()
    user = user_result.get("data") if user_result["success"] else None

    with st.sidebar:
        # User profile section at top
        if user:
            username = user.get("username", "User")
            first_letter = username[0].upper()
            profile_photo = user.get("profile_photo")

            if profile_photo:
                avatar_html = f'<img src="data:image/png;base64,{profile_photo}" style="width:45px;height:45px;border-radius:50%;object-fit:cover;">'
            else:
                avatar_html = f'''
                <div style="
                    width:45px;height:45px;border-radius:50%;
                    background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    display:flex;align-items:center;justify-content:center;
                    color:white;font-weight:bold;font-size:1.2rem;
                ">{first_letter}</div>
                '''

            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:0.75rem;padding:0.75rem;background:#f8fafc;border-radius:10px;margin-bottom:1.5rem;">
                {avatar_html}
                <div>
                    <div style="font-weight:600;color:#1a202c;font-size:0.95rem;">{username}</div>
                    <div style="color:#718096;font-size:0.8rem;">Welcome back</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Navigation buttons - grouped together
        col1, col2 = st.columns(2)
        with col1:
            btn_type = "primary" if current_page == "home" else "secondary"
            if st.button("🏠 Home", use_container_width=True, key="nav_home", type=btn_type):
                st.switch_page("app.py")
        with col2:
            btn_type = "primary" if current_page == "dashboard" else "secondary"
            if st.button("➕ New Task", use_container_width=True, key="nav_task", type=btn_type):
                st.switch_page("pages/1_dashboard.py")

        col1, col2 = st.columns(2)
        with col1:
            btn_type = "primary" if current_page == "history" else "secondary"
            if st.button("📜 History", use_container_width=True, key="nav_history", type=btn_type):
                st.switch_page("pages/2_history.py")
        with col2:
            btn_type = "primary" if current_page == "profile" else "secondary"
            if st.button("👤 Profile", use_container_width=True, key="nav_profile", type=btn_type):
                st.switch_page("pages/3_profile.py")

        st.markdown("<div style='margin-top:0.5rem;'></div>", unsafe_allow_html=True)

        btn_type = "primary" if current_page == "guide" else "secondary"
        if st.button("📖 How It Works", use_container_width=True, key="nav_guide", type=btn_type):
            st.switch_page("pages/4_how_it_works.py")

        st.markdown("---")

        if st.button("🚪 Logout", use_container_width=True, key="nav_logout"):
            sync_logout()
            clear_authentication()
            st.rerun()
