import os
import json
from pathlib import Path
from module.llm import initialize_chat_conversation
import re
from download_and_load_index_data import load_and_index_pdf
from config_app.config import get_config
from langchain.memory import (
    ChatMessageHistory,
    ConversationBufferMemory,
    ConversationBufferWindowMemory,
    ConversationSummaryBufferMemory,
    VectorStoreRetrieverMemory,
)
from langchain.agents import (
    create_openai_functions_agent,
    Tool,
    AgentExecutor,
)
from langchain import hub
from langchain.schema import messages_from_dict, messages_to_dict
from langchain_community.chat_models import ChatOpenAI
from extract_price_info import take_product
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

config_app = get_config()
# DATA_PATH: "data/"
# DB_FAISS_PATH: "vectorstore/db_faiss"
# DB_MESSAGES: "db_messages/"

# search_number_messages = config_app["parameter"]["search_number_messages"]

os.environ['OPENAI_API_KEY'] = config_app["parameter"]["openai_api_key"]
agent_chat_model = ChatOpenAI(model_name=config_app["parameter"]["gpt_model_to_use"], temperature=config_app["parameter"]["temperature"])

faiss_index = load_and_index_pdf()

def predict_llm(InputText, IdRequest, NameBot, User, log_obj):
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
    # response = conversation.predict(input=query_text, user_messages_history=user_messages_history)
    # print('conversation_messages_conv:',memory)
    
    def review_product(query_text):
        return conversation.predict(input=query_text, user_messages_history=user_messages_history)

    tools = [
        Tool(
            name="Reviews",
            func=review_product,
            description="""Answer all questions about product information.
            If you can't find the right tool, it will default here.
            Pass the entire question as input to the tool.
            For instance, if the question is "tôi quan tâm đến điều hòa?",
            the input should be "tôi quan tâm đến điều hòa?"
            """,
        ),
        # Tool(
        #     name="Buy",
        #     func=take_product,
        #     description="""LangChain cung cấp một công cụ hữu ích cho người dùng có nhu cầu tìm kiếm 
        #     thông tin về sản phẩm hoặc dịch vụ. Khi người dùng cung cấp thông tin 
        #     về mức tiền mà họ muốn chi tiêu, để công cụ có thể đề xuất các sản phẩm phù hợp với ngân sách của họ. 
        #     Bằng cách này, người dùng có thể dễ dàng tìm kiếm và so sánh các sản phẩm hoặc dịch vụ mà họ quan tâm, 
        #     giúp họ ra quyết định mua hàng thông minh và hiệu quả.,
        #     """,
        # ),
    ]

    hospital_agent_prompt = hub.pull("hwchase17/openai-functions-agent")

    hospital_agent = create_openai_functions_agent(
        llm=agent_chat_model,
        prompt=hospital_agent_prompt,
        tools=tools,
    )

    hospital_rag_agent_executor = AgentExecutor(
        agent=hospital_agent,
        tools=tools,
        return_intermediate_steps=True,
        verbose=True
    )

    response = hospital_rag_agent_executor.invoke({'chat_history':memory.chat_memory.messages,
                                                    "input": query_text})

    # print('response:',response)
    # Save DB
    conversation_messages_conv = conversation.memory.memories[0].chat_memory.messages
    conversation_messages_snippets = conversation.memory.memories[1].chat_memory.messages
    if response['intermediate_steps'] == [] or response['intermediate_steps'][0][0].tool != "Reviews":
        conversation_messages_conv.append(HumanMessage(content=query_text))
        conversation_messages_conv.append(AIMessage(content=response['output']))
        conversation_messages_snippets.append(HumanMessage(content=query_text))
        conversation_messages_snippets.append(AIMessage(content=response['output']))
    
    messages_conv = messages_to_dict(conversation_messages_conv)
    messages_snippets  = messages_to_dict(conversation_messages_snippets)
    
    with Path(path_messages + "/messages_conv.json").open("w",encoding="utf-8") as f:
        json.dump(messages_conv, f, indent=4,ensure_ascii=False)
    with Path(path_messages + "/messages_snippets.json").open("w",encoding="utf-8") as f:
        json.dump(messages_snippets, f, indent=4, ensure_ascii=False)

    return response['output']

# predict_llm('tôi muốn mua tủ lạnh giá 20 triệu', 'c', 'c', 'c', 'a')