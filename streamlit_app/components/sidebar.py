import streamlit as st
from streamlit_app.utils import sync_get_me, sync_logout, clear_authentication


def render_sidebar(current_page: str = "home"):
    """Render consistent sidebar navigation across all pages.

    Args:
        current_page: The current page identifier ('home', 'dashboard', 'history', 'profile', 'guide')
    """
    # Professional sidebar styling - Warm Orange Theme
    st.markdown("""
    <style>
        /* ============================================
           SIDEBAR - WARM ORANGE THEME
           ============================================ */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #9a3412 0%, #c2410c 100%);
        }

        /* Hide sidebar collapse button - prevent accidental collapse */
        [data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"],
        [data-testid="stSidebar"] button[kind="header"],
        [data-testid="stSidebar"] [data-testid="baseButton-header"],
        [data-testid="stSidebar"] [data-testid="baseButton-headerNoPadding"],
        [data-testid="collapsedControl"],
        [data-testid="stSidebarCollapsedControl"] {
            display: none !important;
            visibility: hidden !important;
        }

        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
            color: rgba(255, 255, 255, 0.9);
        }

        [data-testid="stSidebar"] hr {
            border-color: rgba(255, 255, 255, 0.1);
        }

        /* User Profile Card */
        .sidebar-profile {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 1.25rem;
            margin-bottom: 1.5rem;
            border: 1px solid rgba(255, 255, 255, 0.15);
            display: flex;
            align-items: center;
            gap: 0.875rem;
        }

        .sidebar-avatar {
            width: 48px;
            height: 48px;
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 1.1rem;
            flex-shrink: 0;
            background: linear-gradient(135deg, #f97316 0%, #fb923c 100%);
            color: white;
            box-shadow: 0 4px 12px rgba(249, 115, 22, 0.4);
        }

        .sidebar-avatar img {
            width: 100%;
            height: 100%;
            border-radius: 14px;
            object-fit: cover;
        }

        .sidebar-user-info {
            overflow: hidden;
        }

        .sidebar-username {
            font-weight: 600;
            color: #ffffff;
            font-size: 1rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            letter-spacing: -0.01em;
        }

        .sidebar-role {
            color: rgba(255, 255, 255, 0.7);
            font-size: 0.8rem;
            margin-top: 0.125rem;
        }

        /* Navigation Section */
        .nav-label {
            color: rgba(255, 255, 255, 0.5);
            font-size: 0.7rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            padding: 0 0.5rem;
            margin-bottom: 0.75rem;
        }

        /* Sidebar Divider */
        .sidebar-divider {
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            margin: 1.25rem 0;
        }

        /* Sidebar Button Overrides */
        [data-testid="stSidebar"] .stButton > button {
            background: rgba(255, 255, 255, 0.1) !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            color: rgba(255, 255, 255, 0.95) !important;
            border-radius: 10px !important;
            font-weight: 500 !important;
            transition: all 0.2s ease !important;
        }

        [data-testid="stSidebar"] .stButton > button:hover {
            background: rgba(255, 255, 255, 0.2) !important;
            border-color: rgba(255, 255, 255, 0.25) !important;
            transform: translateX(4px);
        }

        [data-testid="stSidebar"] .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #f97316 0%, #fb923c 100%) !important;
            border: none !important;
            color: white !important;
            box-shadow: 0 4px 12px rgba(249, 115, 22, 0.4) !important;
        }

        [data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
            box-shadow: 0 6px 16px rgba(249, 115, 22, 0.5) !important;
        }

        /* Ensure all navigation buttons have consistent height */
        [data-testid="stSidebar"] .stButton > button {
            min-height: 42px !important;
            height: 42px !important;
            padding: 0.5rem 0.75rem !important;
            font-size: 0.85rem !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }

        /* Ensure main content text is dark */
        .main p, .main span, .main div, .main h1, .main h2, .main h3, .main h4, .main h5, .main h6 {
            color: #1c1917;
        }

        /* Sidebar specific text stays white */
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] div,
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            color: rgba(255, 255, 255, 0.9) !important;
        }
    </style>
    """, unsafe_allow_html=True)

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
                avatar_html = f'<img src="data:image/png;base64,{profile_photo}">'
            else:
                avatar_html = f'{first_letter}'

            st.markdown(f"""
            <div class="sidebar-profile">
                <div class="sidebar-avatar">
                    {avatar_html}
                </div>
                <div class="sidebar-user-info">
                    <div class="sidebar-username">{username}</div>
                    <div class="sidebar-role">Task Manager</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Navigation label
        st.markdown('<div class="nav-label">Navigation</div>', unsafe_allow_html=True)

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

        st.markdown("<div style='margin-top:0.75rem;'></div>", unsafe_allow_html=True)

        btn_type = "primary" if current_page == "guide" else "secondary"
        if st.button("📖 How It Works", use_container_width=True, key="nav_guide", type=btn_type):
            st.switch_page("pages/4_how_it_works.py")

        st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

        if st.button("🚪 Logout", use_container_width=True, key="nav_logout"):
            sync_logout()
            clear_authentication()
            st.rerun()
