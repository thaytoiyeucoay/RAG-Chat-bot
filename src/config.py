# src/config.py
"""Cấu hình tối ưu cho ứng dụng."""

# Performance Settings
MAX_CHAT_HISTORY = 50  # Giới hạn tin nhắn trong memory
MAX_MESSAGE_LENGTH = 2000  # Giới hạn độ dài tin nhắn
MAX_SEARCH_RESULTS = 10  # Giới hạn kết quả tìm kiếm
MIN_SEARCH_LENGTH = 3  # Độ dài tối thiểu để tìm kiếm
CACHE_TTL = 60  # Cache timeout (giây)
MAX_VECTOR_STORES = 5  # Giới hạn số vector stores

# UI Settings
DEFAULT_THEME = "light"
DEFAULT_USER_AVATAR = "👤"
DEFAULT_AI_AVATAR = "🤖"

# Database Settings
DB_QUERY_LIMIT = 50  # Giới hạn query database
DB_TIMEOUT = 10  # Timeout cho database queries

# Error Messages
ERROR_MESSAGES = {
    'pdf_export': 'Lỗi xuất PDF. Vui lòng thử lại.',
    'database': 'Lỗi kết nối cơ sở dữ liệu.',
    'search': 'Lỗi tìm kiếm. Vui lòng thử lại.',
    'load_history': 'Không thể tải lịch sử chat.',
    'save_message': 'Không thể lưu tin nhắn.',
    'generic': 'Đã xảy ra lỗi. Vui lòng thử lại.'
}

# Admin Settings
ADMIN_EMAIL = "duy@gmail.com"

# Logging Settings
LOG_LEVEL = "INFO"
LOG_FILE = "app.log"
