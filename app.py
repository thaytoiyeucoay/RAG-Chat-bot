# app.py - Optimized Version
import nest_asyncio
nest_asyncio.apply()

import streamlit as st
import logging
from src.error_handler import safe_execute, handle_errors

# Lazy imports để giảm thời gian khởi động
@st.cache_resource
def get_components():
    from src.auth import display_auth_form
    from src.chatbot_ui import display_chatbot_interface
    from src.admin_ui import display_admin_interface
    from src.dashboard_ui import display_dashboard
    from src.profile_ui import display_profile_interface
    from src.rag_components import load_base_components
    return {
        'auth': display_auth_form,
        'chatbot': display_chatbot_interface,
        'admin': display_admin_interface,
        'dashboard': display_dashboard,
        'profile': display_profile_interface,
        'components': load_base_components
    }

st.set_page_config(
	page_title="CS50 & Lịch sử Chatbot",
	page_icon="🤖",
	layout="wide",
	menu_items={
		"Get help": "https://docs.streamlit.io/",
		"Report a bug": "https://github.com/streamlit/streamlit/issues",
		"About": "Trợ lý học tập CS50 & Lịch sử — xây dựng với Streamlit"
	}
)

# Tải components với error handling
components = safe_execute(get_components, {}, "Lỗi tải components")
if not components:
    st.error("Không thể khởi động ứng dụng")
    st.stop()

# Tải RAG components với lazy loading
def get_app_data():
    return safe_execute(components['components'], (None, None, None), "Lỗi tải dữ liệu")

vector_stores, prompt, supabase_client = get_app_data()

# Session state với tối ưu
if 'user_session' not in st.session_state:
    st.session_state['user_session'] = None

# Logic điều hướng được tối ưu
if st.session_state['user_session'] is None:
    safe_execute(
        lambda: components['auth'](supabase_client),
        None,
        "Lỗi hiển thị form đăng nhập"
    )
else:
    user = st.session_state['user_session'].user
    user_id = user.id
    user_name = user.user_metadata.get('full_name', 'Người dùng')
    user_email = user.email

    # Sidebar tối ưu
    st.sidebar.title("🛠️ Bảng Điều Khiển")
    
    ADMIN_EMAIL = "duy@gmail.com"
    is_admin = user_email == ADMIN_EMAIL

    # Menu options
    options = ["Chatbot", "Trang cá nhân"]
    if is_admin:
        options.extend(["Quản trị viên", "Dashboard"])
    
    app_mode = st.sidebar.radio("Chọn trang:", options, key="app_mode")
    st.sidebar.divider()

    # Route với error handling
    if app_mode == "Chatbot":
        safe_execute(
            lambda: components['chatbot'](vector_stores, prompt, supabase_client, user_id, user_name),
            None,
            "Lỗi tải chatbot"
        )
    elif app_mode == "Trang cá nhân":
        safe_execute(
            lambda: components['profile'](supabase_client, user),
            None,
            "Lỗi tải trang cá nhân"
        )
    elif app_mode == "Quản trị viên" and is_admin:
        safe_execute(components['admin'], None, "Lỗi tải trang quản trị")
    elif app_mode == "Dashboard" and is_admin:
        safe_execute(
            lambda: components['dashboard'](supabase_client),
            None,
            "Lỗi tải dashboard"
        )