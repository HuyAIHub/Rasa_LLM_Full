from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from ChatBot_Extract_Intent.config_app.config import get_config

config_app = get_config()
openai_api_key=config_app["parameter"]["openai_api_key"]
class ExtractNameAction(Action):

    def name(self) -> Text:
        return "action_extract_name"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_name = None

        for ent in tracker.latest_message.get("entities", []):
            if ent["entity"] == "user_name":
                user_name = ent["value"]

        # You can now use this name in your bot logic
        if user_name:
            dispatcher.utter_message(text=f"Xin chào {user_name}!\nRất vui được gặp {user_name}.Bạn có câu hỏi hoặc yêu cầu cụ thể nào liên quan đến dịch vụ mua sắm của VCC không? Tôi sẽ cố gắng giúp bạn một cách tốt nhất.!")
        else:
            dispatcher.utter_message(text="Xin chào! Tôi là BotV, trợ lý mua sắm của bạn. Tôi có thể giúp gì cho bạn hôm nay?.")

        return []

#policy_produce
class ExtractProduceAction(Action):

    def name(self) -> Text:
        return "action_extract_produce"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        produce_name_policy = None

        for ent in tracker.latest_message.get("entities", []):
            if ent["entity"] == "produce_name_policy":
                produce_name_policy = ent["value"]

        # You can now use this name in your bot logic
        products = ["chính sách", "bảo hành", "chính sách bảo hành", "chinh sach", "bao hanh", "chinh sach bao hanh"]       
        if any(p == produce_name_policy.lower() for p in products):
            dispatcher.utter_message(text=f"""
                Chính sách bảo hành sản phẩm của chúng tôi bao gồm:
                1. Chính sách bảo hành 1 đổi 1
                    - Thời gian áp dụng: Đổi trong 7 ngày từ ngày mua, chi phí bảo hành là 0.5% giá bán.
                    - Điều kiện: Áp dụng cho sản phẩm lỗi theo quy định của VCC, sản phẩm phải nguyên vẹn, không trầy xước, bể, móp méo. Phải trả lại đầy đủ hộp, phụ kiện và hàng khuyến mãi (nếu có). Lỗi phải được xác nhận bởi nhân sự triển khai, và số điện thoại mua sản phẩm phải khớp với dữ liệu hệ thống.
                    Lưu ý: Không áp dụng hoàn tiền
                2. Chính sách bảo hành sửa chữa, thay thế linh kiện
                    - Thời gian: Áp dụng 12 tháng từ ngày mua, căn cứ theo biên bản nghiệm thu và đơn hàng trên hệ thống AIO.
                    - Phạm vi: Áp dụng cho lỗi kỹ thuật do nhà sản xuất. Không bảo hành lỗi do sử dụng, sửa chữa không đúng cách, hoặc nguyên nhân bên ngoài.
                    - Điều kiện: Lỗi được xác nhận bởi nhân sự tại các CNCT, theo Quy trình bảo hành QT.VCC.RRR.2.2-(02) và hướng dẫn của TT. GP&DVKT. Số điện thoại mua phải khớp với dữ liệu hệ thống.
                    Lưu ý: Cần cung cấp hình ảnh/clip sản phẩm lỗi khi yêu cầu bảo hành.
                """)
        else:
            dispatcher.utter_message(text="Quý khách xin thông cảm! Tôi không hiểu câu hỏi của bạn.")

        return []