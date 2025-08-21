import streamlit as st
import requests
import json
from typing import Generator

# Cấu hình trang
st.set_page_config(
    page_title="AI Chat Assistant",
    page_icon="🤖",
    layout="wide"
)

# URL của FastAPI backend
FASTAPI_URL = "http://localhost:8000"

def stream_chat_response(messages: list) -> Generator[str, None, None]:
    """
    Gửi request đến FastAPI và nhận streaming response
    """
    try:
        payload = {"input": messages}
        
        with requests.post(
            f"{FASTAPI_URL}/stream",
            json=payload,
            stream=True,
            headers={"Content-Type": "application/json"}
        ) as response:
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    try:
                        # Parse JSON response từ FastAPI
                        data = json.loads(line.decode('utf-8'))
                        # Trích xuất nội dung từ response
                        if isinstance(data, dict) and 'delta' in data:
                            # delta là string, không phải object
                            content = data.get('delta', '')
                            if content:
                                yield content
                        elif isinstance(data, str):
                            yield data
                    except json.JSONDecodeError:
                        # Nếu không parse được JSON, yield raw text
                        yield line.decode('utf-8')
                        
    except requests.exceptions.RequestException as e:
        yield f"❌ Lỗi kết nối: {str(e)}"
    except Exception as e:
        yield f"❌ Lỗi: {str(e)}"

def main():
    st.title("🤖 AI Chat Assistant")
    st.markdown("---")
    
    # Khởi tạo session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Sidebar với các tùy chọn
    with st.sidebar:
        st.header("⚙️ Cài đặt")
        
        # Button để xóa lịch sử chat
        if st.button("🗑️ Xóa lịch sử chat", type="secondary"):
            st.session_state.messages = []
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 📝 Hướng dẫn")
        st.markdown("""
        1. Nhập tin nhắn vào ô chat bên dưới
        2. Nhấn Enter hoặc click Send
        3. AI sẽ trả lời theo thời gian thực
        4. Sử dụng nút "Xóa lịch sử" để bắt đầu cuộc trò chuyện mới
        """)
        
        # Hiển thị trạng thái kết nối
        st.markdown("---")
        st.markdown("### 🔗 Trạng thái")
        try:
            response = requests.get(f"{FASTAPI_URL}/docs", timeout=2)
            if response.status_code == 200:
                st.success("✅ Kết nối FastAPI thành công")
            else:
                st.error("❌ FastAPI không phản hồi")
        except:
            st.error("❌ Không thể kết nối FastAPI")
            st.info("Đảm bảo FastAPI đang chạy trên localhost:8000")
    
    # Hiển thị lịch sử chat
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Input cho tin nhắn mới
    if prompt := st.chat_input("Nhập tin nhắn của bạn..."):
        # Thêm tin nhắn của user vào lịch sử
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Hiển thị tin nhắn của user
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Chuẩn bị messages để gửi đến API
        api_messages = [
            {"role": msg["role"], "content": msg["content"]} 
            for msg in st.session_state.messages
        ]
        
        # Hiển thị response của AI với streaming
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            # Hiển thị typing indicator
            with st.spinner("AI đang suy nghĩ..."):
                try:
                    # Stream response từ FastAPI
                    for chunk in stream_chat_response(api_messages):
                        full_response += chunk
                        message_placeholder.markdown(full_response + "▌")
                    
                    # Hiển thị response hoàn chỉnh
                    message_placeholder.markdown(full_response)
                    
                except Exception as e:
                    error_msg = f"❌ Lỗi: {str(e)}"
                    message_placeholder.markdown(error_msg)
                    full_response = error_msg
        
        # Thêm response của AI vào lịch sử
        st.session_state.messages.append({"role": "assistant", "content": full_response})

if __name__ == "__main__":
    main()
