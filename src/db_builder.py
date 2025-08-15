# src/db_builder.py
import os
import shutil
import tempfile
from langchain_community.document_loaders import TextLoader, PyPDFLoader, UnstructuredMarkdownLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

# Tải biến môi trường
load_dotenv()

def get_document_loader(file_path):
    """Chọn loader phù hợp dựa trên phần mở rộng của file."""
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    if ext == '.txt':
        return TextLoader(file_path, encoding='utf-8')
    elif ext == '.pdf':
        return PyPDFLoader(file_path)
    elif ext == '.md':
        return UnstructuredMarkdownLoader(file_path)
    else:
        # Bỏ qua các file không hỗ trợ
        print(f"Định dạng file không được hỗ trợ: {ext}")
        return None

def build_vector_store(knowledge_base_name: str, uploaded_files: list) -> bool:
    """
    Xây dựng một vector store mới từ các file được tải lên.

    Args:
        knowledge_base_name: Tên của bộ kiến thức (dùng làm tên thư mục).
        uploaded_files: Danh sách các file được tải lên từ Streamlit.

    Returns:
        True nếu xây dựng thành công, False nếu thất bại.
    """
    if not uploaded_files or not knowledge_base_name:
        return False

    # Chuẩn hóa tên để tránh lỗi path
    safe_kb_name = ''.join(c for c in knowledge_base_name if c.isalnum() or c in ('-', '_')).rstrip()
    db_path = os.path.join("vectorstore_google", safe_kb_name)

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # 1. Lưu các file tải lên vào thư mục tạm
            print(f"Đang lưu {len(uploaded_files)} file vào thư mục tạm: {temp_dir}")
            file_paths = []
            for uploaded_file in uploaded_files:
                file_path = os.path.join(temp_dir, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                file_paths.append(file_path)

            # 2. Xóa database cũ nếu tồn tại
            if os.path.exists(db_path):
                print(f"Phát hiện database cũ. Đang xóa thư mục: {db_path}")
                shutil.rmtree(db_path)

            # 3. Tải và phân mảnh dữ liệu
            print("Bắt đầu tải và phân mảnh tài liệu...")
            documents = []
            for file_path in file_paths:
                loader = get_document_loader(file_path)
                if loader:
                    documents.extend(loader.load())
            
            if not documents:
                print("Không có tài liệu nào được tải thành công.")
                return False

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=150)
            chunks = text_splitter.split_documents(documents)
            print(f"Đã chia {len(documents)} tài liệu thành {len(chunks)} chunks.")

            # 4. Tạo embeddings và lưu vào ChromaDB
            print("Bắt đầu tạo embeddings và lưu vào ChromaDB...")
            embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
            db = Chroma.from_documents(chunks, embeddings, persist_directory=db_path)
            print(f"Đã lưu thành công vector store vào: {db_path}")

        return True

    except Exception as e:
        print(f"Lỗi trong quá trình xây dựng vector store: {e}")
        # Dọn dẹp nếu có lỗi
        if os.path.exists(db_path):
            shutil.rmtree(db_path)
        return False
