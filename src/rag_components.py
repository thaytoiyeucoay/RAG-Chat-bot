# src/rag_components.py
import streamlit as st
import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import SupabaseVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from supabase.client import Client, create_client
from langchain_core.messages import HumanMessage, AIMessage

@st.cache_resource
def load_base_components():
    """Tải các thành phần cơ bản, nặng và ít thay đổi."""
    load_dotenv()
    if "SUPABASE_URL" not in os.environ or "SUPABASE_KEY" not in os.environ:
        st.error("Lỗi: Vui lòng kiểm tra SUPABASE_URL và SUPABASE_KEY trong file .env")
        st.stop()
    
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    supabase_client = create_client(supabase_url, supabase_key)
    
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    vector_store = SupabaseVectorStore(
        client=supabase_client,
        embedding=embeddings,
        table_name="documents",
        query_name="match_documents"
    )
    
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "BẠN LÀ MỘT TRỢ GIẢNG CS50. Hãy trả lời câu hỏi của sinh viên dựa trên NGỮ CẢNH và LỊCH SỬ TRÒ CHUYỆN."),
        ("human", "LỊCH SỬ TRÒ CHUYỆN:\n{chat_history}"),
        ("human", "NGỮ CẢNH:\n{context}\n\nCÂU HỎI: {question}")
    ])
    
    return vector_store, prompt_template, supabase_client

def format_chat_history(chat_history):
    return "\n".join(f"{'Người hỏi' if isinstance(msg, HumanMessage) else 'Trợ giảng'}: {msg.content}" for msg in chat_history)