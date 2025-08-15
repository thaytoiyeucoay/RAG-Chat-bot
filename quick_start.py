# quick_start.py
"""Script khởi động nhanh với kiểm tra tự động."""

import os
import sys
import subprocess
import time

def check_requirements():
    """Kiểm tra và cài đặt requirements nếu cần."""
    print("🔍 Kiểm tra dependencies...")
    
    try:
        import streamlit
        import supabase
        import langchain
        print("✅ Dependencies đã sẵn sàng")
        return True
    except ImportError as e:
        print(f"❌ Thiếu dependency: {e}")
        print("📦 Đang cài đặt requirements...")
        
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Cài đặt thành công")
            return True
        except subprocess.CalledProcessError:
            print("❌ Lỗi cài đặt dependencies")
            return False

def check_env_file():
    """Kiểm tra file .env."""
    if not os.path.exists('.env'):
        print("⚠️ Không tìm thấy file .env")
        print("📝 Tạo file .env từ template...")
        
        env_template = """SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here
GOOGLE_API_KEY=your_google_api_key_here"""
        
        with open('.env', 'w') as f:
            f.write(env_template)
        
        print("✅ Đã tạo file .env template")
        print("🔧 Vui lòng cập nhật thông tin trong file .env")
        return False
    
    print("✅ File .env đã tồn tại")
    return True

def optimize_startup():
    """Tối ưu khởi động."""
    print("🚀 Tối ưu khởi động...")
    
    # Clear cache cũ nếu có
    cache_dirs = ['.streamlit', '__pycache__', 'src/__pycache__']
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            import shutil
            try:
                shutil.rmtree(cache_dir)
                print(f"🧹 Đã xóa cache: {cache_dir}")
            except:
                pass
    
    print("✅ Tối ưu hoàn tất")

def start_app():
    """Khởi động ứng dụng."""
    print("\n🎯 Khởi động Chatbot...")
    print("🌐 Ứng dụng sẽ mở tại: http://localhost:8501")
    print("⏹️ Nhấn Ctrl+C để dừng\n")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.headless", "true",
            "--server.enableCORS", "false",
            "--server.enableXsrfProtection", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Đã dừng ứng dụng")

def main():
    """Main function."""
    print("="*50)
    print("🤖 CHATBOT QUICK START")
    print("="*50)
    
    # Kiểm tra requirements
    if not check_requirements():
        return
    
    # Kiểm tra .env
    env_ready = check_env_file()
    
    # Tối ưu
    optimize_startup()
    
    if not env_ready:
        print("\n⚠️ Vui lòng cập nhật file .env trước khi chạy ứng dụng")
        return
    
    # Khởi động
    start_app()

if __name__ == "__main__":
    main()
