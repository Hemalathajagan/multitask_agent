import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from streamlit_app.utils import (
    init_session_state, is_authenticated,
    sync_get_tasks
)
from streamlit_app.components import render_login_form, render_register_form, render_sidebar

# Initialize session state first to check auth
from streamlit_app.utils import init_session_state as _init
_init()

# Check if authenticated for sidebar state
_is_auth = st.session_state.get("authenticated", False) and st.session_state.get("token") is not None

# Page config
st.set_page_config(
    page_title="Multi-Agent Task Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded" if _is_auth else "collapsed"
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
    [data-testid="stDecoration"] { visibility: hidden; }
    /* Hide header content but not the collapse control */
    header[data-testid="stHeader"] {
        background: transparent !important;
        height: 0 !important;
        min-height: 0 !important;
        padding: 0 !important;
    }

    /* Base font */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    .stApp {
        background: linear-gradient(180deg, #fffbf5 0%, #fef7ed 100%) !important;
    }

    .stApp > header {
        background: transparent !important;
    }

    .main .block-container {
        background: transparent !important;
        padding-top: 2rem !important;
    }

    section[data-testid="stSidebar"] > div {
        background: linear-gradient(180deg, #9a3412 0%, #c2410c 100%) !important;
    }

    /* Hide sidebar collapse/expand buttons - prevent accidental collapse */
    [data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebar"] button[kind="header"],
    [data-testid="stSidebar"] [data-testid="baseButton-header"],
    [data-testid="stSidebar"] [data-testid="baseButton-headerNoPadding"],
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"] {
        display: none !important;
        visibility: hidden !important;
    }

    /* ============================================
       PROFESSIONAL HEADER - WARM ORANGE
       ============================================ */
    .hero-section {
        background: linear-gradient(135deg, #ea580c 0%, #f97316 50%, #fb923c 100%);
        padding: 3rem 2.5rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
        box-shadow:
            0 20px 40px rgba(234, 88, 12, 0.3),
            0 0 0 1px rgba(255, 255, 255, 0.1) inset;
    }

    .hero-section::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 60%;
        height: 200%;
        background: radial-gradient(ellipse, rgba(255,255,255,0.15) 0%, transparent 70%);
        pointer-events: none;
    }

    .hero-section::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
    }

    .hero-title {
        font-size: 2.25rem;
        font-weight: 800;
        margin: 0 0 0.5rem 0;
        letter-spacing: -0.03em;
        line-height: 1.2;
        position: relative;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .hero-subtitle {
        font-size: 1.1rem;
        font-weight: 400;
        margin: 0;
        opacity: 0.95;
        position: relative;
        letter-spacing: -0.01em;
    }

    /* ============================================
       STATS GRID - WARM COLORS
       ============================================ */
    .stats-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1.25rem;
        margin-bottom: 2rem;
    }

    .stat-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        position: relative;
        overflow: hidden;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid rgba(234, 88, 12, 0.08);
        box-shadow:
            0 1px 3px rgba(0,0,0,0.04),
            0 4px 12px rgba(234, 88, 12, 0.06);
    }

    .stat-card:hover {
        transform: translateY(-4px);
        box-shadow:
            0 12px 24px rgba(234, 88, 12, 0.12),
            0 4px 8px rgba(0,0,0,0.04);
    }

    .stat-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        border-radius: 16px 16px 0 0;
    }

    .stat-card.blue::before { background: linear-gradient(90deg, #f97316, #ea580c); }
    .stat-card.green::before { background: linear-gradient(90deg, #22c55e, #16a34a); }
    .stat-card.orange::before { background: linear-gradient(90deg, #f59e0b, #d97706); }
    .stat-card.purple::before { background: linear-gradient(90deg, #ef4444, #dc2626); }

    .stat-icon-wrapper {
        width: 52px;
        height: 52px;
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }

    .stat-card.blue .stat-icon-wrapper { background: linear-gradient(135deg, #fff7ed, #fed7aa); }
    .stat-card.green .stat-icon-wrapper { background: linear-gradient(135deg, #f0fdf4, #bbf7d0); }
    .stat-card.orange .stat-icon-wrapper { background: linear-gradient(135deg, #fffbeb, #fde68a); }
    .stat-card.purple .stat-icon-wrapper { background: linear-gradient(135deg, #fef2f2, #fecaca); }

    .stat-number {
        font-size: 2.5rem;
        font-weight: 800;
        color: #1c1917;
        line-height: 1;
        margin-bottom: 0.25rem;
        letter-spacing: -0.03em;
    }

    .stat-label {
        font-size: 0.875rem;
        font-weight: 500;
        color: #78716c;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* ============================================
       SECTION HEADERS
       ============================================ */
    .section-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1.25rem;
    }

    .section-icon {
        width: 36px;
        height: 36px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
        background: linear-gradient(135deg, #ea580c, #f97316);
        color: white;
    }

    .section-title {
        font-size: 1.125rem;
        font-weight: 700;
        color: #1c1917;
        margin: 0;
        letter-spacing: -0.02em;
    }

    /* ============================================
       ACTION BUTTONS
       ============================================ */
    .action-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 1rem;
        margin-bottom: 2rem;
    }

    .action-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: 2px solid transparent;
        box-shadow: 0 2px 8px rgba(234, 88, 12, 0.06);
    }

    .action-card:hover {
        border-color: #f97316;
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(249, 115, 22, 0.2);
    }

    .action-card.primary {
        background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
        color: white;
    }

    .action-card.primary:hover {
        box-shadow: 0 8px 24px rgba(249, 115, 22, 0.4);
    }

    .action-icon {
        width: 56px;
        height: 56px;
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        margin: 0 auto 1rem auto;
        background: rgba(249, 115, 22, 0.1);
    }

    .action-card.primary .action-icon {
        background: rgba(255,255,255,0.2);
    }

    .action-title {
        font-size: 1rem;
        font-weight: 600;
        margin: 0 0 0.25rem 0;
    }

    .action-desc {
        font-size: 0.85rem;
        opacity: 0.8;
        margin: 0;
    }

    /* ============================================
       ACTIVITY LIST
       ============================================ */
    .activity-list {
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
    }

    .activity-card {
        background: white;
        border-radius: 14px;
        padding: 1rem 1.25rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        transition: all 0.2s ease;
        border: 1px solid rgba(234, 88, 12, 0.08);
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }

    .activity-card:hover {
        border-color: #f97316;
        box-shadow: 0 4px 12px rgba(249, 115, 22, 0.12);
        transform: translateX(4px);
    }

    .activity-indicator {
        width: 44px;
        height: 44px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.25rem;
        flex-shrink: 0;
    }

    .activity-indicator.completed { background: linear-gradient(135deg, #f0fdf4, #bbf7d0); }
    .activity-indicator.pending { background: linear-gradient(135deg, #fafaf9, #e7e5e4); }
    .activity-indicator.active { background: linear-gradient(135deg, #fff7ed, #fed7aa); }
    .activity-indicator.failed { background: linear-gradient(135deg, #fef2f2, #fecaca); }

    .activity-content {
        flex: 1;
        min-width: 0;
    }

    .activity-title {
        font-size: 0.95rem;
        font-weight: 600;
        color: #1c1917;
        margin: 0 0 0.25rem 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .activity-meta {
        font-size: 0.8rem;
        color: #78716c;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .activity-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }

    .activity-badge.completed { background: #bbf7d0; color: #166534; }
    .activity-badge.pending { background: #e7e5e4; color: #57534e; }
    .activity-badge.planning { background: #fed7aa; color: #c2410c; }
    .activity-badge.executing { background: #fde68a; color: #b45309; }
    .activity-badge.reviewing { background: #fecaca; color: #b91c1c; }
    .activity-badge.failed { background: #fecaca; color: #b91c1c; }

    /* ============================================
       EMPTY STATE
       ============================================ */
    .empty-state-card {
        background: white;
        border-radius: 20px;
        padding: 4rem 2rem;
        text-align: center;
        border: 2px dashed #fed7aa;
    }

    .empty-icon {
        font-size: 4rem;
        margin-bottom: 1.5rem;
        opacity: 0.4;
    }

    .empty-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #292524;
        margin: 0 0 0.5rem 0;
    }

    .empty-desc {
        font-size: 0.95rem;
        color: #78716c;
        margin: 0;
    }

    /* ============================================
       AUTH STYLES
       ============================================ */
    .auth-wrapper {
        min-height: 80vh;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .auth-card {
        background: white;
        border-radius: 24px;
        padding: 3rem;
        width: 100%;
        max-width: 420px;
        box-shadow:
            0 25px 50px rgba(234, 88, 12, 0.15),
            0 0 0 1px rgba(234, 88, 12, 0.05);
    }

    .auth-header {
        text-align: center;
        margin-bottom: 2.5rem;
    }

    .auth-logo {
        width: 72px;
        height: 72px;
        border-radius: 20px;
        background: linear-gradient(135deg, #ea580c 0%, #f97316 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        margin: 0 auto 1.25rem auto;
        box-shadow: 0 8px 24px rgba(234, 88, 12, 0.3);
    }

    .auth-title {
        font-size: 1.75rem;
        font-weight: 800;
        color: #1c1917;
        margin: 0 0 0.5rem 0;
        letter-spacing: -0.03em;
    }

    .auth-subtitle {
        font-size: 0.95rem;
        color: #78716c;
        margin: 0;
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
        border-color: #d6d3d1 !important;
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
    .stMultiSelect > label,
    .stFileUploader > label {
        color: #1c1917 !important;
    }

    /* All text elements */
    p, span, div, h1, h2, h3, h4, h5, h6 {
        color: #1c1917;
    }

    /* Streamlit markdown text */
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

    .stSelectbox > div > div:focus-within {
        border-color: #f97316 !important;
    }

    /* Multi-select */
    .stMultiSelect > div > div {
        background-color: #fffbf5 !important;
        border: 2px solid #fed7aa !important;
        border-radius: 12px !important;
        color: #1c1917 !important;
    }

    /* Expander */
    .streamlit-expanderHeader {
        color: #1c1917 !important;
        background-color: #fff7ed !important;
        border-radius: 10px !important;
    }

    .streamlit-expanderContent {
        color: #1c1917 !important;
    }

    /* ============================================
       TAB OVERRIDES
       ============================================ */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: #fafaf9;
        padding: 0.5rem;
        border-radius: 14px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
    }

    .stTabs [aria-selected="true"] {
        background: white !important;
        box-shadow: 0 2px 8px rgba(234, 88, 12, 0.1);
    }

    /* ============================================
       STREAMLIT DEFAULT OVERRIDES
       ============================================ */
    /* Progress bar */
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

    a:hover {
        color: #c2410c !important;
    }

    /* Info box */
    .stAlert[data-baseweb="notification"] {
        background-color: #fff7ed !important;
        border-left-color: #f97316 !important;
    }

    /* Checkbox and radio */
    .stCheckbox > label > div[data-testid="stMarkdownContainer"] > p,
    .stRadio > label > div[data-testid="stMarkdownContainer"] > p {
        color: #1c1917 !important;
    }

    /* Selectbox dropdown */
    [data-baseweb="select"] > div {
        background-color: #fffbf5 !important;
        border-color: #fed7aa !important;
    }

    [data-baseweb="popover"] {
        background-color: #fffbf5 !important;
    }

    [data-baseweb="menu"] {
        background-color: #fffbf5 !important;
    }

    [data-baseweb="menu"] li:hover {
        background-color: #fff7ed !important;
    }

    /* Widget labels */
    .stSelectbox > label,
    .stMultiSelect > label,
    .stSlider > label,
    .stNumberInput > label {
        color: #1c1917 !important;
    }

    /* Slider */
    .stSlider > div > div > div > div {
        background-color: #f97316 !important;
    }

    /* Number input */
    .stNumberInput > div > div > input {
        background-color: #fffbf5 !important;
        border-color: #fed7aa !important;
        color: #1c1917 !important;
    }

    /* Date input */
    .stDateInput > div > div > input {
        background-color: #fffbf5 !important;
        border-color: #fed7aa !important;
        color: #1c1917 !important;
    }

    /* Dataframe */
    .stDataFrame {
        border-color: #fed7aa !important;
    }

    /* Code blocks */
    .stCodeBlock {
        background-color: #1c1917 !important;
    }

    /* Toast notifications */
    [data-testid="stToast"] {
        background-color: #fff7ed !important;
        border-color: #f97316 !important;
    }

    /* Hide "press enter to submit form" globally */
    [data-testid="InputInstructions"] {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
init_session_state()


def render_auth_page():
    """Render the authentication page."""
    # Hide sidebar completely on auth page
    st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none; }
        [data-testid="collapsedControl"] { display: none; }

        /* Hide "press enter to submit form" text */
        [data-testid="InputInstructions"],
        [data-testid="stForm"] small,
        .stTextInput small {
            display: none !important;
        }

        /* Auth page specific styling */
        .auth-page-container {
            max-width: 450px;
            margin: 0 auto;
            padding: 2rem 1rem;
        }

        /* Tab styling for auth */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0;
            background: #fff7ed !important;
            padding: 0.5rem;
            border-radius: 14px;
            border: 1px solid #fed7aa;
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 10px;
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            color: #78716c !important;
            background: transparent !important;
        }

        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #f97316 0%, #ea580c 100%) !important;
            color: white !important;
            box-shadow: 0 4px 12px rgba(249, 115, 22, 0.3);
        }

        .stTabs [data-baseweb="tab-highlight"] {
            display: none !important;
        }

        .stTabs [data-baseweb="tab-border"] {
            display: none !important;
        }

        /* Force all Streamlit blue to orange */
        .stSpinner > div > div {
            border-top-color: #f97316 !important;
        }

        /* Override widget focus states */
        [data-baseweb="input"]:focus-within {
            border-color: #f97316 !important;
            box-shadow: 0 0 0 1px #f97316 !important;
        }

        /* Success message */
        [data-testid="stAlert"][data-baseweb="notification"] {
            background-color: #fff7ed !important;
        }

        /* Checkbox when checked */
        [data-testid="stCheckbox"] svg {
            fill: #f97316 !important;
        }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])

    with col2:
        # Check if we should show login tab after registration
        if st.session_state.get("show_login_after_register"):
            # Show success message
            st.success(f"Account created for {st.session_state.get('registered_email', '')}! Please sign in.")
            # Clear the flag
            st.session_state.show_login_after_register = False
            default_tab = 0  # Login tab
        else:
            default_tab = 0

        tab1, tab2 = st.tabs(["Sign In", "Create Account"])

        with tab1:
            render_login_form()

        with tab2:
            render_register_form()


def render_home():
    """Render the home page."""
    # Hero Section
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">Welcome back</h1>
        <p class="hero-subtitle">Manage your AI-powered tasks and track progress in real-time</p>
    </div>
    """, unsafe_allow_html=True)

    # Get tasks for stats
    result = sync_get_tasks(limit=100)
    tasks = result.get("data", []) if result["success"] else []

    # Calculate stats
    total_tasks = len(tasks)
    completed = len([t for t in tasks if t["status"] == "completed"])
    in_progress = len([t for t in tasks if t["status"] in ["planning", "executing", "reviewing"]])
    pending = len([t for t in tasks if t["status"] == "pending"])

    # Stats Grid using columns
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="stat-card blue">
            <div class="stat-icon-wrapper">📊</div>
            <div class="stat-number">{total_tasks}</div>
            <div class="stat-label">Total Tasks</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="stat-card green">
            <div class="stat-icon-wrapper">✓</div>
            <div class="stat-number">{completed}</div>
            <div class="stat-label">Completed</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="stat-card orange">
            <div class="stat-icon-wrapper">⚡</div>
            <div class="stat-number">{in_progress}</div>
            <div class="stat-label">In Progress</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="stat-card purple">
            <div class="stat-icon-wrapper">⏳</div>
            <div class="stat-number">{pending}</div>
            <div class="stat-label">Pending</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # Quick Actions Section
    st.markdown("""
    <div class="section-header">
        <div class="section-icon">⚡</div>
        <h2 class="section-title">Quick Actions</h2>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("➕  Create New Task", use_container_width=True, type="primary"):
            st.switch_page("pages/1_dashboard.py")

    with col2:
        if st.button("📜  View All Tasks", use_container_width=True):
            st.switch_page("pages/2_history.py")

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # Recent Activity Section
    st.markdown("""
    <div class="section-header">
        <div class="section-icon">🕐</div>
        <h2 class="section-title">Recent Activity</h2>
    </div>
    """, unsafe_allow_html=True)

    if tasks:
        for task in tasks[:5]:
            status_emoji = {
                "pending": "⏳",
                "planning": "📋",
                "executing": "⚡",
                "reviewing": "🔍",
                "completed": "✅",
                "failed": "❌"
            }.get(task["status"], "❓")

            indicator_class = {
                "pending": "pending",
                "planning": "active",
                "executing": "active",
                "reviewing": "active",
                "completed": "completed",
                "failed": "failed"
            }.get(task["status"], "pending")

            col1, col2 = st.columns([6, 1])
            with col1:
                st.markdown(f"""
                <div class="activity-card">
                    <div class="activity-indicator {indicator_class}">{status_emoji}</div>
                    <div class="activity-content">
                        <div class="activity-title">{task['objective'][:60]}{'...' if len(task['objective']) > 60 else ''}</div>
                        <div class="activity-meta">
                            <span class="activity-badge {task['status']}">{task['status']}</span>
                            <span>Task #{task['id']}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                if st.button("View", key=f"view_{task['id']}", use_container_width=True):
                    st.session_state.current_task_id = task["id"]
                    st.switch_page("pages/1_dashboard.py")
    else:
        st.markdown("""
        <div class="empty-state-card">
            <div class="empty-icon">📋</div>
            <h3 class="empty-title">No tasks yet</h3>
            <p class="empty-desc">Create your first task to get started with AI-powered automation</p>
        </div>
        """, unsafe_allow_html=True)


def render_main_app():
    """Render the main application."""
    # Render shared sidebar
    render_sidebar(current_page="home")

    # Main content
    render_home()


# Main app logic
if is_authenticated():
    render_main_app()
else:
    render_auth_page()
