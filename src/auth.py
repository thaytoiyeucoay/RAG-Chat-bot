# src/auth.py (Phiên bản cuối cùng - Bắt lỗi chung, hoạt động ổn định)
import streamlit as st
from supabase import Client

# KHÔNG CẦN IMPORT AuthException nữa

def display_auth_form(supabase_client: Client):
    """Hiển thị form đăng nhập và đăng ký."""
    st.title("Chào mừng đến với CS50 Assistant!")
    st.write("Vui lòng đăng nhập hoặc tạo tài khoản để tiếp tục.")

    tab1, tab2 = st.tabs(["🔐 Đăng nhập", "✍️ Đăng ký"])

    # Form Đăng nhập
    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Mật khẩu", type="password")
            login_button = st.form_submit_button("Đăng nhập")

            if login_button:
                if email and password:
                    # >>> THAY ĐỔI QUAN TRỌNG: Bắt lỗi Exception chung
                    try:
                        user = supabase_client.auth.sign_in_with_password({
                            "email": email,
                            "password": password
                        })
                        st.session_state['user_session'] = user
                        st.rerun()
                    except Exception as e:
                        # Hiển thị thông báo lỗi thực tế từ Supabase
                        st.error(f"Lỗi đăng nhập: {e}")
                else:
                    st.warning("Vui lòng nhập đầy đủ email và mật khẩu.")

    # Form Đăng ký
    with tab2:
        with st.form("register_form"):
            full_name = st.text_input("Tên đầy đủ")
            email = st.text_input("Email đăng ký")
            password = st.text_input("Mật khẩu mới", type="password")
            register_button = st.form_submit_button("Đăng ký")

            if register_button:
                if full_name and email and password:
                    # >>> THAY ĐỔI QUAN TRỌNG: Bắt lỗi Exception chung
                    try:
                        user = supabase_client.auth.sign_up({
                            "email": email,
                            "password": password,
                            "options": {
                                "data": {
                                    'full_name': full_name,
                                }
                            }
                        })
                        st.success("Đăng ký thành công! Vui lòng đăng nhập.")
                    except Exception as e:
                        # Hiển thị thông báo lỗi thực tế từ Supabase
                        st.error(f"Lỗi đăng ký: {e}")
                else:
                    st.warning("Vui lòng điền đầy đủ thông tin.")