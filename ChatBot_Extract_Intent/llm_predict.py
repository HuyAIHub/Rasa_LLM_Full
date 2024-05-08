import os
import json
from pathlib import Path
from ChatBot_Extract_Intent.config_app.config import get_config
from ChatBot_Extract_Intent.main import process_command
import datetime

config_app = get_config()


def predict_llm(InputText, IdRequest, NameBot, User):
    User = str(User)
    print("----------------NEW_SESSION--------------")
    print("GuildID  = ", IdRequest)

    query_text = InputText
    user_messages_history = InputText
    path_messages = config_app["parameter"]["DB_MESSAGES"] + str(NameBot) + "/" +  str(User) + "/" + str(IdRequest)
    if not os.path.exists(path_messages):
        os.makedirs(path_messages)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    response = process_command(query_text,IdRequest,NameBot,User)
    human_message = {
        "type": "human",
        "data": {
            "content": query_text,
            "type": "human",
            "time": timestamp
        }
    }
    bot_message = {
        "type": "ai",
        "data": {
            "content": response,
            "type": "ai",
            "time": timestamp
        }
    }

    conversation = [human_message, bot_message]
    with Path(path_messages + "/messages_conv.json").open("a",encoding="utf-8") as f:
        json.dump(conversation, f, indent=4,ensure_ascii=False)

    return response