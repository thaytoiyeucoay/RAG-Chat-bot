# src/database.py
from supabase.client import Client
from langchain_core.messages import HumanMessage, AIMessage

def save_message_to_db(supabase_client: Client, user_id: str, role: str, content: str):
    """Lưu một tin nhắn vào bảng chat_history."""
    try:
        supabase_client.table("chat_history").insert({
            "user_id": user_id,
            "role": role,
            "content": content
        }).execute()
    except Exception as e:
        print(f"Lỗi khi lưu tin nhắn: {e}")

def load_messages_from_db(supabase_client: Client, user_id: str):
    """Tải lịch sử tin nhắn cho một user_id cụ thể."""
    try:
        response = supabase_client.table("chat_history").select("role, content").eq("user_id", user_id).order("created_at").execute()
        messages = []
        for item in response.data:
            if item['role'] == 'user':
                messages.append(HumanMessage(content=item['content']))
            elif item['role'] == 'assistant':
                messages.append(AIMessage(content=item['content']))
        return messages
    except Exception as e:
        print(f"Lỗi khi tải tin nhắn: {e}")
        return []