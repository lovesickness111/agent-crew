import streamlit as st
import requests
import json
from typing import Generator, List, Dict
import io

# Cấu hình trang
st.set_page_config(
    page_title="CV Evaluator - Đánh giá CV",
    page_icon="📄",
    layout="wide"
)

# URL của FastAPI backend
FASTAPI_URL = "http://localhost:8001"

def get_default_criteria() -> List[Dict]:
    """
    Lấy tiêu chí đánh giá mặc định từ API
    """
    try:
        response = requests.get(f"{FASTAPI_URL}/default-criteria")
        if response.status_code == 200:
            return response.json()["default_criteria"]
    except:
        pass
    
    # Fallback nếu API không hoạt động
    return [
        {
            "name": "Kỹ năng kỹ thuật",
            "weight": 0.30,
            "description": "Đánh giá các kỹ năng kỹ thuật, ngôn ngữ lập trình, framework, công cụ liên quan đến công việc"
        },
        {
            "name": "Kinh nghiệm làm việc",
            "weight": 0.25,
            "description": "Đánh giá số năm kinh nghiệm, các dự án đã thực hiện, vị trí công việc trước đây"
        },
        {
            "name": "Trình độ học vấn",
            "weight": 0.20,
            "description": "Đánh giá bằng cấp, chuyên ngành học, thành tích học tập, các khóa học bổ sung"
        },
        {
            "name": "Kỹ năng mềm",
            "weight": 0.15,
            "description": "Đánh giá khả năng giao tiếp, làm việc nhóm, lãnh đạo, giải quyết vấn đề"
        },
        {
            "name": "Yếu tố khác",
            "weight": 0.10,
            "description": "Đánh giá ngoại ngữ, chứng chỉ, hoạt động xã hội, sở thích phù hợp với công việc"
        }
    ]

def upload_cv(file) -> str:
    """
    Upload CV và trích xuất text
    """
    try:
        files = {"file": (file.name, file.getvalue(), "application/pdf")}
        response = requests.post(f"{FASTAPI_URL}/upload-cv", files=files)
        
        if response.status_code == 200:
            return response.json()["cv_text"]
        else:
            st.error(f"Lỗi upload CV: {response.json().get('detail', 'Unknown error')}")
            return ""
    except Exception as e:
        st.error(f"Lỗi kết nối: {str(e)}")
        return ""

def stream_evaluation(cv_text: str, job_description: str, criteria: List[Dict]) -> Generator[str, None, None]:
    """
    Stream đánh giá CV từ API
    """
    try:
        payload = {
            "cv_text": cv_text,
            "job_description": job_description,
            "criteria": criteria
        }
        
        with requests.post(
            f"{FASTAPI_URL}/evaluate-cv",
            json=payload,
            stream=True,
            headers={"Content-Type": "application/json"}
        ) as response:
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode('utf-8'))
                        if isinstance(data, dict) and 'delta' in data:
                            content = data.get('delta', '')
                            if content:
                                yield content
                    except json.JSONDecodeError:
                        yield line.decode('utf-8')
                        
    except requests.exceptions.RequestException as e:
        yield f"❌ Lỗi kết nối: {str(e)}"
    except Exception as e:
        yield f"❌ Lỗi: {str(e)}"

