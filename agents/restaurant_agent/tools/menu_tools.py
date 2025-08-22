import json
from langchain_core.tools import tool
from typing import List, Dict, Any

MENU_FILE = "agents/restaurant_agent/menu.json"

def load_menu() -> List[Dict[str, Any]]:
    """Tải thực đơn từ file JSON."""
    try:
        with open(MENU_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_menu(menu: List[Dict[str, Any]]):
    """Lưu thực đơn vào file JSON."""
    with open(MENU_FILE, 'w', encoding='utf-8') as f:
        json.dump(menu, f, indent=4, ensure_ascii=False)

@tool
def read_menu() -> str:
    """
    Đọc và hiển thị toàn bộ thực đơn hiện tại.
    Hữu ích khi người dùng muốn xem có những món ăn nào.
    """
    menu = load_menu()
    if not menu:
        return "Thực đơn hiện đang trống."
    return json.dumps(menu, indent=4, ensure_ascii=False)

@tool
def add_menu_item(name: str, description: str, price: float) -> str:
    """
    Thêm một món ăn mới vào thực đơn.
    Sử dụng công cụ này khi người dùng muốn thêm một món ăn cụ thể.
    Args:
        name: Tên của món ăn.
        description: Mô tả chi tiết về món ăn.
        price: Giá của món ăn.
    """
    menu = load_menu()
    # Kiểm tra xem món ăn đã tồn tại chưa
    if any(item['name'].lower() == name.lower() for item in menu):
        return f"Lỗi: Món ăn '{name}' đã tồn tại trong thực đơn."
    
    menu.append({"name": name, "description": description, "price": price})
    save_menu(menu)
    return f"Đã thêm thành công món '{name}' vào thực đơn."

@tool
def edit_menu_item(name: str, new_description: str = None, new_price: float = None) -> str:
    """
    Chỉnh sửa mô tả hoặc giá của một món ăn đã có trong thực đơn.
    Chỉ cập nhật các trường được cung cấp (mô tả hoặc giá).
    Args:
        name: Tên của món ăn cần chỉnh sửa.
        new_description: Mô tả mới cho món ăn (tùy chọn).
        new_price: Giá mới cho món ăn (tùy chọn).
    """
    menu = load_menu()
    item_found = False
    for item in menu:
        if item['name'].lower() == name.lower():
            if new_description is not None:
                item['description'] = new_description
            if new_price is not None:
                item['price'] = new_price
            item_found = True
            break
            
    if not item_found:
        return f"Lỗi: Không tìm thấy món ăn '{name}' trong thực đơn."
        
    save_menu(menu)
    return f"Đã cập nhật thành công thông tin cho món '{name}'."

@tool
def delete_menu_item(name: str) -> str:
    """
    Xóa một món ăn khỏi thực đơn dựa vào tên.
    Sử dụng khi người dùng muốn loại bỏ một món ăn.
    Args:
        name: Tên của món ăn cần xóa.
    """
    menu = load_menu()
    original_length = len(menu)
    new_menu = [item for item in menu if item['name'].lower() != name.lower()]
    
    if len(new_menu) == original_length:
        return f"Lỗi: Không tìm thấy món ăn '{name}' để xóa."
        
    save_menu(new_menu)
    return f"Đã xóa thành công món '{name}' khỏi thực đơn."

@tool
def add_multiple_menu_items(items: List[Dict[str, Any]]) -> str:
    """
    Thêm nhiều món ăn mới vào thực đơn cùng một lúc từ một danh sách.
    Công cụ này rất hữu ích khi phân tích một hình ảnh có nhiều món ăn và muốn thêm tất cả chúng vào thực đơn.
    Args:
        items: Một danh sách các món ăn. Mỗi món ăn phải là một dictionary
               chứa 'name' (tên), 'description' (mô tả), và 'price' (giá).
    """
    menu = load_menu()
    added_count = 0
    skipped_items = []
    added_items_names = []

    for item in items:
        name = item.get('name')
        description = item.get('description', '') # Cung cấp giá trị mặc định
        price = item.get('price')

        if not name or price is None:
            skipped_items.append(name or "Món ăn không tên (thiếu thông tin)")
            continue

        # Kiểm tra xem món ăn đã tồn tại chưa
        if any(existing_item['name'].lower() == name.lower() for existing_item in menu):
            skipped_items.append(f"{name} (đã tồn tại)")
            continue
        
        menu.append({"name": name, "description": description, "price": price})
        added_count += 1
        added_items_names.append(name)

    if added_count > 0:
        save_menu(menu)

    # Tạo thông điệp phản hồi
    if added_count == 0:
        response = "Không có món ăn mới nào được thêm."
    else:
        response = f"Đã thêm thành công {added_count} món ăn mới: {', '.join(added_items_names)}."

    if skipped_items:
        response += f" Các món sau đã bị bỏ qua: {', '.join(skipped_items)}."
    
    return response
