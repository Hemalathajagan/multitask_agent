import streamlit as st
from streamlit_app.utils import sync_login, sync_register, set_authenticated


def render_login_form():
    """Render the login form with warm orange theme."""

    # Custom styling for login form
    st.markdown("""
    <style>
        /* Form container styling */
        .login-form-container {
            padding: 1rem 0;
        }

        .form-header {
            text-align: center;
            margin-bottom: 1.5rem;
        }

        .form-header h3 {
            color: #1c1917 !important;
            font-size: 1.5rem;
            font-weight: 700;
            margin: 0 0 0.5rem 0;
        }

        .form-header p {
            color: #78716c !important;
            font-size: 0.9rem;
            margin: 0;
        }

        .form-divider {
            display: flex;
            align-items: center;
            margin: 1.5rem 0;
            color: #a8a29e;
            font-size: 0.85rem;
        }

        .form-divider::before,
        .form-divider::after {
            content: '';
            flex: 1;
            height: 1px;
            background: #fed7aa;
        }

        .form-divider span {
            padding: 0 1rem;
        }

        /* =============================================
           COMPLETE INPUT STYLING - WITH EYE ICON SUPPORT
           ============================================= */

        /* Form container reset */
        [data-testid="stForm"] {
            background: transparent !important;
            border: none !important;
            padding: 0 !important;
        }

        /* Hide "press enter to submit form" text */
        [data-testid="stForm"] [data-testid="InputInstructions"],
        [data-testid="stForm"] [data-testid="stFormSubmitButton"] ~ div,
        [data-testid="stForm"] .stMarkdown small,
        [data-testid="stForm"] small,
        [data-testid="InputInstructions"],
        .stTextInput [data-testid="InputInstructions"],
        div[data-testid="InputInstructions"] {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
            overflow: hidden !important;
        }

        /* Label styling */
        [data-testid="stForm"] .stTextInput > label {
            color: #1c1917 !important;
            font-weight: 500 !important;
            font-size: 0.9rem !important;
        }

        /* The outer input wrapper - THIS gets the border (includes eye icon) */
        [data-testid="stForm"] [data-baseweb="input"] {
            background-color: #fffbf5 !important;
            border: 2px solid #fed7aa !important;
            border-top: 2px solid #fed7aa !important;
            border-bottom: 2px solid #fed7aa !important;
            border-left: 2px solid #fed7aa !important;
            border-right: 2px solid #fed7aa !important;
            border-radius: 12px !important;
            padding: 0 !important;
            overflow: hidden !important;
            min-height: 48px !important;
            display: flex !important;
            align-items: center !important;
        }

        [data-testid="stForm"] [data-baseweb="input"]:focus-within {
            border: 2px solid #f97316 !important;
            box-shadow: 0 0 0 3px rgba(249, 115, 22, 0.15) !important;
        }

        /* Inner wrapper - no border */
        [data-testid="stForm"] [data-baseweb="base-input"] {
            background: transparent !important;
            border: none !important;
            padding: 0 !important;
            flex: 1 !important;
        }

        /* The actual input field - no border, just padding */
        [data-testid="stForm"] input {
            background: transparent !important;
            border: none !important;
            padding: 0.875rem 1rem !important;
            color: #1c1917 !important;
            font-size: 0.95rem !important;
            width: 100% !important;
            outline: none !important;
            box-shadow: none !important;
        }

        [data-testid="stForm"] input::placeholder {
            color: #a8a29e !important;
        }

        /* Eye icon button styling */
        [data-testid="stForm"] [data-baseweb="input"] button {
            background: transparent !important;
            border: none !important;
            padding: 0 0.75rem !important;
            color: #78716c !important;
            cursor: pointer !important;
        }

        [data-testid="stForm"] [data-baseweb="input"] button:hover {
            color: #f97316 !important;
        }

        /* Submit button */
        [data-testid="stForm"] .stFormSubmitButton > button {
            background: linear-gradient(135deg, #f97316 0%, #ea580c 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 0.875rem 1.5rem !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
            box-shadow: 0 4px 14px rgba(249, 115, 22, 0.4) !important;
            transition: all 0.2s ease !important;
        }

        [data-testid="stForm"] .stFormSubmitButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(249, 115, 22, 0.5) !important;
        }

        /* Welcome back icon */
        .welcome-icon {
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #fff7ed 0%, #fed7aa 100%);
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 1rem auto;
            font-size: 1.75rem;
        }

        /* Override any Streamlit blue defaults */
        .stSpinner > div > div {
            border-top-color: #f97316 !important;
        }

        /* Links */
        a, a:visited {
            color: #ea580c !important;
        }

        /* Success/Error/Info messages */
        .stSuccess {
            background-color: #f0fdf4 !important;
            color: #166534 !important;
        }

        .stError {
            background-color: #fef2f2 !important;
            color: #b91c1c !important;
        }

        .stWarning {
            background-color: #fffbeb !important;
            color: #b45309 !important;
        }

        .stInfo {
            background-color: #fff7ed !important;
            color: #c2410c !important;
        }

        /* Checkbox */
        .stCheckbox > label > span {
            color: #1c1917 !important;
        }

        [data-testid="stCheckbox"] > label > div:first-child {
            background-color: #f97316 !important;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="form-header">
        <h3>Sign In</h3>
        <p>Sign in to continue to your dashboard</p>
    </div>
    """, unsafe_allow_html=True)

    # Check if email should be pre-filled from registration
    default_email = st.session_state.get("registered_email", "")
    if default_email:
        # Clear it after using
        st.session_state.registered_email = ""

    with st.form("login_form"):
        email = st.text_input("Email Address", value=default_email, placeholder="your@email.com")
        password = st.text_input("Password", type="password", placeholder="Enter your password")

        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
        submitted = st.form_submit_button("Sign In", use_container_width=True)

        if submitted:
            if not email or not password:
                st.error("Please fill in all fields")
                return

            with st.spinner("Signing in..."):
                result = sync_login(email, password)

            if result["success"]:
                set_authenticated({"email": email}, result["data"]["access_token"])
                st.success("Welcome back! Redirecting...")
                st.rerun()
            else:
                st.error(result["error"])


