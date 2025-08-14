# src/chatbot_ui.py (Phiên bản cuối cùng)
import streamlit as st
import os
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI, HarmBlockThreshold, HarmCategory
from src.database import save_message_to_db, load_messages_from_db
from src.rag_components import format_chat_history

def display_chatbot_interface(vector_stores, prompt, supabase_client, user_id, user_name):
    """Hiển thị toàn bộ giao diện chatbot sau khi đăng nhập."""

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

    st.title("🤖 Trợ lý học tập (CS50 & Lịch sử)")

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

        with st.chat_message("user"):
            st.markdown(user_question)

        with st.chat_message("assistant"):
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
                with st.expander("Xem các nguồn tham khảo"):
                    if retrieved_docs:
                        for doc in retrieved_docs:
                            full_path = doc.metadata.get('source', 'Không rõ nguồn')
                            source_name = os.path.basename(full_path)
                            st.markdown(f"**Nguồn:** `{source_name}`")
                    else:
                        st.write("Không tìm thấy tài liệu liên quan.")

        st.session_state.chat_history.append(AIMessage(content=full_response))
        save_message_to_db(supabase_client, user_id, "assistant", full_response)