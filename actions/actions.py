from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import UserUtteranceReverted
from ChatBot_Extract_Intent.llm_predict import predict_llm
import requests
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

#produce
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
                Chính sách bảo hành sản phẩm {produce_name_policy} của chúng tôi bao gồm:
        1. Chính sách bảo hành 1 đổi 1
        2. Chính sách bảo hành sửa chữa, thay thế linh kiện
        Nếu muốn biết thông tin chi tiết của từng chính sách bạn có thể hỏi tôi cụ thể hơn.
        Lưu ý: Để đảm bảo quyền lợi khách hàng và VCC có cơ sở làm việc với các bộ phận liên quan, quý khách cần cung cấp hình ảnh/clip sản phẩm lỗi khi yêu cầu bảo hành.
                """)
        else:
            dispatcher.utter_message(text="Quý khách xin thông cảm! Tôi không hiểu câu hỏi của bạn.")

        return []
    