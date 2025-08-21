# AI Agent Collection

Bộ sưu tập các AI Agent với giao diện Streamlit kết nối với FastAPI backend.

## Cấu trúc dự án

```
agent-poem/
├── agent-poem.py          # Agent sáng tác thơ lục bát
├── agent-cv-evaluator.py  # Agent đánh giá CV
├── streamlit_app.py       # Frontend cho agent thơ
├── streamlit_cv_app.py    # Frontend cho agent đánh giá CV
├── requirements.txt       # Dependencies
└── README.md             # Hướng dẫn này
```

## Các Agent có sẵn

### 1. 🎭 Agent Thơ Lục Bát
- **Backend**: `agent-poem.py` (Port 8000)
- **Frontend**: `streamlit_app.py` (Port 8501)
- **Chức năng**: Sáng tác thơ lục bát theo chủ đề

### 2. 📄 Agent Đánh Giá CV
- **Backend**: `agent-cv-evaluator.py` (Port 8001)
- **Frontend**: `streamlit_cv_app.py` (Port 8502)
- **Chức năng**: Đánh giá độ phù hợp CV với tin tuyển dụng
- **Tính năng**:
  - Upload và đọc file PDF CV
  - Tiêu chí đánh giá configurable
  - Phân tích chi tiết theo trọng số
  - Gợi ý cải thiện CV

## Cài đặt

1. **Cài đặt dependencies:**
Chạy tại Window
1. mở folder chứa code
2. cài python > 3.11 (tải trên internet)
3. Cài venv (mt ảo cho project, giống nodejs)
chạy: python -m venv venv
4. chạy: .\venv\Scripts\activate
5. chạy: pip install -r requirements.txt


2. **Cấu hình API Key:**
   - Mở file `agent-poem.py`
   - Thêm API key của bạn vào dòng:
   ```python
   client = OpenAI(
       api_key="YOUR_API_KEY_HERE"  # Thay thế bằng API key thực
   )
   ```

## Chạy ứng dụng

### 🎭 Agent Thơ Lục Bát

**Bước 1: Khởi động Backend**
```bash
python agent-poem.py
```
Backend chạy tại: http://localhost:8000

**Bước 2: Khởi động Frontend**
```bash
streamlit run streamlit_app.py
```
Giao diện web tại: http://localhost:8501

### 📄 Agent Đánh Giá CV

**Bước 1: Khởi động Backend**
```bash
python agent-cv-evaluator.py
```
Backend chạy tại: http://localhost:8001

**Bước 2: Khởi động Frontend**
```bash
streamlit run streamlit_cv_app.py --server.port 8502
```
Giao diện web tại: http://localhost:8502

## Sử dụng

### 🎭 Agent Thơ Lục Bát
1. **Truy cập:** http://localhost:8501
2. **Chat với AI:** Nhập chủ đề thơ và nhấn Enter
3. **Xem thơ:** AI sẽ sáng tác thơ lục bát theo thời gian thực
4. **Quản lý:** Sử dụng nút "Xóa lịch sử chat" trong sidebar

### 📄 Agent Đánh Giá CV
1. **Truy cập:** http://localhost:8502
2. **Upload CV:** Chọn file PDF CV cần đánh giá
3. **Nhập JD:** Mô tả công việc tuyển dụng
4. **Cấu hình tiêu chí:** Điều chỉnh trọng số đánh giá (tổng = 1.0)
5. **Đánh giá:** Nhấn nút "ĐÁNH GIÁ CV"
6. **Xem kết quả:** Kết quả chi tiết với điểm số và gợi ý
7. **Tải xuống:** Download kết quả dưới dạng text file

## Tính năng

- ✅ Giao diện chat đẹp mắt
- ✅ Streaming response real-time
- ✅ Lưu lịch sử chat trong session
- ✅ Kiểm tra trạng thái kết nối
- ✅ Responsive design
- ✅ Typing indicator khi AI đang trả lời

## Khắc phục sự cố

### Lỗi kết nối FastAPI
- Đảm bảo FastAPI đang chạy trên port 8000
- Kiểm tra firewall không chặn port 8000
- Xem log trong terminal chạy FastAPI

### Lỗi API Key
- Kiểm tra API key đã được cấu hình đúng
- Đảm bảo API key còn hiệu lực và có đủ quota

### Lỗi Dependencies
```bash
pip install --upgrade -r requirements.txt
```

## API Endpoints

### 🎭 Agent Thơ (Port 8000)
- `POST /stream`: Endpoint streaming chat thơ
- `GET /docs`: FastAPI documentation

### 📄 Agent Đánh Giá CV (Port 8001)
- `POST /upload-cv`: Upload và trích xuất text từ PDF
- `POST /evaluate-cv`: Đánh giá CV với streaming response
- `GET /default-criteria`: Lấy tiêu chí đánh giá mặc định
- `POST /stream`: Endpoint chat tương thích
- `GET /docs`: FastAPI documentation

## Cấu hình nâng cao

### Cấu hình API Key cho Agent CV
Mở file `agent-cv-evaluator.py` và thay đổi:
```python
client = OpenAI(
    api_key="YOUR_API_KEY_HERE"  # Thay thế bằng API key thực
)
```

### Thay đổi port
- **Agent Thơ**: Sửa `port=8000` trong `agent-poem.py`
- **Agent CV**: Sửa `port=8001` trong `agent-cv-evaluator.py`
- **Frontend**: Sửa `FASTAPI_URL` trong các file streamlit

### Tùy chỉnh tiêu chí đánh giá
Sửa hàm `get_default_criteria()` trong `agent-cv-evaluator.py`:
```python
default_criteria = [
    {
        "name": "Tên tiêu chí",
        "weight": 0.xx,  # Trọng số (tổng = 1.0)
        "description": "Mô tả tiêu chí"
    }
]
```

### Tùy chỉnh giao diện
- **Agent Thơ**: Sửa `streamlit_app.py`
- **Agent CV**: Sửa `streamlit_cv_app.py`
- Thay đổi title, icon, layout trong `st.set_page_config()`
