import streamlit as st
import requests
import uuid
import os

# Cấu hình trang
st.set_page_config(
    page_title="Trợ lý Nhà hàng AI",
    page_icon="👨‍🍳",
    layout="wide"
)

# URL của FastAPI backend
FASTAPI_URL = "http://localhost:8000/invoke"

# --- Hàm tương tác với API ---
def call_agent_api(prompt: str, thread_id: str, uploaded_file):
    """
    Gửi yêu cầu đến FastAPI backend với prompt và file đính kèm.
    """
    files = {}
    if uploaded_file is not None:
        files['file'] = (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)

    data = {
        'prompt': prompt,
        'thread_id': thread_id
    }

    try:
        response = requests.post(FASTAPI_URL, data=data, files=files)
        response.raise_for_status()  # Ném lỗi nếu status code là 4xx hoặc 5xx
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Lỗi kết nối đến API: {e}")
        return None
    except Exception as e:
        st.error(f"Đã xảy ra lỗi không mong muốn: {e}")
        return None

# --- Giao diện chính ---
def main():
    st.title("👨‍🍳 Trợ lý Quản lý Thực đơn Nhà hàng AI")
    st.markdown("Chào mừng! Tôi có thể giúp bạn quản lý thực đơn, phân tích món ăn từ hình ảnh và hơn thế nữa.")

    # Khởi tạo session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = f"streamlit-thread-{uuid.uuid4()}"
    # Dùng key để có thể reset file uploader
    if "uploader_key" not in st.session_state:
        st.session_state.uploader_key = 0

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Tùy chọn")
        if st.button("🗑️ Bắt đầu cuộc trò chuyện mới"):
            # Xóa các session state liên quan để bắt đầu lại
            keys_to_clear = ["messages", "thread_id", "uploader_key"]
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

        st.markdown("---")
        st.markdown("### 💡 Gợi ý:")
        st.info(
            """
            - **Xem thực đơn:** "Cho tôi xem thực đơn hiện tại."
            - **Thêm món:** "Thêm món 'Bún Chả Hà Nội' với giá 60000 VND."
            - **Phân tích ảnh:** Đính kèm ảnh và nhập "Món này là gì? Thêm vào thực đơn giúp tôi."
            - **Tạo ảnh:** "Tạo cho tôi một hình ảnh về món phở bò."
            """
        )

    # Hiển thị lịch sử trò chuyện
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            # Hiển thị ảnh nếu có trong lịch sử
            if "image_bytes" in message:
                st.image(message["image_bytes"], width=200)

    # Container cho ô nhập liệu và tải file
    # Streamlit không cho phép đặt file_uploader "bên trong" chat_input.
    # Đây là cách bố trí phổ biến và tốt nhất có thể.
    # Tôi đã cải thiện logic để file tải lên sẽ được xóa sau khi gửi.
    with st.container():
        uploaded_file = st.file_uploader(
            "Đính kèm ảnh món ăn (tùy chọn)",
            type=["jpg", "jpeg", "png"],
            key=f"uploader_{st.session_state.uploader_key}"
        )
        prompt = st.chat_input("Bạn cần tôi giúp gì?")

    if prompt:
        # Tạo message của người dùng để lưu vào lịch sử
        user_message = {"role": "user", "content": prompt}
        
        if uploaded_file:
            # Lưu bytes của ảnh để hiển thị lại trong lịch sử
            image_bytes = uploaded_file.getvalue()
            user_message["image_bytes"] = image_bytes

        st.session_state.messages.append(user_message)

        # Hiển thị tin nhắn của người dùng ngay lập tức
        with st.chat_message("user"):
            st.markdown(prompt)
            if uploaded_file:
                st.image(uploaded_file, width=200)

        # Gọi API và hiển thị phản hồi của agent
        with st.chat_message("assistant"):
            with st.spinner("Agent đang xử lý..."):
                api_response = call_agent_api(prompt, st.session_state.thread_id, uploaded_file)

                if api_response and "response" in api_response:
                    response_text = api_response["response"]
                    st.markdown(response_text)
                    # Thêm phản hồi của agent vào lịch sử
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                else:
                    st.error("Không nhận được phản hồi hợp lệ từ agent.")

        # Reset file uploader bằng cách thay đổi key và chạy lại app
        if uploaded_file is not None:
            st.session_state.uploader_key += 1
        
        # Chạy lại ứng dụng để cập nhật giao diện (ví dụ: xóa file đã tải lên)
        st.rerun()


if __name__ == "__main__":
    main()
