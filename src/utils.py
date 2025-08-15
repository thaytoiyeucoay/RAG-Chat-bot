# src/utils.py
from fpdf import FPDF
from langchain_core.messages import HumanMessage
import datetime
import os

def export_chat_to_pdf(chat_history, user_name):
    """Xuất lịch sử chat ra file PDF với xử lý lỗi."""
    try:
        # Sử dụng font mặc định thay vì DejaVu để tránh lỗi
        pdf = FPDF()
        pdf.add_page()
        
        # Header
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, f'Lich su chat cua {user_name}', 0, 1, 'C')
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 8, f'Ngay xuat: {datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")}', 0, 1, 'L')
        pdf.ln(10)

        for message in chat_history:
            is_user = isinstance(message, HumanMessage)
            role = "Nguoi dung" if is_user else "Tro ly AI"
            
            # Role header
            pdf.set_font('Arial', 'B', 12)
            pdf.set_fill_color(230, 230, 230)
            pdf.cell(0, 10, f'{role}:', 0, 1, 'L', fill=True)
            
            # Message content - chuyển đổi tiếng Việt thành ASCII
            pdf.set_font('Arial', '', 11)
            content = message.content.encode('ascii', 'ignore').decode('ascii')
            if len(content) > 500:  # Giới hạn độ dài để tránh lag
                content = content[:500] + "..."
            pdf.multi_cell(0, 8, content)
            pdf.ln(5)

        return pdf.output(dest='S').encode('latin-1')
    
    except Exception as e:
        print(f"Lỗi xuất PDF: {e}")
        # Trả về PDF trống nếu có lỗi
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, 'Loi xuat file PDF', 0, 1, 'C')
        return pdf.output(dest='S').encode('latin-1')
