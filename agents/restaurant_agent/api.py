import os
import uuid
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import List
import shutil
from dotenv import load_dotenv

# Tải biến môi trường từ .env
load_dotenv()

# Sử dụng import tuyệt đối từ gốc dự án
from agents.restaurant_agent.restaurant_agent import agent_executor

# Tạo thư mục để lưu trữ tệp tải lên tạm thời
UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(
    title="Restaurant Agent API",
    description="API để tương tác với agent quản lý nhà hàng.",
)

class ApiResponse(BaseModel):
    response: str
    thread_id: str

@app.post("/invoke", response_model=ApiResponse)
async def invoke_agent(
    prompt: str = Form(...),
    thread_id: str = Form(...),
    file: UploadFile = File(None)
):
    """
    Gọi agent với một lời nhắc của người dùng và một tệp ảnh tùy chọn.
    """
    image_path = None
    try:
        user_input = prompt
        if file:
            # Lưu tệp tải lên tạm thời
            file_extension = os.path.splitext(file.filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            image_path = os.path.join(UPLOAD_DIR, unique_filename)
            
            with open(image_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Nối đường dẫn ảnh vào lời nhắc cho agent
            user_input = f"{prompt} (Ảnh đính kèm tại: {image_path})"

        # Cấu hình cho cuộc trò chuyện
        config = {"configurable": {"thread_id": thread_id}}
        
        # Định dạng đầu vào cho agent
        input_message = {"messages": [("user", user_input)]}

        # Gọi agent
        response = agent_executor.invoke(input_message, config)
        
        # Trích xuất nội dung tin nhắn cuối cùng
        last_message = response["messages"][-1]
        agent_response = last_message.content if last_message.content else ""

        return {"response": agent_response, "thread_id": thread_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Dọn dẹp tệp tạm
        if image_path and os.path.exists(image_path):
            os.remove(image_path)

if __name__ == "__main__":
    import uvicorn
    # Chạy FastAPI server
    # Lệnh để chạy: uvicorn agents.restaurant_agent.api:app --reload
    uvicorn.run(app, host="0.0.0.0", port=8000)
