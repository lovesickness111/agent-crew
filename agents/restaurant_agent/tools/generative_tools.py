import base64
import os
import time
from langchain_core.tools import tool
from google import genai
from google.genai import types
from langchain_core.messages import AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
# Tải các biến môi trường từ tệp .env
from dotenv import load_dotenv
load_dotenv()
def _get_image_base64(response: AIMessage) -> str | None:
    """Trích xuất hình ảnh được mã hóa base64 từ AIMessage."""
    if not isinstance(response.content, list):
        return None
        
    image_block = next(
        (
            block
            for block in response.content
            if isinstance(block, dict) and block.get("image_url")
        ),
        None,
    )
    if image_block:
        # URL có định dạng 'data:image/png;base64,<dữ_liệu_base64>'
        return image_block["image_url"].get("url").split(",")[-1]
    return None

@tool
def generate_image(food_name: str, description: str) -> str:
    """
    Tạo một hình ảnh quảng cáo cho món ăn bằng Gemini, lưu vào file và trả về đường dẫn.
    Args:
        food_name: Tên món ăn để tạo ảnh.
        description: Mô tả để làm nguồn cảm hứng cho ảnh.
    """
    print(f"**Đang tạo ảnh cho: {food_name} với mô tả: {description}**")

    llm = ChatGoogleGenerativeAI(model="models/gemini-2.0-flash-preview-image-generation", api_key=os.environ["GEMINI_API_KEY"])

    prompt = f"Generate a photorealistic promotional image for a dish named '{food_name}'. The description is: '{description}'"
    message = {"role": "user", "content": prompt}

    try:
        response = llm.invoke(
            [message],
            generation_config=dict(response_modalities=["TEXT", "IMAGE"]),
        )

        image_base64 = _get_image_base64(response)

        if not image_base64:
            return "Không thể tạo ảnh. Không tìm thấy dữ liệu ảnh trong phản hồi."

        # Giải mã chuỗi base64
        image_data = base64.b64decode(image_base64)

        # Tạo thư mục nếu chưa tồn tại
        output_dir = "temp_uploads"
        os.makedirs(output_dir, exist_ok=True)

        # Tạo tên tệp duy nhất
        timestamp = int(time.time())
        safe_food_name = "".join(c for c in food_name if c.isalnum() or c in (' ', '_')).rstrip()
        file_name = f"image_{safe_food_name.replace(' ', '_')}_{timestamp}.png"
        output_path = os.path.join(output_dir, file_name)

        # Lưu tệp hình ảnh
        with open(output_path, 'wb') as f:
            f.write(image_data)

        print(f"**Ảnh cho '{food_name}' đã được tạo và lưu tại: {output_path}**")
        # Trả về chuỗi định dạng đặc biệt
        return f"image_path:{output_path}"

    except Exception as e:
        error_message = f"Đã xảy ra lỗi khi tạo ảnh cho '{food_name}': {e}"
        print(f"**{error_message}**")
        return error_message

@tool
def generate_video(food_name: str, description: str) -> str:
    """
    Tạo một video quảng cáo ngắn cho món ăn bằng Google Veo3.
    Args:
        food_name: Tên món ăn để tạo video.
        description: Mô tả để làm kịch bản cho video.
    """
    print(f"**Bắt đầu tạo video cho: {food_name}**")
    try:
        # Client sẽ tự động sử dụng GEMINI_API_KEY từ biến môi trường
        client = genai.Client()

        prompt = f"Create a short, cinematic promotional video for a dish named '{food_name}'. The description is: '{description}'. The video should be vibrant, appetizing, and high-quality."

        operation = client.models.generate_videos(
            model="veo-3.0-generate-preview",
            prompt=prompt,
        )

        print(f"**Đã gửi yêu cầu tạo video cho '{food_name}'. Đang chờ xử lý...**")
        while not operation.done:
            print("Video chưa được tạo. Kiểm tra lại sau 10 giây...")
            time.sleep(10)
            operation = client.operations.get(operation)

        # Truy cập kết quả thông qua 'response' thay vì 'result'
        response = operation.response
        if not response or not response.generated_videos:
            return f"Lỗi: Không thể tạo video cho '{food_name}'."

        generated_video = response.generated_videos[0]
        print(f"**Video đã được tạo: {generated_video.video.uri}**")

        # Tạo thư mục nếu chưa tồn tại
        output_dir = "temp_uploads"
        os.makedirs(output_dir, exist_ok=True)
        
        # Tạo tên file duy nhất
        timestamp = int(time.time())
        safe_food_name = "".join(c for c in food_name if c.isalnum() or c in (' ', '_')).rstrip()
        file_name = f"video_{safe_food_name.replace(' ', '_')}_{timestamp}.mp4"
        output_path = os.path.join(output_dir, file_name)

        # Tải và lưu video
        downloaded_file = client.files.download(file=generated_video.video)
        with open(output_path, 'wb') as f:
            f.write(downloaded_file)
        
        print(f"**Video cho '{food_name}' đã được tải về tại: {output_path}**")
        
        # Trả về chuỗi định dạng đặc biệt
        return f"video_path:{output_path}"

    except Exception as e:
        error_message = f"Đã xảy ra lỗi khi tạo video cho '{food_name}': {e}"
        print(f"**{error_message}**")
        return error_message
