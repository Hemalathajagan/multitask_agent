import streamlit as st
import base64


def render_user_header(user: dict):
    """Render user avatar header that links to profile."""
    if not user:
        return

    username = user.get("username", "User")
    first_letter = username[0].upper() if username else "U"
    profile_photo = user.get("profile_photo")

    # CSS for the header
    st.markdown("""
    <style>
        .user-header {
            position: fixed;
            top: 60px;
            right: 20px;
            z-index: 1000;
            display: flex;
            align-items: center;
            gap: 10px;
            background: white;
            padding: 8px 15px;
            border-radius: 25px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            cursor: pointer;
        }

        .user-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 1.2rem;
            color: white;
            background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
            overflow: hidden;
        }

        .user-avatar img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }

        .user-name {
            font-weight: 500;
            color: #2d3748;
            font-size: 0.9rem;
        }

        .user-header:hover {
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
        }
    </style>
    """, unsafe_allow_html=True)

    # Render avatar
    if profile_photo:
        avatar_content = f'<img src="data:image/png;base64,{profile_photo}" alt="Profile">'
    else:
        avatar_content = first_letter

    st.markdown(f"""
    <div class="user-header" onclick="window.location.href='pages/3_profile'">
        <div class="user-avatar">{avatar_content}</div>
        <span class="user-name">{username}</span>
    </div>
    """, unsafe_allow_html=True)


def render_avatar_circle(user: dict, size: int = 40):
    """Render just the avatar circle."""
    if not user:
        return ""

    username = user.get("username", "User")
    first_letter = username[0].upper() if username else "U"
    profile_photo = user.get("profile_photo")

    if profile_photo:
        return f'''
        <div style="
            width: {size}px;
            height: {size}px;
            border-radius: 50%;
            overflow: hidden;
            display: inline-flex;
            align-items: center;
            justify-content: center;
        ">
            <img src="data:image/png;base64,{profile_photo}"
                 style="width: 100%; height: 100%; object-fit: cover;"
                 alt="Profile">
        </div>
        '''
    else:
        return f'''
        <div style="
            width: {size}px;
            height: {size}px;
            border-radius: 50%;
            background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
            display: inline-flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: {size // 2}px;
        ">
            {first_letter}
        </div>
        '''


def get_avatar_html(user: dict, size: int = 40):
    """Get HTML for avatar that can be used in buttons."""
    if not user:
        return "👤"

    username = user.get("username", "User")
    first_letter = username[0].upper() if username else "U"
    profile_photo = user.get("profile_photo")

    if profile_photo:
        return f'<img src="data:image/png;base64,{profile_photo}" style="width:{size}px;height:{size}px;border-radius:50%;object-fit:cover;">'
    else:
        return first_letter
