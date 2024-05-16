import os
from langchain_core.prompts import PromptTemplate
from langchain.llms import OpenAI
from ChatBot_Extract_Intent.config_app.config import get_config

config_app = get_config()

text1 = '''Sản phẩm 'bếp từ' tìm thấy:
- Bếp từ đôi AIO Smart - Giá: 4962870 - Số lượng đã bán: 16
  Thông số kỹ thuật:
    • Công suất: 4400W 
    • Trái: 2200W - Phải: 2200W 
    • Chất liệu mặt bếp: Kính Vitro Ceramic 
    • Bảng điều khiển: Cảm ứng 
- Bếp từ đơn AIO Smart kèm nồi - Giá: 1089000 - Số lượng đã bán: 6
  Thông số kỹ thuật:
    Công suất vùng nấu: 2100W 
    Kích thước vùng nấu: 200mm 
    Bảng điều khiển: cảm ứng 
    Chất liệu mặt bếp: Kính Microcrystalline (cường lực, chịu nhiệt) 
    Khóa phím, chống nhiễu điện tử, tự ngắt khi điện áp tăng giảm đột ngột quá ngưỡng '''

prompt_template = """Bạn là một trợ lý hỗ trợ thông tin sản phẩm. Nhiệm vụ của bạn là trả lời các câu hỏi của khách hàng dựa trên các đoạn thông tin kỹ thuật được cung cấp. 
Đoạn thông tin sau có thể giúp bạn trả lời các câu hỏi:
{}
Hãy trả lời các yêu cầu của khách hàng dựa trên các đoạn thông tin này và lịch sử cuộc trò chuyện. Xem lại các tin nhắn trước đó để hiểu ngữ cảnh.
Cung cấp câu trả lời cụ thể, chỉ sử dụng thông tin được cung cấp ở trên. Không trộn lẫn thông tin từ nguồn bên ngoài.
Tất cả các câu trả lời của bạn phải bằng tiếng Việt.
Khách hàng: {}
"""

prompt_header = prompt_template.format(text1, "Sản phẩm bếp từ nào bán chạy nhất")

# Khởi tạo đối tượng OpenAI
api_key = config_app["parameter"].get("openai_api_key")
if not api_key:
    raise ValueError("API key is missing")

llm = OpenAI(openai_api_key=api_key)

# Dự đoán và in kết quả
try:
    prediction = llm.predict(prompt_header)
    print(prediction)
except Exception as e:
    print(f"An error occurred: {e}")