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

## 🔄 Cách cập nhật Code

Khi bạn muốn sửa code hoặc thêm tính năng:

1. Sửa code trên máy tính của bạn (Local).
2. Chạy thử `streamlit run app.py` để đảm bảo code chạy đúng.
3. **Chạy các lệnh Git để đẩy code mới lên:**
   ```bash
   git add .
   git commit -m "Mô tả thay đổi mới"
   git push
   ```

**Streamlit Cloud sẽ tự động phát hiện thay đổi và cập nhật ứng dụng của bạn trong vòng vài phút. Bạn KHÔNG cần phải xóa app cũ hay deploy lại từ đầu.**

## 🌐 Tùy chỉnh đường dẫn (URL)

Mặc định Streamlit sẽ tạo link ngẫu nhiên. Để sửa thành link đẹp hơn (ví dụ: `hoadon-congty.streamlit.app`):

1. Vào dashboard **Streamlit Cloud**.
2. Nhấn vào dấu **3 chấm (⋮)** bên cạnh ứng dụng của bạn -> Chọn **Settings**.
3. Tại mục **General**, tìm phần **Custom subdomain**.
4. Nhập tên bạn muốn và lưu lại.