def main():
    st.title("📄 CV Evaluator - Đánh giá CV")
    st.markdown("---")
    
    # Khởi tạo session state
    if "cv_text" not in st.session_state:
        st.session_state.cv_text = ""
    if "evaluation_result" not in st.session_state:
        st.session_state.evaluation_result = ""
    if "criteria" not in st.session_state:
        st.session_state.criteria = get_default_criteria()
    
    # Sidebar với cài đặt
    with st.sidebar:
        st.header("⚙️ Cài đặt")
        
        # Trạng thái kết nối
        st.markdown("### 🔗 Trạng thái")
        try:
            response = requests.get(f"{FASTAPI_URL}/docs", timeout=2)
            if response.status_code == 200:
                st.success("✅ Kết nối FastAPI thành công")
            else:
                st.error("❌ FastAPI không phản hồi")
        except:
            st.error("❌ Không thể kết nối FastAPI")
            st.info("Đảm bảo FastAPI đang chạy trên localhost:8001")
        
        st.markdown("---")
        
        # Reset button
        if st.button("🔄 Reset tất cả", type="secondary"):
            st.session_state.cv_text = ""
            st.session_state.evaluation_result = ""
            st.session_state.criteria = get_default_criteria()
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 📝 Hướng dẫn")
        st.markdown("""
        1. **Upload CV**: Chọn file PDF CV cần đánh giá
        2. **Nhập JD**: Mô tả công việc tuyển dụng
        3. **Cấu hình tiêu chí**: Điều chỉnh trọng số đánh giá
        4. **Đánh giá**: Nhấn nút để bắt đầu đánh giá
        5. **Xem kết quả**: Kết quả sẽ hiển thị theo thời gian thực
        """)
    
    # Layout chính với 2 cột
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📤 Upload CV")
        
        # Upload file CV
        uploaded_file = st.file_uploader(
            "Chọn file CV (PDF)",
            type=['pdf'],
            help="Chỉ chấp nhận file PDF"
        )
        
        if uploaded_file is not None:
            if st.button("📄 Trích xuất text từ CV", type="primary"):
                with st.spinner("Đang xử lý CV..."):
                    cv_text = upload_cv(uploaded_file)
                    if cv_text:
                        st.session_state.cv_text = cv_text
                        st.success("✅ Trích xuất CV thành công!")
        
        # Hiển thị nội dung CV đã trích xuất
        if st.session_state.cv_text:
            st.subheader("📋 Nội dung CV")
            with st.expander("Xem nội dung CV", expanded=False):
                st.text_area(
                    "CV Text",
                    value=st.session_state.cv_text,
                    height=200,
                    disabled=True,
                    label_visibility="collapsed"
                )
        
        st.markdown("---")
        
        # Job Description
        st.header("💼 Mô tả công việc (JD)")
        job_description = st.text_area(
            "Nhập mô tả công việc tuyển dụng",
            height=200,
            placeholder="Ví dụ: Tuyển dụng lập trình viên Python với 2+ năm kinh nghiệm, thành thạo Django/Flask, có kinh nghiệm với database PostgreSQL..."
        )
    
    with col2:
        st.header("⚖️ Tiêu chí đánh giá")
        
        # Cấu hình tiêu chí
        st.markdown("**Điều chỉnh trọng số cho từng tiêu chí:**")
        
        criteria_config = []
        total_weight = 0
        
        for i, criterion in enumerate(st.session_state.criteria):
            with st.container():
                st.markdown(f"**{criterion['name']}**")
                
                # Slider cho trọng số
                weight = st.slider(
                    f"Trọng số",
                    min_value=0.0,
                    max_value=1.0,
                    value=criterion['weight'],
                    step=0.05,
                    key=f"weight_{i}",
                    label_visibility="collapsed"
                )
                
                # Mô tả tiêu chí
                description = st.text_input(
                    f"Mô tả",
                    value=criterion['description'],
                    key=f"desc_{i}",
                    label_visibility="collapsed"
                )
                
                criteria_config.append({
                    "name": criterion['name'],
                    "weight": weight,
                    "description": description
                })
                
                total_weight += weight
                st.markdown("---")
        
        # Hiển thị tổng trọng số
        if abs(total_weight - 1.0) > 0.01:
            st.error(f"⚠️ Tổng trọng số: {total_weight:.2f} (phải bằng 1.0)")
        else:
            st.success(f"✅ Tổng trọng số: {total_weight:.2f}")
        
        # Button reset tiêu chí
        if st.button("🔄 Reset tiêu chí về mặc định"):
            st.session_state.criteria = get_default_criteria()
            st.rerun()
    
    st.markdown("---")
    
    # Nút đánh giá
    col_eval1, col_eval2, col_eval3 = st.columns([1, 2, 1])
    
    with col_eval2:
        if st.button("🎯 ĐÁNH GIÁ CV", type="primary", use_container_width=True):
            # Kiểm tra điều kiện
            if not st.session_state.cv_text:
                st.error("❌ Vui lòng upload và trích xuất CV trước!")
            elif not job_description.strip():
                st.error("❌ Vui lòng nhập mô tả công việc!")
            elif abs(total_weight - 1.0) > 0.01:
                st.error("❌ Tổng trọng số phải bằng 1.0!")
            else:
                # Thực hiện đánh giá
                st.markdown("### 📊 Kết quả đánh giá")
                
                result_placeholder = st.empty()
                full_result = ""
                
                with st.spinner("AI đang đánh giá CV..."):
                    try:
                        for chunk in stream_evaluation(
                            st.session_state.cv_text,
                            job_description,
                            criteria_config
                        ):
                            full_result += chunk
                            result_placeholder.markdown(full_result + "▌")
                        
                        # Hiển thị kết quả hoàn chỉnh
                        result_placeholder.markdown(full_result)
                        st.session_state.evaluation_result = full_result
                        
                    except Exception as e:
                        st.error(f"❌ Lỗi đánh giá: {str(e)}")
    
    # Hiển thị kết quả đã lưu (nếu có)
    if st.session_state.evaluation_result and not st.button:
        st.markdown("### 📊 Kết quả đánh giá gần nhất")
        st.markdown(st.session_state.evaluation_result)
        
        # Button để download kết quả
        if st.download_button(
            label="💾 Tải xuống kết quả",
            data=st.session_state.evaluation_result,
            file_name="cv_evaluation_result.txt",
            mime="text/plain"
        ):
            st.success("✅ Đã tải xuống kết quả!")

if __name__ == "__main__":
    main()
