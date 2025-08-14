import streamlit as st
from supabase import Client


def _inject_auth_css():
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] * {
        font-family: 'Inter', system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, 'Helvetica Neue', Helvetica, Arial !important;
    }
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(1200px 600px at 0% 0%, #f0f7ff 0%, #ffffff 50%) no-repeat;
    }
    .auth-hero {
        border-radius: 18px; padding: 22px 24px; margin-bottom: 12px;
        background: linear-gradient(135deg, rgba(99,102,241,0.12) 0%, rgba(59,130,246,0.06) 100%);
        border: 1px solid rgba(59,130,246,0.25);
    }
    .auth-hero h1 { font-size: 28px; font-weight: 800; color: #0f172a; margin: 0 0 6px 0; }
    .auth-hero p { color: #334155; margin: 0; }
    .auth-card {
        border-radius: 16px; padding: 18px 16px; border: 1px solid #e2e8f0; background: #ffffff;
        box-shadow: 0 6px 20px rgba(30,58,138,0.06);
    }
    .hint { color: #64748b; font-size: 13px; }
    .or-sep { text-align:center; color:#94a3b8; font-size:12px; margin: 6px 0; }
    .muted { color:#64748b; }
    /* Buttons */
    .stButton>button {
        border-radius: 12px; padding: 0.6rem 0.9rem;
        background: linear-gradient(180deg, #2563eb 0%, #1d4ed8 100%);
        border: 1px solid rgba(255,255,255,0.2); color: #fff; font-weight: 700;
    }
    .stButton>button:hover { filter: brightness(1.05); }
    .stTextInput>div>div>input { border-radius: 10px; }
    .stPassword>div>div>input { border-radius: 10px; }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def display_auth_form(supabase_client: Client):
    """Hiển thị form đăng nhập và đăng ký với giao diện chuyên nghiệp."""
    _inject_auth_css()

    st.markdown(
        """
        <div class="auth-hero">
            <div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap;">
                <div style="font-size:28px;">🛡️</div>
                <div>
                    <h1>Chào mừng đến với CS50 & Lịch sử Assistant</h1>
                    <p>Đăng nhập hoặc tạo tài khoản để bắt đầu trải nghiệm học tập tuyệt vời.</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab1, tab2 = st.tabs(["🔐 Đăng nhập", "✍️ Đăng ký"])

    # Form Đăng nhập
    with tab1:
        st.markdown("<div class='auth-card'>", unsafe_allow_html=True)
        with st.form("login_form", clear_on_submit=False):
            email = st.text_input("Email", placeholder="you@example.com")
            password = st.text_input("Mật khẩu", type="password", placeholder="••••••••")

            col1, col2 = st.columns([1,1])
            with col1:
                login_button = st.form_submit_button("Đăng nhập")
            with col2:
                st.caption("Quên mật khẩu? Hãy liên hệ quản trị viên.")

            if login_button:
                if email and password:
                    try:
                        user = supabase_client.auth.sign_in_with_password({
                            "email": email,
                            "password": password
                        })
                        st.session_state['user_session'] = user
                        st.success("Đăng nhập thành công! Đang chuyển hướng…")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Lỗi đăng nhập: {e}")
                else:
                    st.warning("Vui lòng nhập đầy đủ email và mật khẩu.")
        st.markdown("</div>", unsafe_allow_html=True)

    # Form Đăng ký
    with tab2:
        st.markdown("<div class='auth-card'>", unsafe_allow_html=True)
        with st.form("register_form", clear_on_submit=True):
            full_name = st.text_input("Tên đầy đủ", placeholder="Nguyễn Văn A")
            email = st.text_input("Email đăng ký", placeholder="you@example.com")
            password = st.text_input("Mật khẩu mới", type="password", placeholder="Tối thiểu 6 ký tự")

            col1, col2 = st.columns([1,1])
            with col1:
                register_button = st.form_submit_button("Tạo tài khoản")
            with col2:
                st.caption("Bằng việc đăng ký, bạn đồng ý với Điều khoản sử dụng.")

            if register_button:
                if full_name and email and password:
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
                        st.error(f"Lỗi đăng ký: {e}")
                else:
                    st.warning("Vui lòng điền đầy đủ thông tin.")
        st.markdown("</div>", unsafe_allow_html=True)