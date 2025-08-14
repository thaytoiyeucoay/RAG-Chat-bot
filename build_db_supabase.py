# build_db_supabase.py
import os
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
# >>> THAY ĐỔI QUAN TRỌNG: Import SupabaseVectorStore
from langchain_community.vectorstores import SupabaseVectorStore
from supabase.client import Client, create_client
from dotenv import load_dotenv

# Tải các biến môi trường
load_dotenv()
if "GOOGLE_API_KEY" not in os.environ or "SUPABASE_URL" not in os.environ or "SUPABASE_KEY" not in os.environ:
    print("Lỗi: Vui lòng kiểm tra các biến GOOGLE_API_KEY, SUPABASE_URL, và SUPABASE_KEY trong file .env")
    exit()

supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")

# Khởi tạo client cho Supabase
supabase: Client = create_client(supabase_url, supabase_key)

# --- 1. TẢI VÀ PHÂN MẢNH DỮ LIỆU ---
print("Đang tải và phân mảnh dữ liệu từ thư mục 'data/'...")
DATA_PATH = "C:\\Users\\VCSVietNam\\duybk\\cs50_notes"
documents = []
for filename in os.listdir(DATA_PATH):
    if filename.endswith(".txt"):
        filepath = os.path.join(DATA_PATH, filename)
        loader = TextLoader(filepath, encoding='utf-8')
        documents.extend(loader.load())

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
chunks = text_splitter.split_documents(documents)
print(f"Đã chia {len(documents)} tài liệu thành {len(chunks)} chunks.")

# --- 2. TẠO EMBEDDINGS VÀ LƯU VÀO SUPABASE ---
print("Bắt đầu tạo embeddings bằng Google API và lưu vào Supabase...")
embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

# >>> THAY ĐỔI QUAN TRỌNG: Sử dụng SupabaseVectorStore
# LangChain sẽ tự động gọi API Google và lưu kết quả vào bảng 'documents' của Supabase
vector_store = SupabaseVectorStore.from_documents(
    documents=chunks,
    embedding=embeddings,
    client=supabase,
    table_name="documents",
    query_name="match_documents",
)
print("-" * 50)
print("THÀNH CÔNG! Đã lưu dữ liệu vào Supabase Vector Store.")