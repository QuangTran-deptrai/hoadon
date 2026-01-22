# 🧾 Invoice Extraction Web App

Công cụ trích xuất dữ liệu hóa đơn PDF tự động, được xây dựng bằng Python và Streamlit.

## 📂 Cấu trúc dự án
- `app.py`: Giao diện web chính.
- `extract_invoices.py`: Logic xử lý và trích xuất dữ liệu từ PDF.
- `requirements.txt`: Các thư viện cần thiết.

## 🚀 Cách chạy trên máy cá nhân (Local)

1. **Cài đặt Python** (nếu chưa có).
2. **Cài đặt thư viện:**
   Mở terminal (CMD/PowerShell) tại thư mục dự án và chạy:
   ```bash
   pip install -r requirements.txt
   ```
3. **Chạy ứng dụng:**
   ```bash
   streamlit run app.py
   ```
   Ứng dụng sẽ tự động mở trên trình duyệt tại địa chỉ `http://localhost:8501`.

## ☁️ Cách Deploy lên Streamlit Community Cloud (Miễn phí)

Để người khác có thể sử dụng qua mạng, bạn có thể đưa ứng dụng lên cloud miễn phí của Streamlit:

1. **Đẩy code lên GitHub:**
   - Tạo một repository mới trên GitHub (Public).
   - Upload toàn bộ các file trong thư mục này lên repository đó.

2. **Đăng nhập Streamlit Cloud:**
   - Truy cập [share.streamlit.io](https://share.streamlit.io/).
   - Đăng nhập bằng tài khoản GitHub.

3. **Deploy App:**
   - Nhấn **"New app"**.
   - Chọn repository bạn vừa tạo.
   - **Main file path:** Điền `app.py`.
   - Nhấn **"Deploy"**.

Sau khoảng 1-2 phút, bạn sẽ nhận được một đường link (ví dụ: `https://invoice-extractor.streamlit.app`) để chia sẻ cho mọi người sử dụng.
