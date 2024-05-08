from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import UserUtteranceReverted
from chat import predict_rasa_llm
import requests

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

    
class Actionseachproduct(Action):
    def name(self) -> Text:
        return "action_search_product"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any], ) -> List[Dict[Text, Any]]:
        # Lấy tin nhắn từ người dùng từ Rasa tracker
        user_message = tracker.latest_message.get("text").split(",")
        print('user_message:',user_message)
        result = {}

        # Duyệt qua các cặp khóa-giá trị và thêm vào dict
        for pair in user_message:
            key, value = pair.split(":")
            key = key.strip()  # Loại bỏ khoảng trắng
            value = value.strip()  # Loại bỏ khoảng trắng
            result[key] = value
        print("result:",result)
        # Call the llm_predict function and retrieve its result
        message = predict_rasa_llm(result['InputText'],result['IdRequest'], result['NameBot'], result['User'],type = 'llm')

        # You can now use the result as needed
        # print(f"Result from predict_llm: {result}")
        dispatcher.utter_message(message)
        # Return an empty list, as this is a custom action
        return []

