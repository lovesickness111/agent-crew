import streamlit as st
import requests
import json
import io

# Cấu hình trang
st.set_page_config(
    page_title="AI Presentation Generator",
    page_icon="📊",
    layout="wide"
)

# URL của FastAPI backend
FASTAPI_URL = "http://localhost:8002"

def main():
    st.title("📊 AI Presentation Generator")
    st.markdown("Nhập chủ đề và tải lên tài liệu (tùy chọn) để tạo dàn ý cho bài trình bày của bạn.")

    # Khởi tạo session state
    if "outline" not in st.session_state:
        st.session_state.outline = None
    if "pptx_file" not in st.session_state:
        st.session_state.pptx_file = None

    with st.sidebar:
        st.header("⚙️ Tùy chọn")
        topic = st.text_input("Chủ đề bài trình bày:", placeholder="VD: Lịch sử trí tuệ nhân tạo")
        uploaded_file = st.file_uploader("Tải lên tài liệu PDF (tùy chọn)", type="pdf")

        if st.button("📝 Tạo dàn ý", type="primary", disabled=not topic):
            with st.spinner("Đang phân tích và tìm kiếm thông tin để tạo dàn ý..."):
                files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)} if uploaded_file else None
                data = {'topic': topic}
                
                try:
                    response = requests.post(f"{FASTAPI_URL}/generate-outline", data=data, files=files)
                    response.raise_for_status()
                    outline_data = response.json()
                    # The actual outline can be a list or a dict with a 'slides' or 'outline' key
                    if isinstance(outline_data, dict) and "slides" in outline_data:
                        st.session_state.outline = outline_data["slides"]
                    elif isinstance(outline_data, dict) and "outline" in outline_data:
                        st.session_state.outline = outline_data["outline"]
                    else: # If the root is the list
                        st.session_state.outline = outline_data
                    st.session_state.pptx_file = None # Reset pptx file
                    st.success("Tạo dàn ý thành công!")
                except requests.exceptions.RequestException as e:
                    st.error(f"Lỗi kết nối: {e}")
                except json.JSONDecodeError:
                    st.error("Lỗi: Không thể phân tích phản hồi từ server. Phản hồi không phải là JSON hợp lệ.")
                    st.error(f"Nội dung phản hồi: {response.text}")
                except Exception as e:
                    st.error(f"Đã xảy ra lỗi không mong muốn: {e}")

    st.markdown("---")

    if st.session_state.outline:
        st.subheader("Dàn ý đề xuất (có thể chỉnh sửa)")
        
        # Allow editing the outline
        for i, slide in enumerate(st.session_state.outline):
            with st.expander(f"Slide {i+1}: {slide.get('title', '')}", expanded=True):
                slide['title'] = st.text_input("Tiêu đề Slide", value=slide.get('title', ''), key=f"title_{i}")
                slide['points'] = st.text_area("Nội dung (mỗi dòng một gạch đầu dòng)", 
                                               value="\n".join(slide.get('points', [])), 
                                               key=f"points_{i}").split("\n")
                slide['image_suggestion'] = st.text_input("Gợi ý hình ảnh", value=slide.get('image_suggestion', ''), key=f"img_{i}")

        if st.button("🚀 Tạo bài trình bày", type="primary"):
            with st.spinner("Đang tạo file PowerPoint... Quá trình này có thể mất vài phút."):
                try:
                    payload = {"outline": st.session_state.outline}
                    response = requests.post(f"{FASTAPI_URL}/generate-presentation", json=payload)
                    response.raise_for_status()
                    
                    # Save the pptx file to session state
                    st.session_state.pptx_file = io.BytesIO(response.content)
                    st.success("Tạo bài trình bày thành công!")

                except requests.exceptions.RequestException as e:
                    st.error(f"Lỗi kết nối khi tạo bài trình bày: {e}")
                except Exception as e:
                    st.error(f"Đã xảy ra lỗi không mong muốn khi tạo bài trình bày: {e}")

    if st.session_state.pptx_file:
        st.markdown("---")
        st.subheader("Tải xuống bài trình bày của bạn")
        st.download_button(
            label="📥 Tải xuống file .pptx",
            data=st.session_state.pptx_file,
            file_name="presentation.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
        )

if __name__ == "__main__":
    main()
