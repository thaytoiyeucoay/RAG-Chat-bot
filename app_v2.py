# app_v2.py (Phiên bản Nâng cấp Toàn diện)

# --- PHẦN 1: IMPORT CÁC CÔNG CỤ CẦN THIẾT ---
import nest_asyncio
nest_asyncio.apply() # Sửa lỗi event loop cho Streamlit

import streamlit as st
import os
from dotenv import load_dotenv

# Các thành phần cốt lõi của LangChain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage

# Các thành phần chuyên dụng
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.retrievers.contextual_compression import ContextualCompressionRetriever
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain.retrievers.document_compressors import FlashrankRerank # Nâng cấp: Re-ranker

from langchain_community.vectorstores import SupabaseVectorStore
from supabase.client import Client, create_client

# --- PHẦN 2: HÀM TẢI "BỘ NÃO" CHATBOT ĐÃ NÂNG CẤP ---
# Sử dụng cache để không phải tải lại model mỗi lần tương tác
@st.cache_resource
def load_upgraded_rag_components():
    """
    Tải và khởi tạo tất cả các thành phần đã được nâng cấp.
    Chỉ chạy MỘT LẦN DUY NHẤT.
    """
    print("--- ĐANG KẾT NỐI TỚI SUPABASE VÀ TẢI CÁC THÀNH PHẦN ---")
    
    # Tải API Key và thông tin kết nối Supabase
    load_dotenv()
    if "GOOGLE_API_KEY" not in os.environ or "SUPABASE_URL" not in os.environ or "SUPABASE_KEY" not in os.environ:
        st.error("Lỗi: Vui lòng kiểm tra các biến môi trường trong file .env")
        st.stop()

    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    supabase_client: Client = create_client(supabase_url, supabase_key)

    # 1. Khởi tạo Embedding Model
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    
    # 2. >>> THAY ĐỔI QUAN TRỌNG: Kết nối tới Supabase Vector Store đã có
    vector_store = SupabaseVectorStore(
        client=supabase_client,
        embedding=embeddings,
        table_name="documents",
        query_name="match_documents"
    )

    # 3. Tạo retriever từ Supabase Vector Store
    # Chúng ta không cần Re-ranker ở đây vì Supabase đã có hàm tìm kiếm rất tốt
    retriever = vector_store.as_retriever(search_kwargs={'k': 5})
    print("--- Kết nối tới Supabase Vector Store thành công! ---")

    # 4. Khởi tạo LLM
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.1, streaming=True)
    
    # 5. NÂNG CẤP: Tạo Prompt mới hỗ trợ "Trí nhớ" và "Trích dẫn nguồn"
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", """BẠN LÀ MỘT TRỢ GIẢNG CS50 THÔNG MINH VÀ THÂN THIỆN.
        Nhiệm vụ của bạn là trả lời câu hỏi của sinh viên dựa trên NGỮ CẢNH là các bài giảng đã được cung cấp và LỊCH SỬ TRÒ CHUYỆN trước đó.
        
        QUY TẮC BẮT BUỘC:
        1. Luôn trả lời dựa trên NGỮ CẢNH.
        2. Sau khi trả lời xong, hãy liệt kê các nguồn đã sử dụng. Mỗi nguồn phải được định dạng là: `- [Tên file hoặc nguồn]: [Một đoạn trích ngắn gọn từ nguồn đó]`.
        3. Nếu NGỮ CẢNH không chứa thông tin, hãy trả lời một cách trung thực: "Rất tiếc, tôi không tìm thấy thông tin về vấn đề này trong tài liệu."
        
        NGỮ CẢNH:
        {context}"""),
        ("human", "LỊCH SỬ TRÒ CHUYỆN:\n{chat_history}"),
        ("human", "CÂU HỎI MỚI: {question}")
    ])
    
    print("--- Đã tải xong tất cả thành phần! ---")
    # Trả về các thành phần để sử dụng trong app
    return retriever, llm, prompt_template

def format_chat_history(chat_history):
    """Định dạng lịch sử chat thành một chuỗi văn bản duy nhất."""
    buffer = ""
    for message in chat_history:
        if isinstance(message, HumanMessage):
            buffer += f"Người hỏi: {message.content}\n"
        elif isinstance(message, AIMessage):
            buffer += f"Trợ giảng: {message.content}\n"
    return buffer

# --- PHẦN 3: XÂY DỰNG GIAO DIỆN STREAMLIT ---

# Thiết lập custom CSS
st.set_page_config(
    page_title="Trợ giảng CS50 Pro 🚀",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS để làm đẹp giao diện
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    .stTitle {
        font-size: 3rem !important;
        text-align: center;
        color: #0e1117;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    .stMarkdown {
        font-size: 1.1rem;
    }
    .stChatMessage {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .stButton button {
        width: 100%;
        border-radius: 20px;
        padding: 0.5rem 1rem;
    }
    .css-1v0mbdj.etr89bj1 {
        text-align: center;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar với thông tin và tùy chọn
with st.sidebar:
    st.image("https://cs50.harvard.edu/x/2024/favicon.ico", width=100)
    st.title("⚙️ Tùy chọn")
    
    # Tùy chọn nhiệt độ cho model
    temperature = st.slider("🌡️ Temperature", 0.0, 1.0, 0.1, 0.1,
                          help="Điều chỉnh độ sáng tạo trong câu trả lời (0: ổn định, 1: sáng tạo)")
    
    # Tùy chọn số lượng tài liệu tham khảo
    k_documents = st.slider("📚 Số tài liệu tham khảo", 3, 10, 5,7,
                          help="Số lượng tài liệu được sử dụng để trả lời")
    
    # Thêm một divider
    st.divider()
    
    # Thông tin về dự án
    st.markdown("""
    ### 📖 Về CS50 Chatbot
    
    Chatbot này được thiết kế để hỗ trợ sinh viên học CS50 
    với khả năng:
    - 🧠 Trí nhớ trong cuộc hội thoại
    - 📑 Trích dẫn nguồn tự động
    - 🔍 Tìm kiếm thông minh
    - ⚡ Phản hồi nhanh chóng
    """)

# Main content
st.title("🤖 Trợ giảng CS50 Pro 🚀")
st.markdown("""
<div style='text-align: center; padding: 1rem; background-color: #f8f9fa; border-radius: 10px; margin-bottom: 2rem;'>
    <h3>Chào mừng bạn đến với CS50 Assistant!</h3>
    <p>Version 2.0 - Nâng cấp với Trí nhớ, Trích dẫn nguồn, Re-ranking và Streaming!</p>
