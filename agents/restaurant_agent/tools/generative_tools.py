from langchain_core.tools import tool

@tool
def generate_image(food_name: str, description: str) -> str:
    """
    (Placeholder) Tạo một hình ảnh quảng cáo cho món ăn.
    Công cụ này hiện chưa được triển khai đầy đủ.
    Args:
        food_name: Tên món ăn để tạo ảnh.
        description: Mô tả để làm nguồn cảm hứng cho ảnh.
    """
    print(f"**Đang giả lập tạo ảnh cho: {food_name}**")
    return f"Đây là đường dẫn đến ảnh đã tạo cho '{food_name}': [chưa triển khai]"

@tool
def generate_video(food_name: str, description: str) -> str:
    """
    (Placeholder) Tạo một video quảng cáo ngắn cho món ăn.
    Công cụ này hiện chưa được triển khai đầy đủ.
    Args:
        food_name: Tên món ăn để tạo video.
        description: Mô tả để làm kịch bản cho video.
    """
    print(f"**Đang giả lập tạo video cho: {food_name}**")
    return f"Đây là đường dẫn đến video đã tạo cho '{food_name}': [chưa triển khai]"
