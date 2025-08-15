# src/database.py
from supabase import create_client, Client
from langchain_core.messages import HumanMessage, AIMessage
import json
import streamlit as st
from functools import lru_cache
from postgrest.exceptions import APIError
from src.error_handler import handle_errors, PerformanceMonitor

@handle_errors
@PerformanceMonitor.time_function
def save_message_to_db(supabase_client: Client, user_id: str, role: str, content: str):
    """Lưu một tin nhắn vào bảng chat_history."""
    supabase_client.table("chat_history").insert({
        "user_id": user_id,
        "role": role,
        "content": content[:2000]  # Giới hạn độ dài để tránh lỗi
    }).execute()

@st.cache_data(ttl=60)  # Cache trong 1 phút
@handle_errors
@PerformanceMonitor.time_function
def load_messages_from_db(_supabase_client: Client, user_id: str):
    """Tải lịch sử tin nhắn cho một user_id với caching."""
    response = _supabase_client.table("chat_history")\
        .select("role, content")\
        .eq("user_id", user_id)\
        .order("created_at")\
        .limit(50)\
        .execute()  # Giới hạn 50 tin nhắn để tăng tốc
    
    messages = []
    for item in response.data:
        if item['role'] == 'user':
            messages.append(HumanMessage(content=item['content']))
        elif item['role'] == 'assistant':
            messages.append(AIMessage(content=item['content']))
    return messages

# --- Pinned Conversations --- 

def pin_conversation_to_db(supabase_client: Client, user_id: str, title: str, history: list):
    """Lưu toàn bộ cuộc hội thoại vào bảng pinned_conversations."""
    try:
        # Chuyển đổi history object thành list of dicts để lưu dưới dạng JSON
        history_json = [{'role': 'user' if isinstance(m, HumanMessage) else 'assistant', 'content': m.content} for m in history]
        supabase_client.table("pinned_conversations").insert({
            "user_id": user_id,
            "title": title,
            "history": history_json
        }).execute()
        return True
    except Exception as e:
        print(f"Lỗi khi ghim hội thoại: {e}")
        return False

def load_pinned_conversations_from_db(supabase_client: Client, user_id: str):
    """Tải danh sách các cuộc hội thoại đã ghim."""
    try:
        response = supabase_client.table("pinned_conversations").select("id, title, created_at").eq("user_id", user_id).order("created_at", desc=True).execute()
        return response.data
    except APIError as e:
        if 'relation "public.pinned_conversations" does not exist' in e.message:
            # Bảng không tồn tại, tính năng này chưa được kích hoạt.
            # Trả về danh sách rỗng để không làm crash UI.
            pass
        else:
            print(f"Lỗi khi tải hội thoại đã ghim: {e}")
        return []
    except Exception as e:
        print(f"Lỗi không xác định khi tải hội thoại đã ghim: {e}")
        return []

def load_specific_pinned_conversation(supabase_client: Client, conversation_id: int):
    """Tải nội dung của một cuộc hội thoại đã ghim cụ thể."""
    try:
        response = supabase_client.table("pinned_conversations").select("history").eq("id", conversation_id).single().execute()
        history_json = response.data['history']
        messages = []
        for item in history_json:
            if item['role'] == 'user':
                messages.append(HumanMessage(content=item['content']))
            else:
                messages.append(AIMessage(content=item['content']))
        return messages
    except Exception as e:
        print(f"Lỗi khi tải nội dung hội thoại: {e}")
        return None

def delete_pinned_conversation_from_db(supabase_client: Client, conversation_id: int):
    """Xóa một cuộc hội thoại đã ghim."""
    try:
        supabase_client.table("pinned_conversations").delete().eq("id", conversation_id).execute()
        return True
    except Exception as e:
        print(f"Lỗi khi xóa hội thoại: {e}")
        return False

# --- Chat History Search ---

def search_messages_in_db(supabase_client: Client, user_id: str, query: str):
    """Tìm kiếm tin nhắn trong lịch sử chat của người dùng."""
    if not query:
        return []
    try:
        # Sử dụng ilike để tìm kiếm không phân biệt chữ hoa chữ thường
        response = supabase_client.table("chat_history")\
            .select("role, content, created_at")\
            .eq("user_id", user_id)\
            .ilike("content", f"%{query}%")\
            .order("created_at", desc=True)\
            .execute()
        return response.data
    except Exception as e:
        print(f"Lỗi khi tìm kiếm tin nhắn: {e}")
        return []

def load_messages_up_to_db(supabase_client: Client, user_id: str, timestamp: str):
    """Tải lịch sử tin nhắn cho một user_id cho đến một thời điểm nhất định."""
    try:
        response = supabase_client.table("chat_history")\
            .select("role, content")\
            .eq("user_id", user_id)\
            .lte("created_at", timestamp)\
            .order("created_at")\
            .execute()
        messages = []
        for item in response.data:
            if item['role'] == 'user':
                messages.append(HumanMessage(content=item['content']))
            elif item['role'] == 'assistant':
                messages.append(AIMessage(content=item['content']))
        return messages
    except Exception as e:
        print(f"Lỗi khi tải tin nhắn theo thời gian: {e}")
        return []

# --- Analytics Functions ---

def get_total_users(supabase_client: Client) -> int:
    """Lấy tổng số lượng người dùng đã đăng ký."""
    try:
        # Supabase auth users are in the auth.users table
        response = supabase_client.rpc('count_users', {}).execute()
        return response.data
    except Exception as e:
        print(f"Lỗi khi lấy tổng số người dùng: {e}")
        # Fallback for older Supabase projects without rpc
        try:
            response = supabase_client.table('_user').select('id', count='exact').execute()
            return response.count
        except Exception as e2:
            print(f"Lỗi fallback khi lấy tổng số người dùng: {e2}")
            return 0

def get_total_messages(supabase_client: Client) -> int:
    """Lấy tổng số tin nhắn trong hệ thống."""
    try:
        response = supabase_client.table("chat_history").select("id", count='exact').execute()
        return response.count
    except Exception as e:
        print(f"Lỗi khi lấy tổng số tin nhắn: {e}")
        return 0

def get_messages_per_domain(supabase_client: Client):
    """Thống kê số lượng tin nhắn cho mỗi miền kiến thức."""
    try:
        response = supabase_client.table("chat_history").select("metadata").execute()
        domain_counts = {}
        for item in response.data:
            if item.get('metadata') and 'domain' in item['metadata']:
                domain = item['metadata']['domain']
                domain_counts[domain] = domain_counts.get(domain, 0) + 1
        return domain_counts
    except Exception as e:
        print(f"Lỗi khi thống kê tin nhắn theo miền: {e}")
        return {}