import os
import json
from pathlib import Path
from ChatBot_Extract_Intent.module.llm import initialize_chat_conversation
from ChatBot_Extract_Intent.download_and_load_index_data import load_and_index_pdf
from ChatBot_Extract_Intent.config_app.config import get_config
from langchain.memory import (
    ChatMessageHistory
)
from langchain.schema import messages_from_dict, messages_to_dict
from langchain_community.chat_models import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import requests
from ChatBot_Extract_Intent.main import search_db
import random
<<<<<<< HEAD
import logging
import datetime
logging.basicConfig(filename=f"logs/{datetime.date.today()}_chatbot.log", level=logging.INFO, format='%(asctime)s - %(message)s')
=======
from ChatBot_Extract_Intent.module.llm2 import llm2
>>>>>>> fc8d1f2c2afe319a6100fca45c0bcc08d1bc2dec

random_number = random.randint(0, 4)

config_app = get_config()

os.environ['OPENAI_API_KEY'] = config_app["parameter"]["openai_api_key"]
llm = ChatOpenAI(model_name=config_app["parameter"]["gpt_model_to_use"], temperature=config_app["parameter"]["temperature"])
faiss_index = load_and_index_pdf()


def predict_rasa_llm(InputText, IdRequest, NameBot, User,type='rasa'):
    User = str(User)
    print("----------------NEW_SESSION--------------")
    print("GuildID  = ", IdRequest)

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
        conversation_messages_conv, conversation_messages_snippets = [], []

    # Predict Text
    conversation, memory = initialize_chat_conversation(faiss_index, config_app["parameter"]["gpt_model_to_use"],
                                                conversation_messages_conv, conversation_messages_snippets)
<<<<<<< HEAD
    results = {'out_text':''}

    # message_data = '''InputText:{},IdRequest:{},NameBot:{},User:{}'''.format(InputText,IdRequest,NameBot,User)
    response = requests.post('http://127.0.0.1:5005/webhooks/rest/webhook', json={"sender": "test", "message": query_text})
    if len(response.json()) == 0:
        results['out_text'] = config_app['parameter']['can_not_res'][random_number]
    else:
        logging.info("------------rasa------------")
        logging.info(f"User: {query_text}")
        results['out_text'] = response.json()[0]["text"]
=======
    results = {
        'terms':'','out_text':''}
    if type == 'rasa':
        # message_data = '''InputText:{},IdRequest:{},NameBot:{},User:{}'''.format(InputText,IdRequest,NameBot,User)
        response = requests.post('http://127.0.0.1:5005/webhooks/rest/webhook', json={"sender": "test", "message": query_text})

        if len(response.json()) == 0:
            results['out_text'] = config_app['parameter']['can_not_res'][random_number]
        elif response.json()[0].get("buttons"):
            results['terms'] = response.json()[0]["buttons"]
            results['out_text'] = response.json()[0]["text"]
        else:
            results['out_text'] = response.json()[0]["text"]
>>>>>>> fc8d1f2c2afe319a6100fca45c0bcc08d1bc2dec

    if results['out_text'] == "LLM_predict":
        logging.info("------------llm------------")
        logging.info(f"User: {query_text}")
        try:
            response = search_db(query_text)
            num_check , response_rules = response[0], response[1]
            if num_check == 0:
                results['out_text'] = response_rules
            else:
<<<<<<< HEAD
                result = llm.invoke("Trả lời câu hỏi sau: " + query_text + " dựa trên các thông tin dưới đây\n" + response_rules)
                results['out_text'] = result.content
            
=======
                
                result = llm2(query_text, response_rules)
                results['out_text'] = result
>>>>>>> fc8d1f2c2afe319a6100fca45c0bcc08d1bc2dec
        except:
            
            results['out_text'] = config_app['parameter']['can_not_res'][random_number]
    
    # Save DB
    conversation_messages_conv = conversation.memory.memories[0].chat_memory.messages
    conversation_messages_snippets = conversation.memory.memories[1].chat_memory.messages
    if type == "rasa":
        conversation_messages_conv.append(HumanMessage(content=query_text))
        conversation_messages_conv.append(AIMessage(content=results['out_text']))
        conversation_messages_snippets.append(HumanMessage(content=query_text))
        conversation_messages_snippets.append(AIMessage(content=results['out_text']))

    messages_conv = messages_to_dict(conversation_messages_conv)
    messages_snippets  = messages_to_dict(conversation_messages_snippets)

    with Path(path_messages + "/messages_conv.json").open("w",encoding="utf-8") as f:
        json.dump(messages_conv, f, indent=4,ensure_ascii=False)
    with Path(path_messages + "/messages_snippets.json").open("w",encoding="utf-8") as f:
        json.dump(messages_snippets, f, indent=4, ensure_ascii=False)
<<<<<<< HEAD
    logging.info(f"Vcc_bot: {results['out_text']}")
    return results['out_text']
=======

    return results
>>>>>>> fc8d1f2c2afe319a6100fca45c0bcc08d1bc2dec
