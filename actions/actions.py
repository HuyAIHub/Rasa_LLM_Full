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
            dispatcher.utter_message(text="Xin chào! Tôi là VCC AI BOT, trợ lý mua sắm của bạn. Tôi có thể giúp gì cho bạn hôm nay?.")

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
        products = ["bảo hành", "chính sách bảo hành", "bao hanh", "chinh sach bao hanh"]       
        if any(p == produce_name_policy.lower() for p in products):
            dispatcher.utter_message(text=f"""
                Chính sách bảo hành sản phẩm của chúng tôi bao gồm:
                1. Chính sách bảo hành 1 đổi 1
                    1.1. Thời gian áp dụng
                    - Một đổi một trong vòng 7 ngày kể từ ngày khách hàng mua hàng, căn cứ theo biên bản nghiệm thu và đơn hàng được đóng thành công trên hệ thống AIO.
                    - Chi phí bảo hành nằm trong 0.5% chi phí giá bán theo quy định TCT.
                    1.2. Điều kiện:
                    - Áp dụng bảo hành đối với các sản phẩm lỗi nằm trong quy định và điều kiện bảo hành 1 đổi 1 của VCC.
                    - Sản phẩm đổi trả phải giữ nguyên 100% hình dạng ban đầu (không bị trầy xước, bể, vỡ, móp méo).
                    - Hoàn trả lại đầy đủ hộp đựng, phụ kiện đi kèm và các hàng khuyến mãi(nếu có)
                    - Lỗi được xác nhận bởi nhân sự triển khai tại CNCT, áp dụng theo hướng dẫn kiểm tra sản phẩm bảo hành do TT. GP&DVKT
                    - Số điện thoại mua sản phẩm trùng khớp với dữ liệu trên hệ thống ghi nhận.
                    Lưu ý: Không áp dụng hoàn tiền sản phẩm
                2. Chính sách bảo hành sửa chữa, thay thế linh kiện
                    2.1. Thời gian
                    - Áp dụng 12 tháng kể từ ngày khách hàng mua sản phẩm, căn cứ theo biên bản nghiệm thu và đơn hàng được đóng thành công trên hệ thống AIO.
                    2.2. Phạm vi
                    - Áp dụng cho các lỗi kỹ thuật do nhà sản xuất (theo danh mục lỗi nhà sản xuất quy định với từng sản phẩm).
                    - Không bảo hành đối với các trường hợp do sử dụng, sửa chữa không đúng cách hoặc hỏng hóc do nguyên nhân bên ngoài.
                    2.3. Điều kiện được bảo hành
                    - Lỗi được xác nhận và kiểm tra bởi nhân sự triển khai tại các CNCT, căn cứ theo Quy trình bảo hành số QT.VCC.RRR.2.2-(02) và hướng dẫn kiểm tra sản
                    phẩm bảo hành do TT. GP&DVKT ban hành.
                    - Số điện thoại mua sản phẩm trùng khớp với dữ liệu trên hệ thống ghi nhận.
                    Lưu ý: Để đảm bảo quyền lợi khách hàng và VCC có cơ sở làm việc với các bộ phận liên quan, quý khách cần cung cấp hình ảnh/clip sản phẩm lỗi khi yêu cầu bảo hành.
                """)
        else:
            dispatcher.utter_message(text="Quý khách xin thông cảm! Tôi không hiểu câu hỏi của bạn.")

        return []
    


class ExtractProduceInventory(Action):

    def name(self) -> Text:
        return "action_extract_produce_inventory"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        produce_name_inventory = None

        for ent in tracker.latest_message.get("entities", []):
            if ent["entity"] == "produce_name_inventory":
                produce_name_inventory = ent["value"]

        # You can now use this name in your bot logic
        products = ["kho", "tồn kho", "sản phẩm tồn kho", "ton kho", "trong kho"]       
        if any(p == produce_name_inventory.lower() for p in products):
            dispatcher.utter_message(text=f"""
                Anh/chị vui lòng nhập mã sản phẩm và mã tỉnh theo mẫu sau: mã sản phẩm: M&EDM000005 và mã tỉnh: HNI
                """)
        else:
            dispatcher.utter_message(text="Quý khách xin thông cảm! Tôi không hiểu yêu cầu của bạn.")

        return []