def render_register_form():
    """Render the registration form with warm orange theme."""

    # Custom styling for register form
    st.markdown("""
    <style>
        /* Create account icon */
        .create-icon {
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #fff7ed 0%, #fed7aa 100%);
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 1rem auto;
            font-size: 1.75rem;
        }

        .password-hint {
            background: #fff7ed;
            border: 1px solid #fed7aa;
            border-radius: 10px;
            padding: 0.75rem 1rem;
            margin-top: 0.5rem;
            font-size: 0.8rem;
            color: #78716c;
        }

        .password-hint strong {
            color: #ea580c;
        }

    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="form-header">
        <h3>Create Account</h3>
        <p>Join us and start automating your tasks</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("register_form"):
        email = st.text_input("Email Address", placeholder="your@email.com")
        username = st.text_input("Username", placeholder="Choose a unique username")
        password = st.text_input("Password", type="password", placeholder="Min 8 characters")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter your password")

        st.markdown("""
        <div class="password-hint">
            <strong>Password requirements:</strong> At least 8 characters
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
        submitted = st.form_submit_button("Create Account", use_container_width=True)

        if submitted:
            if not email or not username or not password:
                st.error("Please fill in all fields")
                return

            if password != confirm_password:
                st.error("Passwords do not match")
                return

            if len(password) < 8:
                st.error("Password must be at least 8 characters")
                return

            with st.spinner("Creating your account..."):
                result = sync_register(email, username, password)

            if result["success"]:
                st.success("Account created successfully! Redirecting to login...")
                # Set flag to switch to login tab
                st.session_state.show_login_after_register = True
                st.session_state.registered_email = email
                st.rerun()
            else:
                st.error(result["error"])
