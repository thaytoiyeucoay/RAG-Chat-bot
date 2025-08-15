# src/error_handler.py
import streamlit as st
import traceback
import logging
from functools import wraps

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

def handle_errors(func):
    """Decorator để xử lý lỗi một cách graceful."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_msg = f"Lỗi trong {func.__name__}: {str(e)}"
            logging.error(error_msg)
            logging.error(traceback.format_exc())
            
            # Hiển thị lỗi user-friendly
            st.error(f"Đã xảy ra lỗi: {str(e)}")
            
            # Trả về giá trị mặc định tùy theo loại function
            if func.__name__.startswith('load_'):
                return []
            elif func.__name__.startswith('get_'):
                return 0 if 'count' in func.__name__ else {}
            else:
                return None
    return wrapper

def safe_execute(func, default_value=None, error_message="Có lỗi xảy ra"):
    """Thực thi function một cách an toàn với fallback."""
    try:
        return func()
    except Exception as e:
        logging.error(f"Safe execute error: {str(e)}")
        if error_message:
            st.warning(error_message)
        return default_value

class PerformanceMonitor:
    """Monitor hiệu suất của các operations."""
    
    @staticmethod
    def time_function(func):
        """Decorator để đo thời gian thực thi."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            import time
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            
            if execution_time > 2:  # Cảnh báo nếu > 2 giây
                logging.warning(f"{func.__name__} took {execution_time:.2f} seconds")
            
            return result
        return wrapper
