import os
import json
from pathlib import Path
from ChatBot_Extract_Intent.module.llm import initialize_chat_conversation
import re
from ChatBot_Extract_Intent.download_and_load_index_data import load_and_index_pdf
from ChatBot_Extract_Intent.config_app.config import get_config
from langchain.memory import (
    ChatMessageHistory,
    ConversationBufferMemory,
    ConversationBufferWindowMemory,
    ConversationSummaryBufferMemory,
    VectorStoreRetrieverMemory,
)
from langchain.schema import messages_from_dict, messages_to_dict

config_app = get_config()
# DATA_PATH: "data/"
# DB_FAISS_PATH: "vectorstore/db_faiss"
# DB_MESSAGES: "db_messages/"

# search_number_messages = config_app["parameter"]["search_number_messages"]

faiss_index = load_and_index_pdf()

def predict_llm(InputText, IdRequest, NameBot, User):
    User = str(User)
    print("----------------NEW_SESSION--------------")
    print("GuildID  = ", IdRequest)
    print("InputText  = ", InputText)

    query_text = InputText
    user_messages_history = InputText
    path_messages = config_app["parameter"]["DB_MESSAGES"] + str(NameBot) + "/" +  str(User) + "/" + str(IdRequest)
    if not os.path.exists(path_messages):
        os.makedirs(path_messages)

    # Load memory
    try:
        with Path(path_messages + "/messages_conv.json").open("r") as f:
            loaded_messages_conv = json.load(f)
        with Path(path_messages + "/messages_snippets.json").open("r") as f:
            loaded_messages_snippets = json.load(f)
        conversation_messages_snippets = ChatMessageHistory(messages=messages_from_dict(loaded_messages_snippets))
        conversation_messages_conv = ChatMessageHistory(messages=messages_from_dict(loaded_messages_conv))
    except:
        conversation_messages_conv, conversation_messages_snippets = None, None

    # Predict Text
    conversation = initialize_chat_conversation(faiss_index, config_app["parameter"]["gpt_model_to_use"],
                                                conversation_messages_conv, conversation_messages_snippets)
    response = conversation.predict(input=query_text, user_messages_history=user_messages_history)

    # Save DB
    conversation_messages_conv = conversation.memory.memories[0].chat_memory.messages
    conversation_messages_snippets = conversation.memory.memories[1].chat_memory.messages
    messages_conv = messages_to_dict(conversation_messages_conv)
    messages_snippets  = messages_to_dict(conversation_messages_snippets)
    
    with Path(path_messages + "/messages_conv.json").open("w",encoding="utf-8") as f:
        json.dump(messages_conv, f, indent=4,ensure_ascii=False)
    with Path(path_messages + "/messages_snippets.json").open("w",encoding="utf-8") as f:
        json.dump(messages_snippets, f, indent=4,ensure_ascii=False)
    print('LLM out:',response)
    return response