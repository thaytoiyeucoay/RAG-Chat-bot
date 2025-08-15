# src/profile_ui.py
import streamlit as st

def display_profile_interface(supabase_client, user):
    """Hiển thị giao diện trang thông tin cá nhân."""

    st.markdown("### 👤 Thông tin cá nhân")

    full_name = user.user_metadata.get('full_name', '')
    email = user.email

    col1, col2 = st.columns([1, 2])
    with col1:
        st.info("**Email:**")
        st.write(email)
    with col2:
        st.info("**Họ và tên:**")
        st.write(full_name)

    st.divider()

    st.markdown("#### Cập nhật thông tin")
    with st.form("update_profile_form", clear_on_submit=True):
        new_full_name = st.text_input("Họ và tên mới", value=full_name)
        submitted = st.form_submit_button("Lưu thay đổi")

        if submitted:
            if new_full_name and new_full_name != full_name:
                try:
                    # Cập nhật metadata của người dùng trên Supabase
                    supabase_client.auth.update_user({
                        "data": {
                            'full_name': new_full_name
                        }
                    })
                    st.success("Cập nhật họ tên thành công!")
                    # Cập nhật session state để giao diện phản ánh ngay lập tức
                    st.session_state['user_session'].user.user_metadata['full_name'] = new_full_name
                    st.rerun()
                except Exception as e:
                    st.error(f"Lỗi khi cập nhật: {e}")
            elif not new_full_name:
                st.warning("Họ và tên không được để trống.")
            else:
                st.info("Không có thông tin nào thay đổi.")
