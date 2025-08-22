import base64
import os
import mimetypes
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

# Tải các biến môi trường từ tệp .env
load_dotenv()

# Khởi tạo mô hình Gemini
# Hãy chắc chắn rằng bạn đã đặt biến môi trường GOOGLE_API_KEY
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", api_key=os.environ["GOOGLE_API_KEY"])

def image_to_base64(image_path: str) -> str:
    """Chuyển đổi file ảnh sang định dạng base64."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

@tool
def extract_food_info_from_image(image_path: str) -> str:
    """
    Phân tích hình ảnh món ăn và trích xuất thông tin như tên, mô tả và giá cả ước tính.
    Sử dụng mô hình Gemini 1.5 Flash để nhận dạng món ăn từ ảnh.
    Args:
        image_path: Đường dẫn đến file ảnh món ăn.
    """
    if not os.path.exists(image_path):
        return f"Lỗi: Không tìm thấy file ảnh tại đường dẫn: {image_path}"

    # Chuyển ảnh sang base64
    base64_image = image_to_base64(image_path)

    # Xác định mime type từ đường dẫn file
    mime_type, _ = mimetypes.guess_type(image_path)
    if mime_type is None:
        # Mặc định là jpeg nếu không xác định được
        mime_type = "image/jpeg"

    # Tạo message để gửi đến mô hình
    message = HumanMessage(
        content=[
            {
                "type": "text",
                "text": (
                    "Bạn là một chuyên gia ẩm thực. Hãy phân tích hình ảnh này và cung cấp thông tin về các món ăn. "
                    "Trả lời dưới dạng một array đối tượng JSON với các khóa sau: 'name' (tên món ăn), "
                    "'description' (mô tả ngắn gọn, hấp dẫn về món ăn), và 'price' (giá bán lẻ ước tính bằng VND). "
                    "Ví dụ: [{\"name\": \"Phở Bò Tái\", \"description\": \"Sự hòa quyện của nước dùng đậm đà, bánh phở mềm và thịt bò thái mỏng.\", \"price\": 50000}]"
                ),
            },
            {
                "type": "image_url",
                "image_url": f"data:{mime_type};base64,{base64_image}"
            },
        ]
    )

    try:
        # Gọi mô hình và nhận kết quả
        response = llm.invoke([message])
        # Trích xuất nội dung JSON từ phản hồi
        # Thường thì mô hình sẽ trả về nội dung trong cặp ```json ... ```
        json_response = response.content.strip().replace("```json", "").replace("```", "").strip()
        return json_response
    except Exception as e:
        return f"Đã xảy ra lỗi khi gọi Gemini API: {e}"
