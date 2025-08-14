# update_db.py (Script thông minh để cập nhật dữ liệu)
import os
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

# Tải API Key và các thiết lập
load_dotenv()
if "GOOGLE_API_KEY" not in os.environ:
    print("Lỗi: Vui lòng đặt GOOGLE_API_KEY trong file .env")
    exit()

print("Bắt đầu quá trình cập nhật cơ sở dữ liệu...")

# --- 1. ĐỊNH NGHĨA CÁC THAM SỐ ---
DATA_PATH = "data/"
DB_PATH = "vectorstore_google/"
EMBEDDING_MODEL = "models/text-embedding-004"

# --- 2. KIỂM TRA XEM DATABASE ĐÃ TỒN TẠI CHƯA ---
if not os.path.exists(DB_PATH):
    print(f"Lỗi: Không tìm thấy cơ sở dữ liệu tại '{DB_PATH}'.")
    print("Vui lòng chạy file 'build_db_google.py' trước để tạo cơ sở dữ liệu ban đầu.")
    exit()

# --- 3. LẤY DANH SÁCH CÁC FILE ĐÃ ĐƯỢC XỬ LÝ ---
# Tải lại database hiện có
print(f"Đang tải cơ sở dữ liệu hiện có từ '{DB_PATH}'...")
embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)
db = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)

# Lấy metadata của tất cả các chunk đã có trong DB
existing_docs_metadata = db.get()['metadatas']
# Lấy ra danh sách các nguồn (đường dẫn file) duy nhất đã được xử lý
existing_sources = set(doc['source'] for doc in existing_docs_metadata)
print(f"Đã tìm thấy {len(existing_sources)} tài liệu đã được xử lý trong database.")

# --- 4. TÌM CÁC FILE MỚI CẦN XỬ LÝ ---
all_files_in_data = set()
for filename in os.listdir(DATA_PATH):
    if filename.endswith(".txt"):
        # Tạo đường dẫn chuẩn hóa để so sánh
        full_path = os.path.join(DATA_PATH, filename).replace('\\', '/')
        all_files_in_data.add(full_path)

# So sánh để tìm ra những file chưa có trong DB
new_files_to_process = all_files_in_data - existing_sources

# --- 5. XỬ LÝ VÀ THÊM CÁC FILE MỚI VÀO DATABASE ---
if not new_files_to_process:
    print("\nKhông có file mới nào cần thêm. Cơ sở dữ liệu đã được cập nhật.")
else:
    print(f"\nPhát hiện {len(new_files_to_process)} file mới cần xử lý:")
    for file_path in new_files_to_process:
        print(f"- {os.path.basename(file_path)}")

    new_documents = []
    for file_path in new_files_to_process:
        loader = TextLoader(file_path, encoding='utf-8')
        new_documents.extend(loader.load())
    
    print("\nĐang phân mảnh các tài liệu mới...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=150)
    new_chunks = text_splitter.split_documents(new_documents)
    
    print(f"Đang thêm {len(new_chunks)} chunks mới vào cơ sở dữ liệu...")
    # SỬ DỤNG db.add_documents ĐỂ THÊM VÀO DB HIỆN CÓ
    db.add_documents(new_chunks)
    
    print("-" * 50)
    print("THÀNH CÔNG! Đã cập nhật xong cơ sở dữ liệu.")