# src/dashboard_ui.py
import streamlit as st
import pandas as pd
from src.database import (
    get_total_users,
    get_total_messages,
    get_messages_per_domain
)

def display_dashboard(supabase_client):
    """Hiển thị trang tổng quan quản trị."""
    st.header("📊 Tổng quan hệ thống")
    st.markdown("Thống kê nhanh về hoạt động của chatbot.")

    # Fetch data
    with st.spinner("Đang tải dữ liệu..."):
        total_users = get_total_users(supabase_client)
        total_messages = get_total_messages(supabase_client)
        messages_per_domain = get_messages_per_domain(supabase_client)

    # Display key metrics in columns
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="👥 Tổng số người dùng", value=total_users)
    with col2:
        st.metric(label="💬 Tổng số tin nhắn", value=total_messages)

    st.divider()

    # Display messages per domain chart
    st.subheader("Tin nhắn theo từng lĩnh vực")
    if messages_per_domain:
        # Convert to DataFrame for charting
        df_domain = pd.DataFrame(list(messages_per_domain.items()), columns=['Lĩnh vực', 'Số tin nhắn'])
        df_domain = df_domain.sort_values('Số tin nhắn', ascending=False)
        
        st.bar_chart(df_domain.set_index('Lĩnh vực'))
        
        st.dataframe(df_domain, use_container_width=True)
    else:
        st.info("Chưa có dữ liệu về tin nhắn theo lĩnh vực.")
