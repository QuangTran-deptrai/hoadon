# Sử dụng Python 3.11 slim 
FROM python:3.11-slim

# Thiết lập thư mục làm việc trong container
WORKDIR /app

# Copy file requirements và cài đặt dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ source code vào container
COPY . .

# Mở port 8501 (Port mặc định của Streamlit)
EXPOSE 8501

# Lệnh chạy ứng dụng khi container khởi động
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
