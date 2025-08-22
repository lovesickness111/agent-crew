from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import StreamingResponse
from openai import OpenAI
from typing import List, Dict, Optional
from pydantic import BaseModel
import json
import PyPDF2
import io
import os
class EvaluationCriteria(BaseModel):
    name: str
    weight: float
    description: str

class CVEvaluationRequest(BaseModel):
    job_description: str
    criteria: List[EvaluationCriteria]
    cv_text: Optional[str] = None

class MessageRequest(BaseModel):
    input: List[Dict[str, str]]

app = FastAPI()
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY", "")
)

def extract_text_from_pdf(pdf_file: bytes) -> str:
    """
    Trích xuất text từ file PDF
    """
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Lỗi đọc file PDF: {str(e)}")

def create_evaluation_prompt(cv_text: str, job_description: str, criteria: List[EvaluationCriteria]) -> str:
    """
    Tạo prompt đánh giá CV với tiêu chí configurable
    """
    criteria_text = ""
    for criterion in criteria:
        criteria_text += f"- {criterion.name} ({criterion.weight*100}%): {criterion.description}\n"
    
    prompt = f"""
Bạn là một chuyên gia tuyển dụng và đánh giá CV chuyên nghiệp. Nhiệm vụ của bạn là đánh giá độ phù hợp của CV với tin tuyển dụng dựa trên các tiêu chí được cung cấp.

**THÔNG TIN TUYỂN DỤNG:**
{job_description}

**TIÊU CHÍ ĐÁNH GIÁ:**
{criteria_text}

**NỘI DUNG CV:**
{cv_text}

**YÊU CẦU ĐÁNH GIÁ:**

1. **Phân tích từng tiêu chí:**
   - Đánh giá mức độ phù hợp của CV với từng tiêu chí (thang điểm 0-10)
   - Giải thích cụ thể tại sao đạt điểm đó
   - Chỉ ra điểm mạnh và điểm yếu

2. **Tính điểm tổng hợp:**
   - Áp dụng trọng số cho từng tiêu chí
   - Tính điểm tổng (thang điểm 0-10)
   - Phân loại: Xuất sắc (8.5-10), Tốt (7-8.4), Khá (5.5-6.9), Trung bình (4-5.4), Yếu (<4)

3. **Đưa ra nhận xét chi tiết:**
   - Điểm nổi bật của ứng viên
   - Những thiếu sót cần cải thiện
   - Mức độ phù hợp với vị trí tuyển dụng

4. **Gợi ý cải thiện:**
   - Những kỹ năng cần bổ sung
   - Cách trình bày CV tốt hơn
   - Kinh nghiệm cần tích lũy thêm

**ĐỊNH DẠNG TRÌNH BÀY:**
```
🎯 ĐÁNH GIÁ CV - [TÊN ỨNG VIÊN]

📊 ĐIỂM SỐ CHI TIẾT:
[Từng tiêu chí với điểm số và giải thích]

🏆 ĐIỂM TỔNG HỢP: [X.X]/10 - [Phân loại]

💪 ĐIỂM MẠNH:
[Liệt kê các điểm mạnh]

⚠️ ĐIỂM CẦN CẢI THIỆN:
[Liệt kê các điểm yếu]

🎯 MỨC ĐỘ PHÙ HỢP: [Phù hợp/Không phù hợp] với vị trí tuyển dụng

💡 GỢI Ý CẢI THIỆN:
[Các gợi ý cụ thể]
```

Hãy đánh giá một cách khách quan, công bằng và chi tiết.
"""
    return prompt

def event_stream(cv_text: str, job_description: str, criteria: List[EvaluationCriteria]):
    """
    Stream đánh giá CV
    """
    system_prompt = create_evaluation_prompt(cv_text, job_description, criteria)
    
    input_messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user", 
            "content": "Hãy đánh giá CV này theo các tiêu chí đã được cung cấp. Kết quả trả về chi cần Phần điểm và Kết luận, không cần giải thích thêm"
        }
    ]
    
    stream = client.chat.completions.create(
        model="gpt-4.1",
        messages=input_messages,
        stream=True,
    )
    
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            yield json.dumps({"delta": chunk.choices[0].delta.content}) + "\n"

@app.post("/upload-cv")
async def upload_cv(file: UploadFile = File(...)):
    """
    Upload và trích xuất text từ file CV PDF
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Chỉ chấp nhận file PDF")
    
    try:
        pdf_content = await file.read()
        cv_text = extract_text_from_pdf(pdf_content)
        
        if not cv_text.strip():
            raise HTTPException(status_code=400, detail="Không thể trích xuất text từ file PDF")
        
        return {
            "filename": file.filename,
            "cv_text": cv_text,
            "message": "Upload CV thành công"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý file: {str(e)}")

@app.post("/evaluate-cv")
def evaluate_cv(request: CVEvaluationRequest):
    """
    Đánh giá CV với streaming response
    """
    if not request.cv_text:
        raise HTTPException(status_code=400, detail="Thiếu nội dung CV")
    
    if not request.job_description:
        raise HTTPException(status_code=400, detail="Thiếu mô tả công việc")
    
    if not request.criteria:
        raise HTTPException(status_code=400, detail="Thiếu tiêu chí đánh giá")
    
    # Kiểm tra tổng trọng số = 1.0
    total_weight = sum(criterion.weight for criterion in request.criteria)
    if abs(total_weight - 1.0) > 0.01:
        raise HTTPException(status_code=400, detail=f"Tổng trọng số phải bằng 1.0, hiện tại: {total_weight}")
    
    return StreamingResponse(
        event_stream(request.cv_text, request.job_description, request.criteria),
        media_type="application/json"
    )

@app.get("/default-criteria")
def get_default_criteria():
    """
    Trả về tiêu chí đánh giá mặc định
    """
    default_criteria = [
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
    return {"default_criteria": default_criteria}

# Endpoint tương thích với agent-poem (để test)
@app.post("/stream")
def stream_response(request: MessageRequest):
    """
    Endpoint tương thích với agent-poem để test
    """
    def stream_generator():
        input_system = [
            {
                "role": "system",
                "content": "Bạn là một chuyên gia tuyển dụng và đánh giá CV. Hãy trả lời các câu hỏi liên quan đến tuyển dụng và đánh giá ứng viên một cách chuyên nghiệp. Kết quả trả ra chỉ cần phần Kế Luận, Đánh giá mức độ phù hợp"
            }
        ]
        input_system.extend(request.input)
        
        stream = client.chat.completions.create(
            model="gpt-4.1",
            messages=input_system,
            stream=True,
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield json.dumps({"delta": chunk.choices[0].delta.content}) + "\n"
    
    return StreamingResponse(stream_generator(), media_type="application/json")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("agent-cv-evaluator:app", host="0.0.0.0", port=8001, reload=True)
