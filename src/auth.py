import streamlit as st
from supabase import Client


def _inject_auth_css():
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    :root {
        --primary-600: #2563eb;
        --gray-50: #f8fafc;
        --gray-200: #e2e8f0;
        --gray-500: #64748b;
        --gray-700: #334155;
        --gray-900: #0f172a;
        --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.07), 0 2px 4px -2px rgb(0 0 0 / 0.07);
    }

    html, body, [data-testid="stAppViewContainer"] * {
        font-family: 'Inter', sans-serif !important;
    }

    [data-testid="stAppViewContainer"] {
        background: var(--gray-50);
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
    }

    .auth-container {
        max-width: 420px;
        width: 100%;
        margin: 2rem;
        padding: 2.5rem;
        background: white;
        border-radius: 16px;
        border: 1px solid var(--gray-200);
        box-shadow: var(--shadow-md);
    }

    .auth-hero {
        text-align: center;
        margin-bottom: 2rem;
    }

    .auth-logo {
        font-size: 2.5rem; /* Smaller logo */
        margin-bottom: 1rem;
        color: var(--primary-600);
    }

    .auth-hero h1 {
        font-size: 1.75rem;
        font-weight: 700;
        color: var(--gray-900);
        margin: 0 0 0.5rem 0;
    }

    .auth-hero p {
        color: var(--gray-500);
        font-size: 1rem;
        line-height: 1.6;
    }

    .stTabs [data-baseweb="tab-list"] {
        justify-content: center;
        border-bottom: 2px solid var(--gray-200);
        margin-bottom: 1.5rem;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 0.75rem 0.5rem !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        color: var(--gray-500);
        border-bottom: 2px solid transparent !important;
        margin: 0 1rem;
    }

    .stTabs [aria-selected="true"] {
        color: var(--primary-600) !important;
        border-bottom-color: var(--primary-600) !important;
    }

    .stTextInput > div > div > input,
    .stPassword > div > div > input {
        border-radius: 8px !important;
        border: 1px solid var(--gray-200) !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
    }

    .stTextInput > div > div > input:focus,
    .stPassword > div > div > input:focus {
        border-color: var(--primary-600) !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
    }

    .stButton > button {
        width: 100% !important;
        border-radius: 8px !important;
        padding: 0.75rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        background-color: var(--primary-600) !important;
        border: none !important;
    }
    
    .stButton > button:hover {
        filter: brightness(1.1);
    }

    .stAlert {
        border-radius: 8px !important;
    }

    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def display_auth_form(supabase_client: Client):
    """Hiển thị form đăng nhập và đăng ký với giao diện chuyên nghiệp."""
    _inject_auth_css()

    st.markdown(
        """
        <div class="auth-container">
            <div class="auth-hero">
                <div class="auth-logo">🎓</div>
                <h1>CS50 & Lịch sử Assistant</h1>
                <p>Trải nghiệm học tập thông minh với AI - Đăng nhập để khám phá kiến thức CS50 và Lịch sử Việt Nam</p>
            </div>
        """,
        unsafe_allow_html=True,
    )

    tab1, tab2 = st.tabs(["🔐 Đăng nhập", "✍️ Đăng ký"])

    # Form Đăng nhập
    with tab1:
        with st.form("login_form", clear_on_submit=False):
            st.markdown("### 🔐 Đăng nhập vào tài khoản")
            
            email = st.text_input("📧 Email", placeholder="your.email@example.com", help="Nhập địa chỉ email của bạn")
            password = st.text_input("🔒 Mật khẩu", type="password", placeholder="••••••••", help="Nhập mật khẩu của bạn")

            st.markdown("<br>", unsafe_allow_html=True)
            login_button = st.form_submit_button("🚀 Đăng nhập", use_container_width=True)
            
            st.markdown(
                """
                <div style="text-align: center; margin-top: 1rem;">
                    <p style="color: var(--gray-500); font-size: 0.875rem;">
                        Quên mật khẩu? <a href="#" style="color: var(--primary-600); text-decoration: none;">Liên hệ quản trị viên</a>
                    </p>
                </div>
                """, 
                unsafe_allow_html=True
            )

            if login_button:
                if email and password:
                    with st.spinner("🔄 Đang xác thực..."):
                        try:
                            user = supabase_client.auth.sign_in_with_password({
                                "email": email,
                                "password": password
                            })
                            st.session_state['user_session'] = user
                            st.success("✅ Đăng nhập thành công! Đang chuyển hướng...")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Lỗi đăng nhập: {e}")
                else:
                    st.warning("⚠️ Vui lòng nhập đầy đủ email và mật khẩu.")

    # Form Đăng ký
    with tab2:
        with st.form("register_form", clear_on_submit=True):
            st.markdown("### ✍️ Tạo tài khoản mới")
            
            full_name = st.text_input("👤 Tên đầy đủ", placeholder="Nguyễn Văn A", help="Nhập họ và tên của bạn")
            email = st.text_input("📧 Email đăng ký", placeholder="your.email@example.com", help="Email này sẽ dùng để đăng nhập")
            password = st.text_input("🔒 Mật khẩu mới", type="password", placeholder="Tối thiểu 6 ký tự", help="Tạo mật khẩu mạnh để bảo vệ tài khoản")

            st.markdown("<br>", unsafe_allow_html=True)
            register_button = st.form_submit_button("🎉 Tạo tài khoản", use_container_width=True)
            
            st.markdown(
                """
                <div style="text-align: center; margin-top: 1rem;">
                    <p style="color: var(--gray-500); font-size: 0.875rem;">
                        Bằng việc đăng ký, bạn đồng ý với 
                        <a href="#" style="color: var(--primary-600); text-decoration: none;">Điều khoản sử dụng</a>
                        và <a href="#" style="color: var(--primary-600); text-decoration: none;">Chính sách bảo mật</a>
                    </p>
                </div>
                """, 
                unsafe_allow_html=True
            )

            if register_button:
                if full_name and email and password:
                    if len(password) < 6:
                        st.warning("⚠️ Mật khẩu phải có ít nhất 6 ký tự.")
                    else:
                        with st.spinner("🔄 Đang tạo tài khoản..."):
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
                                st.success("🎉 Đăng ký thành công! Vui lòng chuyển sang tab Đăng nhập.")
                            except Exception as e:
                                st.error(f"❌ Lỗi đăng ký: {e}")
                else:
                    st.warning("⚠️ Vui lòng điền đầy đủ thông tin.")
    
    st.markdown("</div>", unsafe_allow_html=True)