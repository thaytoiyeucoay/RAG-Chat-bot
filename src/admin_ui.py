import streamlit as st
import os
import shutil
from src.error_handler import handle_errors, safe_execute
from src.db_builder import build_vector_store

def display_admin_interface():
    """Hiển thị giao diện quản trị để quản lý các bộ kiến thức."""
    st.title("🔑 Trang Quản Trị")
    st.markdown("---_---")
    st.header("📚 Thêm Bộ Kiến Thức Mới")

    # Form để thêm kiến thức mới
    with st.form("new_knowledge_base_form", clear_on_submit=True):
        col1, col2 = st.columns([1, 2])
        with col1:
            knowledge_base_name = st.text_input(
                "**Tên bộ kiến thức**",
                placeholder="Ví dụ: Kinh tế học vĩ mô",
                help="Đặt tên ngắn gọn, không dấu, không khoảng trắng. Ví dụ: 'KinhTeHoc'"
            )
        with col2:
            uploaded_files = st.file_uploader(
                "**Tải lên tài liệu (.txt, .pdf, .md)**",
                accept_multiple_files=True,
                type=["txt", "pdf", "md"]
            )

        submitted = st.form_submit_button("🚀 Bắt đầu xây dựng Vector Store")

        if submitted:
            if not knowledge_base_name:
                st.error("Vui lòng nhập tên cho bộ kiến thức.")
            elif not uploaded_files:
                st.error("Vui lòng tải lên ít nhất một tài liệu.")
            else:
                with st.spinner(f"Đang xử lý {len(uploaded_files)} tệp cho bộ kiến thức '{knowledge_base_name}'..."):
                    success = build_vector_store(knowledge_base_name, uploaded_files)
                    if success:
                        st.success(f"Đã tạo thành công bộ kiến thức '{knowledge_base_name}'!")
                        st.balloons()
                    else:
                        st.error(f"Xảy ra lỗi khi tạo bộ kiến thức '{knowledge_base_name}'. Vui lòng kiểm tra logs.")

    st.markdown("---_---")
    st.header("🗂️ Các Bộ Kiến Thức Hiện Có")

    vector_store_path = "vectorstore_google"
    if os.path.exists(vector_store_path) and os.path.isdir(vector_store_path):
        knowledge_bases = [d for d in os.listdir(vector_store_path) if os.path.isdir(os.path.join(vector_store_path, d))]
        
        if not knowledge_bases:
            st.info("Chưa có bộ kiến thức nào được tạo.")
        else:
            st.markdown("Dưới đây là danh sách các bộ kiến thức đã được tạo:")
            for kb_name in sorted(knowledge_bases):
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"- **{kb_name}**")
                    with col2:
                        if st.button("🗑️ Xóa", key=f"delete_{kb_name}", help=f"Xóa vĩnh viễn bộ kiến thức {kb_name}"):
                            # Use session state to manage confirmation for each KB
                            st.session_state[f'confirm_delete_{kb_name}'] = True
                
                # Show confirmation dialog if requested
                if st.session_state.get(f'confirm_delete_{kb_name}'):
                    with st.expander(f"**Xác nhận xóa '{kb_name}'?**", expanded=True):
                        st.warning(f"Hành động này không thể hoàn tác. Toàn bộ dữ liệu của **{kb_name}** sẽ bị xóa vĩnh viễn.")
                        col_confirm, col_cancel = st.columns(2)
                        with col_confirm:
                            if st.button("🔴 Có, tôi chắc chắn", key=f"confirm_btn_{kb_name}"):
                                kb_path = os.path.join(vector_store_path, kb_name)
                                try:
                                    shutil.rmtree(kb_path)
                                    st.success(f"Đã xóa thành công bộ kiến thức '{kb_name}'.")
                                    del st.session_state[f'confirm_delete_{kb_name}'] # Clean up session state
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Lỗi khi xóa thư mục: {e}")
                        with col_cancel:
                            if st.button("Hủy", key=f"cancel_btn_{kb_name}"):
                                del st.session_state[f'confirm_delete_{kb_name}'] # Clean up session state
                                st.rerun()
    else:
        st.warning(f"Thư mục '{vector_store_path}' không tồn tại. Vui lòng tạo bộ kiến thức đầu tiên.")

# To run this page directly for testing:
if __name__ == "__main__":
    display_admin_interface()
