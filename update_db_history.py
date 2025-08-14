# update_db.py (Phiên bản nâng cấp cho Supabase)
import os
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import SupabaseVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from supabase.client import Client, create_client
from dotenv import load_dotenv

# --- 0. TẢI CÁC THIẾT LẬP ---
load_dotenv()
if "GOOGLE_API_KEY" not in os.environ or "SUPABASE_URL" not in os.environ or "SUPABASE_KEY" not in os.environ:
    print("Lỗi: Vui lòng kiểm tra các biến môi trường trong file .env")
    exit()

print("Bắt đầu quá trình cập nhật cơ sở dữ liệu CS50 trên Supabase...")

# --- 1. ĐỊNH NGHĨA CÁC THAM SỐ ---
# Thư mục chứa dữ liệu CS50
DATA_PATH = "C:/Users/VCSVietNam/duybk/db_history" 
# Thông tin bảng và hàm trên Supabase cho CS50
TABLE_NAME = "history_documents"
QUERY_NAME = "match_history_documents"
EMBEDDING_MODEL = "models/embedding-001"

# --- 2. KẾT NỐI TỚI SUPABASE ---
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)
embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)

# Khởi tạo đối tượng vector store để tương tác

vector_store = SupabaseVectorStore(
    client=supabase,
    embedding=embeddings,
    table_name=TABLE_NAME,
    query_name=QUERY_NAME
)

# --- 3. LẤY DANH SÁCH CÁC FILE ĐÃ ĐƯỢC XỬ LÝ TỪ SUPABASE ---
try:
    # Lấy metadata của tất cả các dòng đã có trong bảng
    response = supabase.table(TABLE_NAME).select("metadata").execute()
    existing_docs_metadata = response.data
except Exception as e:
    print(f"Lỗi khi lấy metadata từ Supabase: {e}")
    existing_docs_metadata = []

# Lấy ra danh sách các nguồn (đường dẫn file) duy nhất đã được xử lý
existing_sources = set(doc['metadata']['source'] for doc in existing_docs_metadata if 'metadata' in doc and 'source' in doc['metadata'])
print(f"Đã tìm thấy {len(existing_sources)} tài liệu CS50 đã được xử lý trong database.")

# --- 4. TÌM CÁC FILE MỚI CẦN XỬ LÝ ---
all_files_in_data = set()
for filename in os.listdir(DATA_PATH):
    if filename.endswith(".txt"):
        full_path = os.path.join(DATA_PATH, filename).replace('\\', '/')
        all_files_in_data.add(full_path)

# So sánh để tìm ra những file chưa có trong DB
new_files_to_process = all_files_in_data - existing_sources

# --- 5. XỬ LÝ VÀ THÊM CÁC FILE MỚI VÀO DATABASE ---
if not new_files_to_process:
    print("\nKhông có file mới nào cần thêm. Cơ sở dữ liệu CS50 đã được cập nhật.")
else:
    print(f"\nPhát hiện {len(new_files_to_process)} file CS50 mới cần xử lý:")
    for file_path in new_files_to_process:
        print(f"- {os.path.basename(file_path)}")

    new_documents = []
    for file_path in new_files_to_process:
        loader = TextLoader(file_path, encoding='utf-8')
        new_documents.extend(loader.load())
    
    print("\nĐang phân mảnh các tài liệu mới...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=150)
    new_chunks = text_splitter.split_documents(new_documents)

    
    print(f"Đang thêm {len(new_chunks)} chunks mới vào cơ sở dữ liệu Supabase...")
    # >>> SỬ DỤNG vector_store.add_documents ĐỂ THÊM VÀO DB HIỆN CÓ
    vector_store.add_documents(new_chunks)
    
    print("-" * 50)
    print("THÀNH CÔNG! Đã cập nhật xong cơ sở dữ liệu CS50.")