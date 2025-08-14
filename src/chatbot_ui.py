# src/chatbot_ui.py (Phiên bản cuối cùng)
import streamlit as st
import os
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI, HarmBlockThreshold, HarmCategory
from src.database import save_message_to_db, load_messages_from_db
from src.rag_components import format_chat_history


def _inject_global_css():
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] * {
        font-family: 'Inter', system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, 'Helvetica Neue', Helvetica, Arial, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol' !important;
    }
    /* App background */
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(1200px 600px at 0% 0%, #f0f7ff 0%, #ffffff 50%) no-repeat;
    }
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
        color: #e5e7eb;
    }
    [data-testid="stSidebar"] .stButton>button, [data-testid="stSidebar"] .stDownloadButton button {
        width: 100%;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.15);
        background: linear-gradient(180deg, #1f2937 0%, #111827 100%);
        color: #e5e7eb;
    }
    [data-testid="stSidebar"] .stRadio>div>label {
        padding: 6px 10px;
        border-radius: 8px;
    }
    /* Header card */
    .hero-card {
        border-radius: 16px;
        padding: 20px 22px;
        background: linear-gradient(135deg, rgba(59,130,246,0.12) 0%, rgba(37,99,235,0.06) 100%);
        border: 1px solid rgba(59,130,246,0.25);
    }
    .hero-title { font-weight: 700; font-size: 28px; margin: 0 0 6px 0; color: #0f172a; }
    .hero-subtitle { color: #334155; margin: 0; }
    .badge {
        display: inline-block; padding: 4px 10px; border-radius: 999px; font-size: 12px; font-weight: 600;
        background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; margin-left: 8px;
    }
    /* Chat message bubbles */
    [data-testid="stChatMessage"] {
        border-radius: 16px !important;
        padding: 2px 2px !important;
        margin-bottom: 8px !important;
    }
    [data-testid="stChatMessage"] div[class^="stMarkdown"] p {
        margin-bottom: 0;
    }
    [data-testid="stChatMessage"]:has([data-baseweb="avatar"]) {
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.06);
    }
    /* Source chips */
    .chip { display:inline-block; padding:6px 10px; border-radius:999px; background:#f1f5f9; color:#0f172a; border:1px solid #e2e8f0; font-size:12px; margin:4px 6px 0 0; }
    .chip b { color:#1e293b; }
    .sources-card { border-radius: 14px; border:1px solid #e2e8f0; background:#ffffff; padding:10px 14px; }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def display_chatbot_interface(vector_stores, prompt, supabase_client, user_id, user_name):
    """Hiển thị toàn bộ giao diện chatbot sau khi đăng nhập."""

    _inject_global_css()

    with st.sidebar:
        # Lấy tên người dùng từ session_state
        st.write(f'Chào mừng *{user_name}*')
        if st.button("Đăng xuất"):
            supabase_client.auth.sign_out()
            del st.session_state['user_session']  # Xoá session người dùng
            st.rerun()  # Chạy lại script để hiển thị form đăng nhập
        # Lấy authenticator từ session_state để gọi hàm logout
        #st.session_state.authenticator.logout('Đăng xuất', 'main')

        st.divider()
        st.title("⚙️ Tùy chọn")
        domain = st.radio("Bộ kiến thức", ["CS50", "Lịch sử"], horizontal=True)
        temperature = st.slider("🌡️ Độ sáng tạo", 0.0, 1.0, 0.1, 0.05)
        k_documents = st.slider("📚 Số nguồn tham khảo", 3, 10, 5, 1)

        st.caption("\n")
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🧹 Xóa hội thoại"):
                st.session_state.chat_history = []
                st.rerun()
        with col_b:
            if st.button("🔄 Bắt đầu mới"):
                st.session_state.chat_history = []
                st.rerun()

        # Tải xuống lịch sử hội thoại (từ session)
        if "chat_history" in st.session_state and st.session_state.chat_history:
            export_text = "\n".join([
                ("Người hỏi: " + m.content) if isinstance(m, HumanMessage) else ("Trợ giảng: " + m.content)
                for m in st.session_state.chat_history
            ])
            st.download_button("💾 Tải lịch sử", data=export_text, file_name="chat_history.txt")

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
        with st.chat_message(role):
            st.markdown(message.content)

    # Xử lý input mới
    placeholder_text = "Hỏi tôi về CS50 hoặc Lịch sử Việt Nam..."
    if user_question := st.chat_input(placeholder_text):
        st.session_state.chat_history.append(HumanMessage(content=user_question))
        save_message_to_db(supabase_client, user_id, "user", user_question)

        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(user_question)

        with st.chat_message("assistant", avatar="🤖"):
            response_placeholder = st.empty()
            sources_placeholder = st.empty()

            with st.spinner("Trợ giảng đang suy nghĩ..."):
                llm = ChatGoogleGenerativeAI(
                    model="gemini-2.0-flash",
                    temperature=temperature,
                    # safety_settings={
                    #     HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                    #     HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                    #     HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                    #     HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                    # }
                )
                vector_store = vector_stores[domain]
                retriever = vector_store.as_retriever(search_type="mmr", search_kwargs={'k': 4, 'fetch_k': 20})
                
                formatted_chat_history = format_chat_history(st.session_state.chat_history)
                retrieved_docs = retriever.invoke(user_question)
                print("\n--- KẾT QUẢ TÌM KIẾM (RETRIEVED DOCS) ---")
                if not retrieved_docs:
                    print("!!! CẢNH BÁO: Retriever đã trả về một danh sách rỗng. Không tìm thấy tài liệu nào.")
                else:
                    print(f"Đã tìm thấy {len(retrieved_docs)} tài liệu liên quan.")
                    for i, doc in enumerate(retrieved_docs):
                        print(f"\n--- Tài liệu {i+1} ---")
                        # In một phần nội dung để xem trước
                        print(doc.page_content[:500] + "...") 
                        # In metadata để biết nó đến từ file nào
                        print(f"Metadata: {doc.metadata}") 
                print("=============================================\n")
                
                
                context = "\n\n---\n\n".join([doc.page_content for doc in retrieved_docs])

                rag_chain = prompt | llm | StrOutputParser()
                response_stream = rag_chain.stream({
                    "domain": domain,
                    "question": user_question,
                    "context": context,
                    "chat_history": formatted_chat_history
                })

                # Tránh phụ thuộc write_stream (có thể gây import pyarrow trên Windows)
                accumulated_parts = []
                for chunk in response_stream:
                    accumulated_parts.append(chunk)
                    response_placeholder.markdown("".join(accumulated_parts))
                full_response = "".join(accumulated_parts)

            # Hiển thị nguồn sau khi stream xong
            with sources_placeholder.container():
                with st.expander("📚 Xem nguồn tham khảo"):
                    if retrieved_docs:
                        st.markdown('<div class="sources-card">', unsafe_allow_html=True)
                        cols = st.columns(2)
                        for idx, doc in enumerate(retrieved_docs):
                            full_path = doc.metadata.get('source', 'Không rõ nguồn')
                            source_name = os.path.basename(full_path)
                            with cols[idx % 2]:
                                st.markdown(f"<span class=\"chip\"><b>#{idx+1}</b> {source_name}</span>", unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.write("Không tìm thấy tài liệu liên quan.")

        st.session_state.chat_history.append(AIMessage(content=full_response))
        save_message_to_db(supabase_client, user_id, "assistant", full_response)