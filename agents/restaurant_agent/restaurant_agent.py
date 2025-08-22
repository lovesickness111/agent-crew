import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_tavily import TavilySearch

# Tải các biến môi trường từ tệp .env
from dotenv import load_dotenv
load_dotenv()
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

# Import các công cụ đã tạo
from .tools.menu_tools import (
    read_menu,
    add_menu_item,
    edit_menu_item,
    delete_menu_item,
)
from .tools.vision_tools import extract_food_info_from_image
from .tools.generative_tools import generate_image, generate_video

# --- Thiết lập Agent ---

# 1. Thiết lập bộ nhớ
# MemorySaver dùng để lưu lại trạng thái của cuộc trò chuyện
memory = MemorySaver()

# 2. Thiết lập mô hình ngôn ngữ
# Sử dụng Gemini 1.5 Flash làm bộ não cho agent
# Yêu cầu có GEMINI_API_KEY trong biến môi trường
if "GEMINI_API_KEY" not in os.environ:
    raise ValueError("Biến môi trường GEMINI_API_KEY chưa được thiết lập.")
model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0, api_key=os.environ["GEMINI_API_KEY"])

# 3. Khởi tạo các công cụ
# Công cụ tìm kiếm web
search = TavilySearch(max_results=2)

# Tập hợp tất cả các công cụ lại
tools = [
    search,
    read_menu,
    add_menu_item,
    edit_menu_item,
    delete_menu_item,
    extract_food_info_from_image,
    generate_image,
    generate_video,
]

# 4. Tạo Agent Executor
# create_react_agent sẽ tạo ra một agent có khả năng suy luận (Reason) và hành động (Act)
# Agent sẽ tự quyết định khi nào cần dùng công cụ nào dựa trên yêu cầu của bạn
agent_executor = create_react_agent(model, tools, checkpointer=memory)

# Agent này giờ sẽ được gọi thông qua API trong `api.py`.
# Hàm main() và __name__ == "__main__" không còn cần thiết.
