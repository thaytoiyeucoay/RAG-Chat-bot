# src/rag_components.py
import streamlit as st
import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from supabase.client import Client, create_client
from langchain_core.messages import HumanMessage, AIMessage

@st.cache_resource(ttl=3600)
def load_base_components():
    """Tải các thành phần cơ bản với tối ưu hiệu suất."""
    load_dotenv()

    # 1. Tải Supabase client
    try:
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_KEY")
        if not supabase_url or not supabase_key:
            st.error("Thiếu cấu hình Supabase trong file .env")
            st.stop()
        supabase_client = create_client(supabase_url, supabase_key)
    except Exception as e:
        st.error(f"Lỗi kết nối Supabase: {str(e)}")
        st.stop()

    # 2. Tải Google Embeddings với retry
    try:
        embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    except Exception as e:
        st.error(f"Lỗi tải embeddings: {str(e)}")
        st.stop()

    # 3. Tải vector stores
    vector_stores = {}
    
    # Tải CS50 vector store (từ vectorstore_google)
    try:
        if os.path.exists("vectorstore_google"):
            cs50_store = Chroma(
                persist_directory="vectorstore_google", 
                embedding_function=embeddings
            )
            vector_stores["CS50"] = cs50_store
            print("✅ Đã tải CS50 vector store")
    except Exception as e:
        print(f"❌ Không thể tải CS50 vector store: {e}")
    
    # Tạo History vector store từ db_history nếu chưa có
    try:
        if os.path.exists("db_history") and os.listdir("db_history"):
            from langchain_community.document_loaders import TextLoader
            from langchain.text_splitter import RecursiveCharacterTextSplitter
            
            # Tải documents từ db_history
            history_docs = []
            for filename in os.listdir("db_history"):
                if filename.endswith(".txt"):
                    filepath = os.path.join("db_history", filename)
                    try:
                        loader = TextLoader(filepath, encoding='utf-8')
                        history_docs.extend(loader.load())
                    except Exception as e:
                        print(f"Lỗi tải file {filename}: {e}")
            
            if history_docs:
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=150)
                history_chunks = text_splitter.split_documents(history_docs)
                
                # Tạo vector store cho lịch sử
                history_store = Chroma.from_documents(
                    history_chunks, 
                    embeddings,
                    persist_directory="vectorstore_history"
                )
                vector_stores["Lịch sử"] = history_store
                print("✅ Đã tạo History vector store")
    except Exception as e:
        print(f"❌ Không thể tạo History vector store: {e}")
    
    # Fallback nếu không có vector stores
    if not vector_stores:
        st.warning("Không có bộ kiến thức. Vui lòng chạy build_db_google.py để tạo CS50 vector store.")
        vector_stores = {"CS50": None, "Lịch sử": None}

    # Prompt động theo miền kiến thức
    prompt_template = ChatPromptTemplate.from_messages([
        (
            "system",
            "Bạn là trợ lý học tập thông minh. Miền kiến thức: {domain}. "
            "Trả lời dựa trên NGỮ CẢNH được cung cấp và LỊCH SỬ TRÒ CHUYỆN. "
            "Nếu câu hỏi vượt ngoài miền, hãy nói rõ và đề xuất câu hỏi phù hợp."
        ),
        ("human", "LỊCH SỬ TRÒ CHUYỆN:\n{chat_history}\n\nNGỮ CẢNH:\n{context}\n\nCÂU HỎI: {question}")
    ])

    return vector_stores, prompt_template, supabase_client

def format_chat_history(chat_history):
    return "\n".join(f"{'Người hỏi' if isinstance(msg, HumanMessage) else 'Trợ giảng'}: {msg.content}" for msg in chat_history)