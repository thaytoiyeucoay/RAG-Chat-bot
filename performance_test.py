# performance_test.py
"""Script kiểm tra hiệu suất của ứng dụng sau khi tối ưu."""

import time
import psutil
import os
import sys
from datetime import datetime

def measure_startup_time():
    """Đo thời gian khởi động ứng dụng."""
    print("🚀 Đang kiểm tra thời gian khởi động...")
    start_time = time.time()
    
    try:
        # Import các module chính
        from src.rag_components import load_base_components
        from src.database import load_messages_from_db
        from src.chatbot_ui import display_chatbot_interface
        
        # Tải components
        vector_stores, prompt, supabase_client = load_base_components()
        
        end_time = time.time()
        startup_time = end_time - start_time
        
        print(f"✅ Thời gian khởi động: {startup_time:.2f} giây")
        return startup_time
    except Exception as e:
        print(f"❌ Lỗi khởi động: {str(e)}")
        return None

def check_memory_usage():
    """Kiểm tra mức sử dụng bộ nhớ."""
    print("\n💾 Đang kiểm tra sử dụng bộ nhớ...")
    
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    memory_mb = memory_info.rss / 1024 / 1024
    
    print(f"📊 Bộ nhớ sử dụng: {memory_mb:.1f} MB")
    
    if memory_mb < 200:
        print("✅ Mức sử dụng bộ nhớ: Tốt")
    elif memory_mb < 500:
        print("⚠️ Mức sử dụng bộ nhớ: Trung bình")
    else:
        print("❌ Mức sử dụng bộ nhớ: Cao")
    
    return memory_mb

def check_file_sizes():
    """Kiểm tra kích thước các file quan trọng."""
    print("\n📁 Đang kiểm tra kích thước files...")
    
    important_files = [
        'app.py',
        'src/chatbot_ui.py',
        'src/database.py',
        'src/rag_components.py',
        'requirements.txt'
    ]
    
    total_size = 0
    for file_path in important_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            size_kb = size / 1024
            total_size += size
            print(f"  {file_path}: {size_kb:.1f} KB")
    
    total_mb = total_size / 1024 / 1024
    print(f"📦 Tổng kích thước core files: {total_mb:.2f} MB")
    
    return total_mb

def check_dependencies():
    """Kiểm tra các dependencies."""
    print("\n📚 Đang kiểm tra dependencies...")
    
    required_modules = [
        'streamlit',
        'supabase',
        'langchain',
        'chromadb',
        'fpdf'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} - THIẾU")
            missing_modules.append(module)
    
    return missing_modules

def generate_report():
    """Tạo báo cáo tổng hợp."""
    print("\n" + "="*50)
    print("📋 BÁO CÁO HIỆU SUẤT")
    print("="*50)
    print(f"🕐 Thời gian kiểm tra: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Kiểm tra startup time
    startup_time = measure_startup_time()
    
    # Kiểm tra memory
    memory_usage = check_memory_usage()
    
    # Kiểm tra file sizes
    file_size = check_file_sizes()
    
    # Kiểm tra dependencies
    missing_deps = check_dependencies()
    
    # Tổng kết
    print("\n🎯 TỔNG KẾT:")
    
    if startup_time and startup_time < 5:
        print("✅ Khởi động nhanh")
    elif startup_time:
        print("⚠️ Khởi động chậm")
    
    if memory_usage and memory_usage < 200:
        print("✅ Sử dụng bộ nhớ hiệu quả")
    elif memory_usage:
        print("⚠️ Sử dụng bộ nhớ cao")
    
    if not missing_deps:
        print("✅ Tất cả dependencies đã cài đặt")
    else:
        print(f"❌ Thiếu {len(missing_deps)} dependencies")
    
    print("\n🚀 Các tối ưu đã áp dụng:")
    print("  • Lazy loading components")
    print("  • Database query caching")
    print("  • Memory management")
    print("  • Error handling")
    print("  • Performance monitoring")
    print("  • UI optimization")

if __name__ == "__main__":
    generate_report()
