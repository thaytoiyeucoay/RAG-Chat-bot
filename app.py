# app.py (Phiên bản Supabase Auth - Siêu gọn)
import nest_asyncio
nest_asyncio.apply()

import streamlit as st

from src.auth import display_auth_form
from src.chatbot_ui import display_chatbot_interface
from src.rag_components import load_base_components

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

# Tải các thành phần RAG và client Supabase
vector_stores, prompt, supabase_client = load_base_components()

# Kiểm tra xem đã có session người dùng chưa
if 'user_session' not in st.session_state:
    st.session_state['user_session'] = None

# Logic điều hướng chính
if st.session_state['user_session'] is None:
    # Nếu chưa đăng nhập, hiển thị form
    display_auth_form(supabase_client)
else:
    # Nếu đã đăng nhập, hiển thị giao diện chatbot
    user_id = st.session_state['user_session'].user.id
    user_name = st.session_state['user_session'].user.user_metadata.get('full_name', 'Người dùng')
    
    # Truyền thêm tên người dùng vào giao diện
    display_chatbot_interface(
        vector_stores=vector_stores,
        prompt=prompt,
        supabase_client=supabase_client,
        user_id=user_id,
        user_name=user_name
    )