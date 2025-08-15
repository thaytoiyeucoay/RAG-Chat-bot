# src/chatbot_ui.py (Phiên bản cơ bản)
import streamlit as st
import os
import random
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI, HarmBlockThreshold, HarmCategory
from src.database import (
    save_message_to_db, load_messages_from_db,
    pin_conversation_to_db, load_pinned_conversations_from_db,
    load_specific_pinned_conversation, delete_pinned_conversation_from_db,
    search_messages_in_db, load_messages_up_to_db
)
from src.rag_components import format_chat_history
from src.utils import export_chat_to_pdf


def _inject_global_css():
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    :root {
        --primary-50: #eff6ff;
        --primary-100: #dbeafe;
        --primary-500: #3b82f6;
        --primary-600: #2563eb;
        --primary-700: #1d4ed8;
        --gray-50: #f8fafc;
        --gray-100: #f1f5f9;
        --gray-200: #e2e8f0;
        --gray-300: #cbd5e1;
        --gray-400: #94a3b8;
        --gray-500: #64748b;
        --gray-600: #475569;
        --gray-700: #334155;
        --gray-800: #1e293b;
        --gray-900: #0f172a;
        --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
        --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
        --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
    }
    
    * {
        box-sizing: border-box;
    }
    
    html, body, [data-testid="stAppViewContainer"] * {
        font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        font-feature-settings: 'cv02', 'cv03', 'cv04', 'cv11';
        text-rendering: optimizeLegibility;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
    
    /* App background with subtle gradient */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #ffffff 0%, var(--gray-50) 100%);
        color: var(--gray-900);
        min-height: 100vh;
    }
    
    /* Optimized sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--gray-50) 0%, #ffffff 100%);
        backdrop-filter: blur(10px);
        color: var(--gray-700);
        border-right: 1px solid var(--gray-200);
        width: 300px !important;
        box-shadow: var(--shadow-sm);
    }
    
    [data-testid="stSidebar"] > div {
        padding-top: 1rem;
    }
    
    /* Enhanced sidebar buttons */
    [data-testid="stSidebar"] .stButton > button,
    [data-testid="stSidebar"] .stDownloadButton > button {
        width: 100%;
        border-radius: 10px;
        border: 1px solid var(--gray-200);
        background: linear-gradient(135deg, #ffffff 0%, var(--gray-50) 100%);
        color: var(--gray-700);
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        font-size: 13px !important;
        font-weight: 500 !important;
        padding: 10px 14px !important;
        box-shadow: var(--shadow-sm);
    }
    
    [data-testid="stSidebar"] .stButton > button:hover,
    [data-testid="stSidebar"] .stDownloadButton > button:hover {
        transform: translateY(-1px) scale(1.02);
        box-shadow: var(--shadow-md);
        border-color: var(--primary-200);
        background: linear-gradient(135deg, #ffffff 0%, var(--primary-50) 100%);
    }
    
    /* Radio buttons enhancement */
    [data-testid="stSidebar"] .stRadio > div > label {
        padding: 8px 12px !important;
        border-radius: 8px;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        font-size: 13px !important;
        font-weight: 500 !important;
        cursor: pointer;
    }
    
    [data-testid="stSidebar"] .stRadio > div > label:hover {
        background: var(--primary-50);
        color: var(--primary-600);
        transform: translateX(2px);
    }
    
    /* Slider improvements */
    [data-testid="stSidebar"] .stSlider {
        margin-bottom: 20px !important;
    }
    
    [data-testid="stSidebar"] .stSlider > div > div > div {
        font-size: 12px !important;
        font-weight: 500 !important;
    }
    
    /* Hero card with glassmorphism */
    .hero-card {
        border-radius: 20px;
        padding: 28px 32px;
        background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(248,250,252,0.8) 100%);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,0.2);
        box-shadow: var(--shadow-xl), inset 0 1px 0 rgba(255,255,255,0.1);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .hero-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(59,130,246,0.3), transparent);
    }
    
    .hero-card:hover {
        transform: translateY(-3px);
        box-shadow: var(--shadow-xl), 0 25px 50px -12px rgba(0, 0, 0, 0.15);
    }
    
    .hero-title { 
        font-weight: 700; 
        font-size: 28px; 
        margin: 0 0 8px 0; 
        background: linear-gradient(135deg, var(--primary-600) 0%, #8b5cf6 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -0.025em;
    }
    
    .hero-subtitle { 
        color: var(--gray-600); 
        margin: 0; 
        font-size: 15px;
        line-height: 1.6;
        font-weight: 400;
    }
    
    .badge {
        display: inline-flex;
        align-items: center;
        padding: 6px 14px; 
        border-radius: 50px; 
        font-size: 12px; 
        font-weight: 600;
        background: linear-gradient(135deg, var(--primary-50) 0%, rgba(59,130,246,0.1) 100%);
        color: var(--primary-700); 
        border: 1px solid var(--primary-200); 
        margin-left: 12px;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        backdrop-filter: blur(10px);
    }
    
    .badge:hover {
        transform: scale(1.05);
        box-shadow: var(--shadow-md);
        background: linear-gradient(135deg, var(--primary-100) 0%, rgba(59,130,246,0.15) 100%);
    }
    
    /* Enhanced chat messages */
    [data-testid="stChatMessage"] {
        border-radius: 16px !important;
        padding: 14px 18px !important;
        margin-bottom: 12px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    [data-testid="stChatMessage"]:hover {
        transform: translateY(-1px);
        box-shadow: var(--shadow-lg);
    }
    
    /* User messages */
    [data-testid="stChatMessage"][data-testid*="user"] {
        background: linear-gradient(135deg, var(--primary-500) 0%, var(--primary-600) 100%);
        color: white;
        margin-left: 20%;
    }
    
    /* Assistant messages */
    [data-testid="stChatMessage"]:not([data-testid*="user"]) {
        background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, var(--gray-50) 100%);
        border: 1px solid var(--gray-200);
        margin-right: 20%;
    }
    
    /* Text styling in chat */
    [data-testid="stChatMessage"] div[class^="stMarkdown"] {
        line-height: 1.6 !important;
        text-align: left !important;
    }
    
    [data-testid="stChatMessage"] div[class^="stMarkdown"] p {
        margin-bottom: 8px !important;
        line-height: 1.6 !important;
        word-wrap: break-word !important;
        white-space: pre-wrap !important;
    }
    
    [data-testid="stChatMessage"] * {
        font-family: 'Inter', system-ui, sans-serif !important;
        text-rendering: optimizeLegibility !important;
    }
    
    /* Suggestions container with glassmorphism */
    .suggestions-container {
        margin: 20px 0;
        padding: 24px;
        background: linear-gradient(135deg, rgba(255,255,255,0.8) 0%, rgba(248,250,252,0.6) 100%);
        backdrop-filter: blur(20px);
        border-radius: 16px;
        border: 1px solid rgba(255,255,255,0.2);
        box-shadow: var(--shadow-lg);
    }
    
    /* Enhanced buttons */
    .stButton > button {
        border-radius: 12px !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        font-weight: 500 !important;
        font-size: 14px !important;
        padding: 10px 16px !important;
        border: 1px solid var(--gray-200) !important;
        background: linear-gradient(135deg, #ffffff 0%, var(--gray-50) 100%) !important;
        color: var(--gray-700) !important;
        box-shadow: var(--shadow-sm) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) scale(1.02) !important;
        box-shadow: var(--shadow-md) !important;
        border-color: var(--primary-300) !important;
        background: linear-gradient(135deg, #ffffff 0%, var(--primary-50) 100%) !important;
    }
    
    /* Chat input with modern styling */
    [data-testid="stChatInput"] {
        border-radius: 24px !important;
        border: 2px solid var(--gray-200) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        background: rgba(255,255,255,0.9) !important;
        backdrop-filter: blur(10px) !important;
        box-shadow: var(--shadow-sm) !important;
    }
    
    [data-testid="stChatInput"]:focus-within {
        border-color: var(--primary-400) !important;
        box-shadow: 0 0 0 4px rgba(59,130,246,0.1), var(--shadow-md) !important;
        transform: translateY(-1px) !important;
    }
    
    /* Improved responsive design */
    @media (max-width: 768px) {
        .hero-title { font-size: 22px; }
        .hero-subtitle { font-size: 13px; }
        .hero-card { padding: 20px 24px; }
        .suggestions-container { padding: 16px; margin: 16px 0; }
        [data-testid="stSidebar"] { width: 280px !important; }
        [data-testid="stChatMessage"] { margin-left: 5% !important; margin-right: 5% !important; }
    }
    
    /* Loading states with smooth animations */
    .stSpinner > div {
        border-color: var(--primary-200) !important;
        border-top-color: var(--primary-500) !important;
        animation: spin 1s cubic-bezier(0.4, 0, 0.2, 1) infinite !important;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--gray-100);
        border-radius: 3px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, var(--gray-300) 0%, var(--gray-400) 100%);
        border-radius: 3px;
        transition: all 0.2s ease;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, var(--primary-400) 0%, var(--primary-500) 100%);
    }
    
    /* Smooth page transitions */
    [data-testid="stAppViewContainer"] {
        animation: fadeIn 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    @keyframes fadeIn {
        0% { opacity: 0; transform: translateY(10px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    
    /* Enhanced focus states */
    button:focus-visible,
    input:focus-visible,
    [tabindex]:focus-visible {
        outline: 2px solid var(--primary-500) !important;
        outline-offset: 2px !important;
    }

    /* --- Enhanced Markdown Rendering --- */

    /* Code blocks styling */
    [data-testid="stChatMessage"] div[class^="stMarkdown"] pre {
        background-color: var(--gray-900);
        color: #e5e7eb; /* gray-200 */
        padding: 16px;
        border-radius: 12px;
        overflow-x: auto;
        font-family: 'SF Mono', 'Consolas', 'Menlo', monospace;
        font-size: 14px;
        line-height: 1.6;
        box-shadow: var(--shadow-lg);
        border: 1px solid var(--gray-800);
    }

    [data-testid="stChatMessage"] div[class^="stMarkdown"] code {
        background-color: var(--primary-50);
        color: var(--primary-600);
        padding: 3px 6px;
        border-radius: 6px;
        font-family: 'SF Mono', 'Consolas', 'Menlo', monospace;
        font-weight: 500;
    }

    /* Code inside pre should not have the inline style */
    [data-testid="stChatMessage"] div[class^="stMarkdown"] pre code {
        background-color: transparent;
        color: inherit;
        padding: 0;
        border-radius: 0;
        font-weight: 400;
    }

    /* Table styling */
    [data-testid="stChatMessage"] div[class^="stMarkdown"] table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
        box-shadow: var(--shadow-md);
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid var(--gray-200);
    }

    [data-testid="stChatMessage"] div[class^="stMarkdown"] th,
    [data-testid="stChatMessage"] div[class^="stMarkdown"] td {
        padding: 14px 18px;
        text-align: left;
        border-bottom: 1px solid var(--gray-200);
        font-size: 14px;
    }

    [data-testid="stChatMessage"] div[class^="stMarkdown"] th {
        background-color: var(--gray-100);
        font-weight: 600;
        color: var(--gray-800);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    [data-testid="stChatMessage"] div[class^="stMarkdown"] tr:last-child td {
        border-bottom: none;
    }

    [data-testid="stChatMessage"] div[class^="stMarkdown"] tr:nth-child(even) {
        background-color: var(--gray-50);
    }

    [data-testid="stChatMessage"] div[class^="stMarkdown"] tr:hover {
        background-color: var(--primary-50);
    }

    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def get_smart_suggestions(domain):
    """Tạo gợi ý thông minh dựa trên domain hiện tại."""
    suggestions = {
        "CS50": {
            "Cơ bản": [
                "Giải thích về pointers trong C",
                "Làm thế nào để debug code?",
                "Sự khác biệt giữa array và linked list",
                "Thuật toán sorting nào hiệu quả nhất?",
                "Cách tối ưu hóa memory usage"
            ],
            "Nâng cao": [
                "Recursion hoạt động như thế nào?",
                "Hash tables và time complexity",
                "Binary search trees",
                "Dynamic programming là gì?",
                "Graph algorithms cơ bản"
            ],
            "Thực hành": [
                "Làm bài tập Problem Set 1",
                "Viết code tính fibonacci",
                "Implement bubble sort",
                "Tạo linked list đơn giản",
                "Debug một chương trình C"
            ]
        },
        "Lịch sử": {
            "🏛️ Thời kỳ cổ đại": [
                "🥁 Văn minh Đông Sơn và nghệ thuật trống đồng",
                "👑 Thời kỳ Hùng Vương - 18 đời Hùng Vương",
                "🏰 Văn Lang - Âu Lạc và An Dương Vương",
                "⚔️ Cuộc khởi nghĩa Hai Bà Trưng năm 40",
                "🏮 1000 năm Bắc thuộc và ảnh hưởng Trung Hoa"
            ],
            "👑 Thời kỳ phong kiến": [
                "🛡️ Đinh Bộ Lĩnh - Hoàng đế đầu tiên của Đại Cồ Việt",
                "🏯 Nhà Lý và kinh đô Thăng Long - thời kỳ hưng thịnh",
                "🐉 Nhà Trần và 3 lần đại thắng quân Nguyên Mông",
                "🗡️ Lê Lợi và cuộc khởi nghĩa Lam Sơn vĩ đại",
                "⚡ Quang Trung Nguyễn Huệ đại phá 29 vạn quân Thanh"
            ],
            "🔥 Thời kỳ cận hiện đại": [
                "🚩 Cuộc kháng chiến chống thực dân Pháp 1946-1954",
                "🏔️ Chiến thắng Điện Biên Phủ - lừng lẫy 5 châu",
                "🌟 Cuộc kháng chiến chống đế quốc Mỹ 1955-1975",
                "✍️ Hiệp định Paris 1973 và thắng lợi ngoại giao",
                "🎆 Giải phóng hoàn toàn miền Nam 30/4/1975"
            ]
        }
    }
    # Trả về gợi ý cho domain cụ thể, hoặc một dict rỗng nếu không có
    return suggestions.get(domain, {})


def display_welcome_message(domain):
    """Hiển thị tin nhắn chào mừng cho người dùng mới với animation."""
    messages = {
        "CS50": {
            "icon": "🎓",
            "title": "Chào mừng đến với CS50!",
            "subtitle": "Khám phá thế giới lập trình với Harvard CS50. Từ C đến Python, từ thuật toán cơ bản đến AI. Hãy bắt đầu với những câu hỏi đơn giản!",
            "theme": "cs50-theme"
        },
        "Lịch sử": {
            "icon": "🏛️",
            "title": "Chào mừng đến với lịch sử Việt Nam!",
            "subtitle": "Hành trình 4000 năm dựng nước và giữ nước. Từ văn minh Đông Sơn, các triều đại phong kiến đến những cuộc kháng chiến anh hùng. Khám phá di sản văn hóa và tinh thần bất khuất của dân tộc!",
            "theme": "history-theme"
        }
    }

    # Lấy thông tin cho domain, hoặc dùng giá trị mặc định
    welcome_data = messages.get(domain, {
        "icon": "📚",
        "title": f"Chào mừng đến với {domain}!",
        "subtitle": "Đây là một bộ kiến thức mới. Hãy bắt đầu đặt câu hỏi để khám phá nội dung.",
        "theme": "default-theme"
    })

    return f"""
    <div class="welcome-card {welcome_data['theme']}">
        <div class="welcome-icon">{welcome_data['icon']}</div>
        <h2 class="welcome-title">{welcome_data['title']}</h2>
        <p class="welcome-subtitle">{welcome_data['subtitle']}</p>
        <div class="welcome-pulse"></div>
    </div>
    <style>
    .welcome-card {{ 
        position: relative; padding: 32px; border-radius: 20px; margin: 24px 0; text-align: center;
        backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.2); overflow: hidden;
        animation: welcomeSlideIn 0.8s cubic-bezier(0.4, 0, 0.2, 1); color: white;
    }}
    .cs50-theme {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); box-shadow: 0 20px 40px rgba(102,126,234,0.3); }}
    .history-theme {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); box-shadow: 0 20px 40px rgba(240,147,251,0.3); }}
    .default-theme {{ background: linear-gradient(135deg, #38b2ac 0%, #319795 100%); box-shadow: 0 20px 40px rgba(56,178,172,0.3); }}
    .welcome-icon {{ font-size: 48px; margin-bottom: 16px; animation: iconFloat 3s ease-in-out infinite; }}
    .welcome-title {{ margin: 0 0 12px 0; font-size: 26px; font-weight: 700; letter-spacing: -0.025em; }}
    .welcome-subtitle {{ margin: 0; opacity: 0.95; line-height: 1.6; font-size: 15px; font-weight: 400; }}
    .welcome-pulse {{ position: absolute; top: 50%; left: 50%; width: 100px; height: 100px; background: rgba(255,255,255,0.1); border-radius: 50%; transform: translate(-50%, -50%); animation: pulse 4s ease-in-out infinite; pointer-events: none; }}
    @keyframes welcomeSlideIn {{ 0% {{ opacity: 0; transform: translateY(30px) scale(0.95); }} 100% {{ opacity: 1; transform: translateY(0) scale(1); }} }}
    @keyframes iconFloat {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-10px); }} }}
    @keyframes pulse {{ 0%, 100% {{ transform: translate(-50%, -50%) scale(0); opacity: 0; }} 50% {{ transform: translate(-50%, -50%) scale(2); opacity: 0.1; }} }}
    </style>
    """


def display_chatbot_interface(vector_stores, prompt, supabase_client, user_id, user_name):
    """Hiển thị toàn bộ giao diện chatbot sau khi đăng nhập."""

    # Initialize session state variables with better memory management
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        # Load messages only when needed
        if st.session_state.get("load_history", True):
            try:
                st.session_state.chat_history = load_messages_from_db(supabase_client, user_id)
                st.session_state.load_history = False
            except Exception as e:
                st.error(f"Lỗi tải lịch sử: {str(e)}")
    
    if "theme" not in st.session_state:
        st.session_state.theme = "light"
    if "user_avatar" not in st.session_state:
        st.session_state.user_avatar = ""
    if "ai_avatar" not in st.session_state:
        st.session_state.ai_avatar = ""

    # Giới hạn số lượng tin nhắn trong memory để tránh lag
    if len(st.session_state.chat_history) > 50:
        st.session_state.chat_history = st.session_state.chat_history[-50:]

    _inject_global_css()

    # # Nút chuyển đổi theme động - TẠM THỜI COMMENT
    # col1, col2, col3 = st.columns([1, 1, 1])
    # with col2:
    #     if st.session_state.theme == 'dark':
    #         if st.button("☀️ Chế độ sáng", key="theme_toggle_light", help="Chuyển sang giao diện sáng"):
    #             st.session_state.theme = 'light'
    #             st.rerun()
    #     else:
    #         if st.button("🌙 Chế độ tối", key="theme_toggle_dark", help="Chuyển sang giao diện tối"):
    #             st.session_state.theme = 'dark'
    #             st.rerun()

    with st.sidebar:
        # Lấy tên người dùng từ session_state
        st.write(f'Chào mừng *{user_name}*')
        
        # Avatar selector
        st.subheader("👤 Chọn avatar")
        user_avatars = ['🧑‍💻', '👨‍🎓', '👩‍💼', '👨‍🏫', '👩‍🔬', '👨‍💻', '👩‍🎨', '👨‍🚀']
        ai_avatars = ['🤖', '🧠', '💡', '🎯', '🚀', '⭐', '🌟', '💎']
        
        st.write("**Avatar của bạn:**")
        cols = st.columns(4)
        for i, avatar in enumerate(user_avatars):
            with cols[i % 4]:
                if st.button(avatar, key=f"user_avatar_{i}"):
                    st.session_state.user_avatar = avatar
                    st.rerun()
        
        st.write("**Avatar của AI:**")
        cols = st.columns(4)
        for i, avatar in enumerate(ai_avatars):
            with cols[i % 4]:
                if st.button(avatar, key=f"ai_avatar_{i}"):
                    st.session_state.ai_avatar = avatar
                    st.rerun()
        
        if st.button("Đăng xuất"):
            supabase_client.auth.sign_out()
            del st.session_state['user_session']
            st.rerun()

        st.divider()
        st.title("⚙️ Tùy chọn")
        
        # Tùy chọn bộ kiến thức động
        if not vector_stores:
            st.error("Không có bộ kiến thức nào được tải. Vui lòng thêm một bộ kiến thức qua trang Admin.")
            st.stop()
            
        domain_list = list(vector_stores.keys())
        domain = st.radio("Chọn bộ kiến thức", domain_list, horizontal=True)
        
        temperature = st.slider("🌡️ Độ sáng tạo", 0.0, 1.0, 0.1, 0.05)
        k_documents = st.slider("📚 Số nguồn tham khảo", 5, 20, 15, 1)

        st.caption("\n")
        # --- Chat History Controls ---
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🧹 Xóa hiện tại"):
                st.session_state.chat_history = []
                st.rerun()
        
        # with col_b:
        #     # Disable pin button if history is empty - TẠM THỜI COMMENT
        #     pin_disabled = not st.session_state.get("chat_history")
        #     if st.button("📌 Ghim hội thoại", disabled=pin_disabled):
        #         # Use a session state flag to show the text input
        #         st.session_state.show_pin_input = True

        # # Show text input for pin title if flag is true - TẠM THỜI COMMENT
        # if st.session_state.get("show_pin_input"):
        #     with st.form("pin_form"):
        #         pin_title = st.text_input("Nhập tiêu đề cho hội thoại:", placeholder="Ví dụ: Giải thích về Pointers trong C")
        #         submitted = st.form_submit_button("Lưu")
        #         if submitted:
        #             if pin_title:
        #                 if pin_conversation_to_db(supabase_client, user_id, pin_title, st.session_state.chat_history):
        #                     st.success(f'Đã ghim hội thoại "{pin_title}"!')
        #                 else:
        #                     st.error("Có lỗi xảy ra khi ghim hội thoại.")
        #                 st.session_state.show_pin_input = False
        #                 st.rerun()
        #             else:
        #                 st.warning("Tiêu đề không được để trống.")

        # Tải xuống lịch sử hội thoại
        if st.session_state.get("chat_history"):
            export_text = "\n".join([
                ("Người hỏi: " + m.content) if isinstance(m, HumanMessage) else ("Trợ giảng: " + m.content)
                for m in st.session_state.chat_history
            ])
            st.download_button("💾 Tải lịch sử", data=export_text, file_name="chat_history.txt")

        # st.divider()
        # # --- Pinned Conversations List --- TẠM THỜI COMMENT
        # st.subheader("📌 Hội thoại đã ghim")
        # pinned_conversations = load_pinned_conversations_from_db(supabase_client, user_id)
        # if not pinned_conversations:
        #     st.info("Bạn chưa ghim hội thoại nào.")
        # else:
        #     for convo in pinned_conversations:
        #         with st.container():
        #             col1, col2, col3 = st.columns([3, 1, 1])
        #             with col1:
        #                 st.markdown(f"**{convo['title']}**")
        #                 st.caption(f"Ghim lúc: {convo['created_at'][:16]}")
        #             with col2:
        #                 if st.button("Tải", key=f"load_{convo['id']}", help="Tải lại hội thoại này"):
        #                     loaded_history = load_specific_pinned_conversation(supabase_client, convo['id'])
        #                     if loaded_history:
        #                         st.session_state.chat_history = loaded_history
        #                         st.rerun()
        #                     else:
        #                         st.error("Không thể tải hội thoại.")
        #             with col3:
        #                 if st.button("Xóa", key=f"delete_{convo['id']}", help="Xóa hội thoại đã ghim"):
        #                     if delete_pinned_conversation_from_db(supabase_client, convo['id']):
        #                         st.rerun()
        #                     else:
        #                         st.error("Không thể xóa hội thoại.")

        # st.divider()

        # # --- Export Chat --- TẠM THỜI COMMENT
        # if st.session_state.get("chat_history") and len(st.session_state.chat_history) > 0: 
        #     if st.button("📥 Tạo PDF", help="Tạo file PDF từ lịch sử chat"):
        #         try:
        #             with st.spinner("Đang tạo PDF..."):
        #                 pdf_bytes = export_chat_to_pdf(st.session_state.chat_history, user_name)
        #             st.download_button(
        #                 label="📥 Tải xuống PDF",
        #                 data=pdf_bytes,
        #                 file_name=f"lich_su_chat_{user_name}.pdf",
        #                 mime="application/pdf",
        #                 help="Tải xuống file PDF đã tạo."
        #             )
        #         except Exception as e:
        #             st.error(f"Lỗi tạo PDF: {str(e)}")

        # st.divider()
        # # --- Chat History Search --- TẠM THỜI COMMENT
        # st.subheader("🔍 Tìm kiếm Lịch sử")
        # search_query = st.text_input(
        #     "Nhập từ khóa để tìm kiếm...", 
        #     key="history_search",
        #     help="Tìm kiếm trong toàn bộ lịch sử chat của bạn."
        # )

        # if search_query and len(search_query) >= 3:  # Chỉ tìm kiếm khi có ít nhất 3 ký tự
        #     with st.spinner("Đang tìm kiếm..."):
        #         try:
        #             search_results = search_messages_in_db(supabase_client, user_id, search_query)
        #         except Exception as e:
        #             st.error(f"Lỗi tìm kiếm: {str(e)}")
        #             search_results = []
            
        #     if not search_results:
        #         st.info("Không tìm thấy kết quả nào.")
        #     else:
        #         st.success(f"Tìm thấy {len(search_results[:10])} tin nhắn:")  # Giới hạn hiển thị 10 kết quả
        #         # Use a scrollable container for results
        #         with st.container(height=300):
        #             for i, msg in enumerate(search_results[:10]):  # Chỉ hiển thị 10 kết quả đầu
        #                 role_icon = (st.session_state.get('user_avatar') or '🧑‍💻') if msg['role'] == 'user' else (st.session_state.get('ai_avatar') or '🤖')
        #                 date_str = msg['created_at'][:16].replace("T", " ")
                        
        #                 # Create a button for each search result
        #                 if st.button(f"{role_icon} {date_str}: {msg['content'][:50]}...", key=f"jump_{i}", help="Nhảy đến tin nhắn này"):
        #                     try:
        #                         # Load history up to the selected message's timestamp
        #                         st.session_state.chat_history = load_messages_up_to_db(supabase_client, user_id, msg['created_at'])
        #                         # Clear the search query to hide results after jumping
        #                         st.session_state.history_search = ""
        #                         st.rerun()
        #                     except Exception as e:
        #                         st.error(f"Lỗi tải tin nhắn: {str(e)}")
        # elif search_query and len(search_query) < 3:
        #     st.info("Nhập ít nhất 3 ký tự để tìm kiếm.")

    with st.container():
        st.markdown(
            f"""
            <div class="hero-card">
              <div style="display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;">
                <div>
                  <h1 class="hero-title">🤖 Trợ lý học tập</h1>
                  <p class="hero-subtitle">Hỏi đáp thông minh về CS50 và Lịch sử Việt Nam. Tối ưu cho độ chính xác và nguồn tham khảo.</p>
                </div>
                <div><span class="badge">Miền hiện tại: {domain}</span></div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Tải lịch sử chat của người dùng này
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = load_messages_from_db(supabase_client, user_id)

    # Hiển thị các tin nhắn đã có
    for message in st.session_state.chat_history:
        role = "user" if isinstance(message, HumanMessage) else "assistant"
        avatar = (st.session_state.get('user_avatar') or '🧑‍💻') if role == "user" else (st.session_state.get('ai_avatar') or '🤖')
        with st.chat_message(role, avatar=avatar):
            st.markdown(message.content)

    # Smart suggestions
    if not st.session_state.chat_history or len(st.session_state.chat_history) < 2:
        # Hiển thị tin nhắn chào mừng
        st.markdown(display_welcome_message(domain), unsafe_allow_html=True)
        
        # Hiển thị gợi ý câu hỏi
        suggestions = get_smart_suggestions(domain)
        st.markdown(
            """
            <div class="suggestions-container">
                <h4 style="margin-bottom: 16px;">💡 Gợi ý câu hỏi:</h4>
            """,
            unsafe_allow_html=True
        )
        
        for category, category_suggestions in suggestions.items():
            st.markdown(
                f'<h5 style="margin: 16px 0 8px 0; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px;">{category}</h5>',
                unsafe_allow_html=True
            )
            
            cols = st.columns(2)
            for i, suggestion in enumerate(category_suggestions):
                with cols[i % 2]:
                    if st.button(
                        suggestion, 
                        key=f"suggestion_{category}_{i}",
                        help=f"Click để hỏi: {suggestion}"
                    ):
                        st.session_state.suggested_question = suggestion
                        st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

    # Xử lý input mới
    placeholder_text = "Hỏi tôi về CS50 hoặc Lịch sử Việt Nam..."
    user_question = st.chat_input(placeholder_text)
    
    # Xử lý câu hỏi được gợi ý
    if hasattr(st.session_state, 'suggested_question'):
        user_question = st.session_state.suggested_question
        del st.session_state.suggested_question
    
    if user_question:
        st.session_state.chat_history.append(HumanMessage(content=user_question))
        save_message_to_db(supabase_client, user_id, "user", user_question)

        user_avatar = st.session_state.get('user_avatar') or '🧑‍💻'
        ai_avatar = st.session_state.get('ai_avatar') or '🤖'
        
        with st.chat_message("user", avatar=user_avatar):
            st.markdown(user_question)

        with st.chat_message("assistant", avatar=ai_avatar):
            response_placeholder = st.empty()
            
            # Enhanced typing indicator with animation
            typing_placeholder = st.empty()
            typing_placeholder.markdown(
                """
                <div class="typing-indicator">
                    <div class="typing-dots">
                        <span></span><span></span><span></span>
                    </div>
                    <span class="typing-text">Trợ giảng đang suy nghĩ...</span>
                </div>
                <style>
                .typing-indicator {
                    display: flex;
                    align-items: center;
                    gap: 12px;
                    padding: 12px 16px;
                    background: linear-gradient(135deg, var(--gray-50) 0%, rgba(59,130,246,0.05) 100%);
                    border-radius: 12px;
                    border: 1px solid var(--gray-200);
                    animation: typingPulse 2s ease-in-out infinite;
                }
                .typing-dots {
                    display: flex;
                    gap: 4px;
                }
                .typing-dots span {
                    width: 8px;
                    height: 8px;
                    background: var(--primary-500);
                    border-radius: 50%;
                    animation: typingBounce 1.4s ease-in-out infinite both;
                }
                .typing-dots span:nth-child(1) { animation-delay: -0.32s; }
                .typing-dots span:nth-child(2) { animation-delay: -0.16s; }
                .typing-text {
                    color: var(--gray-600);
                    font-size: 14px;
                    font-weight: 500;
                }
                @keyframes typingBounce {
                    0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
                    40% { transform: scale(1.2); opacity: 1; }
                }
                @keyframes typingPulse {
                    0%, 100% { box-shadow: 0 2px 8px rgba(59,130,246,0.1); }
                    50% { box-shadow: 0 4px 16px rgba(59,130,246,0.2); }
                }
                </style>
                """,
                unsafe_allow_html=True
            )

            with st.spinner("🤖 Đang phân tích và tìm kiếm thông tin..."):
                try:
                    llm = ChatGoogleGenerativeAI(
                        model="gemini-2.5-flash",
                        temperature=temperature,
                    )
                    
                    # Kiểm tra vector store tồn tại
                    if domain not in vector_stores or vector_stores[domain] is None:
                        st.error(f"Vector store cho {domain} chưa được tạo. Vui lòng chạy build_db_google.py")
                        return
                    
                    vector_store = vector_stores[domain]
                    retriever = vector_store.as_retriever(search_type="mmr", search_kwargs={'k': k_documents, 'fetch_k': 20})
                    
                    formatted_chat_history = format_chat_history(st.session_state.chat_history)
                    retrieved_docs = retriever.invoke(user_question)
                    
                    context = "\n\n---\n\n".join([doc.page_content for doc in retrieved_docs])

                    rag_chain = prompt | llm | StrOutputParser()
                    response_stream = rag_chain.stream({
                        "domain": domain,
                        "question": user_question,
                        "context": context,
                        "chat_history": formatted_chat_history
                    })

                    # Xóa typing indicator
                    typing_placeholder.empty()
                    
                    # Stream response with enhanced formatting
                    accumulated_parts = []
                    for chunk in response_stream:
                        accumulated_parts.append(chunk)
                        current_text = "".join(accumulated_parts)
                        
                        # Add streaming cursor effect
                        response_placeholder.markdown(
                            f"""
                            <div class="streaming-response">
                                {current_text}<span class="cursor">|</span>
                            </div>
                            <style>
                            .streaming-response {{
                                line-height: 1.6;
                                font-size: 15px;
                            }}
                            .cursor {{
                                animation: blink 1s infinite;
                                color: var(--primary-500);
                                font-weight: bold;
                            }}
                            @keyframes blink {{
                                0%, 50% {{ opacity: 1; }}
                                51%, 100% {{ opacity: 0; }}
                            }}
                            </style>
                            """,
                            unsafe_allow_html=True
                        )
                    
                    full_response = "".join(accumulated_parts)
                    
                    # Final response without cursor
                    response_placeholder.markdown(full_response)
                    
                    # Format response với bullet points
                    if "*" in full_response:
                        # Tách các ý chính và format lại
                        lines = full_response.split('\n')
                        formatted_lines = []
                        for line in lines:
                            if line.strip().startswith('*'):
                                # Giữ nguyên bullet points
                                formatted_lines.append(line)
                            elif line.strip() and not line.strip().startswith('•'):
                                # Thêm bullet point cho các ý chính
                                formatted_lines.append(f"• {line.strip()}")
                            else:
                                formatted_lines.append(line)
                        full_response = '\n'.join(formatted_lines)
                    
                except Exception as e:
                    typing_placeholder.empty()
                    error_message = f"Xin lỗi, đã có lỗi xảy ra: {str(e)}"
                    
                    # Enhanced error display
                    response_placeholder.markdown(
                        f"""
                        <div class="error-container">
                            <div class="error-icon">⚠️</div>
                            <div class="error-content">
                                <h4 class="error-title">Đã xảy ra lỗi</h4>
                                <p class="error-message">{str(e)}</p>
                                <p class="error-suggestion">Vui lòng thử lại hoặc liên hệ hỗ trợ nếu lỗi tiếp tục xảy ra.</p>
                            </div>
                        </div>
                        <style>
                        .error-container {
                            display: flex;
                            align-items: flex-start;
                            gap: 16px;
                            padding: 20px;
                            background: linear-gradient(135deg, #fef2f2 0%, #fecaca 100%);
                            border: 1px solid #fca5a5;
                            border-radius: 12px;
                            margin: 12px 0;
                        }
                        .error-icon {
                            font-size: 24px;
                            flex-shrink: 0;
                        }
                        .error-title {
                            margin: 0 0 8px 0;
                            color: #dc2626;
                            font-size: 16px;
                            font-weight: 600;
                        }
                        .error-message {
                            margin: 0 0 8px 0;
                            color: #991b1b;
                            font-size: 14px;
                            font-family: 'Monaco', 'Menlo', monospace;
                            background: rgba(255,255,255,0.5);
                            padding: 8px;
                            border-radius: 6px;
                        }
                        .error-suggestion {
                            margin: 0;
                            color: #7f1d1d;
                            font-size: 13px;
                        }
                        </style>
                        """,
                        unsafe_allow_html=True
                    )
                    full_response = error_message

        st.session_state.chat_history.append(AIMessage(content=full_response))
        save_message_to_db(supabase_client, user_id, "assistant", full_response)