</div>
""", unsafe_allow_html=True)

# Tải các thành phần cốt lõi
try:
    retriever, llm, prompt = load_upgraded_rag_components()
except Exception as e:
    st.error(f"Đã xảy ra lỗi nghiêm trọng khi tải mô hình: {e}")
    st.stop()

# NÂNG CẤP: Quản lý "Trí nhớ" trong session_state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Hiển thị các tin nhắn đã có trong lịch sử
for message in st.session_state.chat_history:
    role = "user" if isinstance(message, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(message.content)

# Container cho chat history với custom style
chat_container = st.container()
with chat_container:
    # Thêm placeholder cho tin nhắn chào mừng nếu chưa có lịch sử chat
    if not st.session_state.chat_history:
        st.markdown("""
        <div style='text-align: center; padding: 2rem; color: #6c757d; background-color: #f8f9fa; border-radius: 10px; margin: 2rem 0;'>
            👋 Xin chào! Hãy đặt câu hỏi về CS50 để bắt đầu cuộc trò chuyện.
            <br><br>
            💡 Ví dụ:
            <br>• "Giải thích về Big O Notation"
            <br>• "Sự khác biệt giữa array và linked list?"
            <br>• "Làm thế nào để tối ưu code trong C?"
        </div>
        """, unsafe_allow_html=True)

# Ô nhập liệu cho người dùng với style mới
st.markdown("<br>", unsafe_allow_html=True)  # Thêm khoảng trống
user_question = st.chat_input("💭 Hỏi tôi về một khái niệm trong CS50...")

if user_question:
    # Hiển thị câu hỏi của người dùng ngay lập tức
    st.session_state.chat_history.append(HumanMessage(content=user_question))
    with st.chat_message("user", avatar="👤"):
        st.markdown(f"**Câu hỏi:** {user_question}")

    # NÂNG CẤP: Hiển thị trạng thái "Suy nghĩ" của chatbot
    with st.chat_message("assistant", avatar="🤖"):
        # Tạo container với style đẹp cho câu trả lời
        st.markdown("""
        <div style='background-color: #f8f9fa; border-left: 4px solid #0066cc; padding: 1rem; border-radius: 5px;'>
        """, unsafe_allow_html=True)
        
        # Tạo một placeholder trống để chứa câu trả lời sẽ được stream vào
        response_placeholder = st.empty()
        
        # Tạo một placeholder trống cho phần trích dẫn nguồn
        sources_placeholder = st.empty()
        
        st.markdown("</div>", unsafe_allow_html=True)

        # Khối 2: Thực hiện công việc hậu trường và cập nhật trạng thái
        with st.status("Trợ giảng đang suy nghĩ...", expanded=True) as status:
            
            # Bước 1: Định dạng lịch sử chat
            status.update(label="Phân tích lịch sử trò chuyện...")
            formatted_chat_history = format_chat_history(st.session_state.chat_history)
            
            # Bước 2: Truy xuất và tái xếp hạng tài liệu
            status.update(label="Tìm kiếm trong tài liệu...")
            retrieved_docs = retriever.invoke(user_question)
            context = "\n\n---\n\n".join([doc.page_content for doc in retrieved_docs])
            
            # Bước 3: Tạo chuỗi RAG
            rag_chain = (
                prompt
                | llm
                | StrOutputParser()
            )
            
            # Bước 4: Chuẩn bị stream câu trả lời
            status.update(label="Tổng hợp câu trả lời...")
            response_stream = rag_chain.stream({
                "question": user_question,
                "context": context,
                "chat_history": formatted_chat_history
            })
            
            # Bước 5: Đưa luồng phản hồi vào placeholder đã tạo ở trên
            # .write_stream sẽ tự động điền vào response_placeholder
            full_response = response_placeholder.write_stream(response_stream)
            
            # Bước 6: Hoàn thành
            status.update(label="Hoàn thành!", state="complete", expanded=False)

        # Sau khi stream xong, điền vào placeholder của trích dẫn nguồn
        with sources_placeholder.container():
            st.markdown("""
            <div style='margin-top: 1rem; padding: 1rem; background-color: #f0f2f6; border-radius: 5px;'>
                <h4 style='color: #0066cc; margin-bottom: 1rem;'>📚 Nguồn Tham Khảo</h4>
            """, unsafe_allow_html=True)
            
            if retrieved_docs:
                for i, doc in enumerate(retrieved_docs, 1):
                    full_path = doc.metadata.get('source', 'Không rõ nguồn')
                    source_name = os.path.basename(full_path)
                    st.markdown(f"""
                    <div style='margin-bottom: 1rem; padding: 0.5rem; background-color: white; border-radius: 5px;'>
                        <strong>📄 Nguồn {i}:</strong> <code>{source_name}</code>
                        <blockquote style='margin: 0.5rem 0; padding-left: 1rem; border-left: 3px solid #0066cc;'>
                            {doc.page_content[:200]}...
                        </blockquote>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style='text-align: center; color: #6c757d;'>
                    ℹ️ Không tìm thấy tài liệu liên quan.
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    # Thêm câu trả lời hoàn chỉnh vào lịch sử chat
    st.session_state.chat_history.append(AIMessage(content=full_response))