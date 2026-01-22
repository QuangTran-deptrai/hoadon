# Mô tả Quy trình Đọc và Tổng hợp Hóa đơn

Tài liệu này mô tả chi tiết quy trình hoạt động của tool `extract_invoices.py` và các trường hợp ngoại lệ.

## 1. Quy trình xử lý (Workflow)

Quy trình được thực hiện tuần tự qua 4 bước chính:

### Bước 1: Đọc dữ liệu (Input)
*   Chương trình quét toàn bộ file `.pdf` trong thư mục `invoices_input`.
*   **Trích xuất văn bản (Text Extraction):**
    *   **Ưu tiên 1:** Sử dụng thư viện `pdfplumber` để đọc lớp text trực tiếp từ file PDF.
    *   **Ưu tiên 2 (Fallback):** Nếu file PDF không có lớp text (ví dụ: file scan, file ảnh), chương trình sẽ tự động tìm kiếm file `.txt` (file kết quả OCR) có tên tương ứng trong cùng thư mục để đọc nội dung.

### Bước 2: Trích xuất thông tin chung (Header Parsing)
Sử dụng **Regular Expressions (Regex)** để tìm kiếm các mẫu (patterns) chuẩn cho các trường thông tin:
*   **Ngày hóa đơn:** Tìm các định dạng `dd/mm/yyyy`, `dd-mm-yyyy`, hoặc chuỗi "Ngày... tháng... năm...".
*   **Số hóa đơn:** Tìm các từ khóa như "Số:", "No:", "Invoice No" và lấy chuỗi ký tự số phía sau.
*   **Đơn vị bán:** Tìm dòng có chứa từ khóa "Đơn vị bán", "Công ty", "Chi nhánh" nằm ở phần đầu của hóa đơn. Bao gồm bước làm sạch tên (loại bỏ các từ xưng hô thừa như "Ông/Bà" hay mã số thuế dính kèm).

### Bước 3: Trích xuất chi tiết hàng hóa (Line Item Extraction)
Đây là phần phức tạp nhất, được thực hiện bằng cách duyệt qua từng dòng văn bản:
*   **Nhận diện dòng hàng:** Xác định dòng bắt đầu bằng số thứ tự (STT) và có chứa các dãy số phía sau (tương ứng với Số lượng, Đơn giá, Thành tiền).
*   **Xử lý tên hàng nhiều dòng (Multi-line merging):**
    *   *Merge Lên:* Nếu tên hàng bị ngắt quãng từ dòng trước, gộp dòng phía trên vào tên hàng hiện tại.
    *   *Merge Xuống:* Nếu dòng tiếp theo là phần mở rộng của tên hàng (ví dụ: mô tả chi tiết, hoặc khoảng thời gian `(01/12 - 31/12)`), gộp dòng đó vào tên hàng.
*   **Xử lý số liệu thông minh:**
    *   Tự động nhận diện đâu là cột Số lượng, Đơn giá, Thành tiền dựa trên số lượng các con số tìm được trong dòng.
    *   **Logic `Smart Amount Selection`:** Tự động tính toán `Qty * Price` để đối chiếu và chọn ra con số "Thành tiền" chính xác nhất (tránh nhầm lẫn với các cột khác như "Thuế suất" hoặc "Chiết khấu").
*   **Xử lý đặc biệt:**
    *   Nhận diện và trích xuất các dòng **"Phụ thu", "Phí dịch vụ"** ngay cả khi chỉ có một con số (Thành tiền) mà không cần có Số lượng hay Đơn giá.

### Bước 4: Tổng hợp tài chính & Xuất Excel
*   Trích xuất **Tổng tiền**, **Tiền thuế**, **Số tiền trước thuế** từ phần chân trang (footer).
*   **Logic bổ sung:** Nếu hóa đơn không có thuế (hóa đơn bán hàng trực tiếp), tự động gán `Số tiền trước thuế = Số tiền sau thuế`.
*   Kết quả cuối cùng được ghi vào file Excel `hoadon_tonghop.xlsx` với định dạng bảng chuyên nghiệp (merge cells cho các hóa đơn nhiều dòng).

---

## 2. Các trường hợp ngoại lệ (Exceptions)

Trong quá trình xử lý, chương trình có thể gặp khó khăn hoặc **không đọc được** trong các trường hợp sau:

1.  **PDF Scan/Ảnh hoàn toàn (Image-only PDFs):**
    *   **Hiện tượng:** File PDF chỉ là một tấm ảnh chụp, không có lớp text để bôi đen và **không có file .txt OCR đi kèm**.
    *   **Kết quả:** Chương trình báo `Empty PDF text` và trả về kết quả rỗng (Số lượng items: 0, các trường thông tin ghi là "không nhận diện").

2.  **Lỗi Font/Encoding (Corrupted Text):**
    *   **Hiện tượng:** File PDF có lớp text nhưng bị lỗi font hoặc mã hóa sai (khi copy paste ra văn bản chỉ thấy các ký tự lạ như `Ã Ê...`).
    *   **Kết quả:** Các biểu thức chính quy (Regex) không thể khớp được các từ khóa tiếng Việt chuẩn -> Không trích xuất được dữ liệu đúng.

3.  **Bố cục quá dị biệt (Non-standard Layout):**
    *   **Hiện tượng:** Các hóa đơn không tuân theo bố cục thông thường. Ví dụ: Số hóa đơn nằm lẫn trong một đoạn văn bản dài, hoặc bảng hàng hóa không phân chia cột rõ ràng, các con số dính liền nhau không có khoảng cách.
    *   **Kết quả:** Có thể dẫn đến việc bỏ sót hàng hóa hoặc nhầm lẫn vị trí giữa cột "Đơn giá" và "Thành tiền".

4.  **Hóa đơn viết tay hoặc chất lượng quá mờ (Đối với OCR):**
    *   Nếu sử dụng file OCR, chữ quá mờ hoặc nét viết tay có thể khiến máy nhận diện sai ký tự (ví dụ: số `1` nhận nhầm thành chữ `l`, số `0` nhận nhầm thành chữ `O`).
    *   **Kết quả:** Dẫn đến sai lệch về số liệu hoặc tên hàng hóa.
