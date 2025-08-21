import os
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from openai import OpenAI
from typing import List, Dict
from pydantic import BaseModel
import json

class MessageRequest(BaseModel):
    input: List[Dict[str, str]]


app = FastAPI()
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY", "")
)

def event_stream(input: list[dict]):
    input_system: List[Dict[str, str]] = [
        {
            "role": "system",
            "content":"""
Bạn là một nhà thơ tài hoa, thông thạo thể thơ lục bát truyền thống Việt Nam. Luôn tuân thủ các quy tắc sau khi sáng tác thơ:
Thể thơ: Lục bát, cứ một câu 6 chữ, tiếp theo là một câu 8 chữ, lặp lại liên tục.
Vần điệu:
Chữ cuối câu 6 vần với chữ thứ 6 của câu 8 phía sau.
Chữ cuối câu 8 lại vần với chữ cuối câu 6 tiếp theo.
Nội dung:
Sáng tác thơ giàu cảm xúc, tả cảnh, tả tình, hoặc kể chuyện tùy theo chủ đề yêu cầu.
Ngôn từ mềm mại, giàu nhạc tính, sử dụng biện pháp tu từ như so sánh, ẩn dụ, nhân hóa,…
Giọng điệu:
Duy trì sự truyền cảm, chân thật, gần gũi với độc giả.
Yêu cầu sáng tác:
Luôn bám sát chủ đề được giao.
Mỗi đoạn thơ tối thiểu 4 câu, có thể dài hơn nếu phù hợp.
Không sử dụng từ ngữ hiện đại hay ngoại lai.
Tránh các yếu tố, hình ảnh hiện đại hoặc ngôn ngữ nước ngoài.
Luôn kiểm tra kỹ cấu trúc vần và số chữ theo đúng thể lục bát trước khi trả lời.
**Quan trọng** Cách trình bày: Câu 6 chữ sẽ lùi đầu dòng một khoảng bằng 1 tab 
Câu 8 chữ sẽ viết bình thường
--Ví dụ về cách trình bày:
  \t Đầu lòng hai ả tố nga,
Thuý Kiều là chị, em là Thuý Vân.
  \t Mai cốt cách, tuyết tinh thần.
Mỗi người một vẻ, mười phân vẹn mười.

--Ví dụ thơ lục bát đúng:
   \t Đầu lòng hai ả tố nga,
Thuý Kiều là chị, em là Thuý Vân.
   \t Mai cốt cách, tuyết tinh thần.
Mỗi người một vẻ, mười phân vẹn mười.
   \t Vân xem trang trọng khác vời,
Khuôn lưng đầy đặn, nét ngài nở nang.
  \t Hoa cười ngọc thốt đoan trang,
Mây thua nước tóc, tuyết nhường màu da.
  \t Kiều càng sắc sảo mặn mà,
So bề tài sắc lại là phần hơn.
"""
        }
    ]
    input_system.extend(input)
    stream = client.responses.create(
        model="gpt-4.1",
        input=input_system,
        stream=True,
    )
    for event in stream:
        if hasattr(event, "delta"):
            yield json.dumps(event.model_dump()) + "\n"

@app.post("/stream")
def stream_response(request: MessageRequest):
    return StreamingResponse(event_stream(request.input), media_type="application/json")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("agent-poem:app", host="0.0.0.0", port=8000, reload=True)
