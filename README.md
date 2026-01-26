# 🧾 Invoice Extraction App

Ứng dụng trích xuất, phân loại và tổng hợp dữ liệu hóa đơn (Invoice) từ file PDF, hỗ trợ xuất báo cáo Excel cho kế toán.
Được xây dựng bằng **Python (Streamlit)** và tối ưu hóa cho việc triển khai Self-Hosted (Server riêng).

## ✨ Tính năng chính
*   **Trích xuất thông tin:** Tự động đọc Số hóa đơn, Ngày, MST Bán/Mua, Tiền trước thuế, Thuế, Tổng tiền...
*   **Phân loại tự động:** Nhận diện loại chi phí (Ăn uống, Viễn thông, Tiếp khách...) dựa trên từ khóa.
*   **Xử lý hàng loạt:** Upload nhiều file PDF cùng lúc.
*   **Xuất báo cáo:** Tải về file Excel tổng hợp đầy đủ thông tin.

## 📂 Cấu trúc dự án
*   `app.py`: Giao diện chính (Streamlit).
*   `extract_invoices.py`: Core logic xử lý PDF và trích xuất dữ liệu.
*   `Dockerfile` & `docker-compose.yml`: Cấu hình deployment (Docker).
*   `requirements.txt`: Danh sách thư viện Python.
*   `deployment_guide.md`: Hướng dẫn chi tiết cho IT triển khai Server.

---

## � Cài đặt & Chạy (Môi trường Dev/Local)

Dành cho Developer hoặc chạy thử trên máy cá nhân Windows/Mac.

### Yêu cầu
*   Python 3.9 trở lên (Khuyên dùng 3.11).

### Các bước
1.  **Clone code** và mở terminal tại thư mục dự án.
2.  **Cài đặt thư viện:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Chạy ứng dụng:**
    ```bash
    streamlit run app.py
    ```
    Truy cập tại: `http://localhost:8501`

---

## 🚀 Triển khai Server (Production)


**Phương pháp khuyến nghị:** Sử dụng **Docker**.

### Cách 1: Chạy bằng Docker Compose (Nhanh nhất)
*Yêu cầu Server đã cài Docker & Docker Compose.*

1.  Copy toàn bộ source code lên Server.
2.  Mở terminal/CMD tại thư mục code.
3.  Chạy lệnh:
    ```bash
    docker-compose up -d --build
    ```
4.  App sẽ chạy ngầm tại Port **8501**.
5.  (Tùy chọn) Cấu hình Nginx Reverse Proxy để trỏ domain `kiemtrahoadon.psd.com.vn` về port 8501.

### Cách 2: Chạy Thủ công trên Windows Server
*Nếu không dùng Docker.*

1.  Cài đặt **Python 3.11** 64-bit trên Windows Server.
2.  Cài đặt thư viện: `pip install -r requirements.txt`.
3.  Tạo script chạy nền hoặc dùng Task Scheduler để chạy lệnh:
    ```bash
    streamlit run app.py --server.port=8501
    ```

---

## 📝 Lưu ý quan trọng
*   **Upload File Lớn:** Nếu dùng Nginx, cần cấu hình `client_max_body_size 100M;` để không bị lỗi khi upload PDF dung lượng cao.
*   **Bảo mật:** Khuyến nghị setup HTTPS (SSL) nếu truy cập từ môi trường Internet công cộng.
