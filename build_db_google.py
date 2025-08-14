# build_db_google.py
import shutil
import os
import asyncio
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
# >>> THAY ĐỔI QUAN TRỌNG: Import công cụ embedding mới của Google
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

# Tải API Key
load_dotenv()
if "GOOGLE_API_KEY" not in os.environ:
    print("Lỗi: Vui lòng đặt GOOGLE_API_KEY trong file .env")
    exit()

# --- 1. ĐỊNH NGHĨA CÁC THAM SỐ ---
# Dùng lại dữ liệu CS50 cũ
DATA_PATH = "C:/Users/VCSVietNam/duybk/cs50_notes" 
# >>> THAY ĐỔI QUAN TRỌNG: Tạo một thư mục DB MỚI để không ghi đè lên cái cũ
DB_PATH = "vectorstore_google/" 

# --- 2. XÓA DATABASE CŨ (NẾU CÓ) ĐỂ LÀM MỚI ---
if os.path.exists(DB_PATH):
    print(f"Phát hiện database cũ. Đang xóa thư mục: {DB_PATH}")
    shutil.rmtree(DB_PATH)

# --- 3. TẢI VÀ PHÂN MẢNH DỮ LIỆU (Giữ nguyên như cũ) ---
print("Đang tải và phân mảnh dữ liệu từ thư mục 'data/'...")
documents = []
for filename in os.listdir(DATA_PATH):
    if filename.endswith(".txt"):
        filepath = os.path.join(DATA_PATH, filename)
        loader = TextLoader(filepath, encoding='utf-8')
        documents.extend(loader.load())

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=150)
chunks = text_splitter.split_documents(documents)
print(f"Đã chia {len(documents)} tài liệu thành {len(chunks)} chunks.")

# --- 4. TẠO EMBEDDINGS BẰNG GOOGLE API VÀ LƯU VÀO DB ---
print("Bắt đầu tạo embeddings bằng Google API và lưu vào ChromaDB...")
print("Quá trình này có thể mất một lúc tùy thuộc vào số lượng tài liệu và tốc độ mạng...")

# >>> THAY ĐỔI QUAN TRỌNG: Sử dụng Google's embeddings model.
# Model 'text-embedding-004' là một lựa chọn rất tốt và hiệu quả.
embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

# Tạo ChromaDB từ các chunks và lưu vào thư mục mới.
# LangChain sẽ tự động gọi API của Google cho từng chunk để lấy vector.
db = Chroma.from_documents(chunks, embeddings, persist_directory=DB_PATH)

print("-" * 50)
print(f"THÀNH CÔNG! Đã lưu cơ sở dữ liệu vector mới vào thư mục: {DB_PATH}")