import requests
from bs4 import BeautifulSoup
import os

# Thư mục lưu file
os.makedirs("cs50_notes", exist_ok=True)

# Danh sách số bài lecture muốn lấy
lectures = range(0, 11)  # Lecture 0 đến 10

base_url = "https://cs50.harvard.edu/x/2024/notes/"

for lec in lectures:
    url = f"{base_url}{lec}/"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Không lấy được {url}")
        continue
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Xóa menu, footer nếu muốn
    for tag in soup(["nav", "header", "footer", "script", "style"]):
        tag.decompose()
    
    # Lấy text chính
    text = soup.get_text(separator="\n", strip=True)
    
    # Lưu file
    with open(f"cs50_notes/lecture_{lec}.txt", "w", encoding="utf-8") as f:
        f.write(text)
    
    print(f"Đã lưu Lecture {lec}")
