import os
import json
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts.prompt import PromptTemplate
from langchain import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferWindowMemory, CombinedMemory
from langchain.memory import ChatMessageHistory
from langchain import PromptTemplate
from config_app.config import get_config
from pathlib import Path
from langchain.schema import messages_from_dict, messages_to_dict
from typing import Any, Dict, List

config_app = get_config()


class SnippetsBufferWindowMemory(ConversationBufferWindowMemory):
    """
    MemoryBuffer được sử dụng để giữ các đoạn tài liệu. Kế thừa từ ConversationBufferWindowMemory và ghi đè lên
    phương thức Load_memory_variables
    """

    memory_key = 'snippets'
    snippets: list = []
    response_rules = ''

    def __init__(self, *args, **kwargs):
        ConversationBufferWindowMemory.__init__(self, *args, **kwargs)

    # def load_memory_variables(self, inputs) -> dict:
    #     self.snippets.append(self.response_rules)
    #     self.snippets = [snippet for snippet in self.snippets][-self.k:]
    #     to_return = ''.join(self.snippets)

    #     return {'snippets': to_return}
    
    def load_memory_variables(self, inputs) -> Dict:
        """Return history buffer."""

        buffer: Any = self.buffer[-self.k * 2 :] if self.k > 0 else []
        string_messages = []
        for m in buffer:
            if m.type == 'human':
                message = f"{m.content}"
                string_messages.append(message)
        string_messages.append(response_rules)

        to_return = "\n".join(string_messages)
        return {'snippets': to_return}

def construct_conversation(prompt: str, llm, memory) -> ConversationChain:
    """
    Construct a ConversationChain object
    """

    prompt = PromptTemplate.from_template(
        template=prompt,
    )

    conversation = ConversationChain(
        llm=llm,
        memory=memory,
        verbose=False,
        prompt=prompt
    )
    return conversation


def initialize_chat_conversation(model_to_use, conv_memory, snippets_memory, response_rules) -> ConversationChain:
    prompt_header = """You are a product information lookup support, your task is to answer customer questions based on the technical paragraphs provided and history chat.
    The following passages may help you answer the questions:
    {snippets}
    Respond to the customer's needs based on the passages.
    All your answers must be in Vietnamese.
    {history} 
    Customer: {input}
    """

    os.environ['OPENAI_API_KEY'] = config_app["parameter"]["openai_api_key"]
    llm = ChatOpenAI(model_name=model_to_use, temperature=config_app["parameter"]["temperature"])
    if conv_memory == [] and snippets_memory == []:
        conv_memory = ConversationBufferWindowMemory(k=config_app["parameter"]["search_number_messages"], input_key="input")
        snippets_memory = SnippetsBufferWindowMemory(k=config_app["parameter"]["prompt_number_snippets"], response_rules=response_rules, 
                                                     memory_key='snippets', input_key="snippets")
    else:
        conv_memory = ConversationBufferWindowMemory(k=config_app["parameter"]["search_number_messages"], input_key="input", chat_memory=conv_memory)
        snippets_memory = SnippetsBufferWindowMemory(k=config_app["parameter"]["prompt_number_snippets"], response_rules=response_rules, 
                                                     memory_key='snippets', input_key="snippets", chat_memory=snippets_memory)

    memory = CombinedMemory(memories=[conv_memory, snippets_memory])
    conversation = construct_conversation(prompt_header, llm, memory)

    return conversation

def llm2(query_text, response_rules, IdRequest, NameBot, User):
    print('=====llm2======')
    # print('response_rules:',response_rules)


    path_messages = config_app["parameter"]["DB_MESSAGES"] + str(NameBot) + "/" +  str(User) + "/" + str(IdRequest)
    if not os.path.exists(path_messages):
        os.makedirs(path_messages)
    try:
        with Path(path_messages + "/messages_conv.json").open("r", encoding="utf8") as f:
            loaded_messages_conv = json.load(f)
        with Path(path_messages + "/messages_snippets.json").open("r", encoding="utf8") as f:
            loaded_messages_snippets = json.load(f)
        conversation_messages_snippets = ChatMessageHistory(messages=messages_from_dict(loaded_messages_snippets))
        conversation_messages_conv = ChatMessageHistory(messages=messages_from_dict(loaded_messages_conv))
    except:
        conversation_messages_conv, conversation_messages_snippets = [], []
    
    conversation = initialize_chat_conversation(config_app["parameter"]["gpt_model_to_use"], 
                                                conversation_messages_conv, conversation_messages_snippets, response_rules)

    result = conversation.predict(input = query_text)

    # Save DB
    conversation_messages_conv = conversation.memory.memories[0].chat_memory.messages
    conversation_messages_snippets = conversation.memory.memories[1].chat_memory.messages
    messages_conv = messages_to_dict(conversation_messages_conv)
    messages_snippets  = messages_to_dict(conversation_messages_snippets)
    
    with Path(path_messages + "/messages_conv.json").open("w",encoding="utf-8") as f:
        json.dump(messages_conv, f, indent=4,ensure_ascii=False)
    with Path(path_messages + "/messages_snippets.json").open("w",encoding="utf-8") as f:
        json.dump(messages_snippets, f, indent=4, ensure_ascii=False)

    return result

query_text = 'xông suất tiêu thụ của sản phẩm trên'
# response_rules = """'PRODUCT INFO ID': 606038,
#  'GROUP PRODUCT NAME': 'Điều hòa - Điều hòa MDV - Inverter 9000 BTU',
#  'SPECIFICATION BACKUP': 'Nguồn điện: 220-240V \nCông suất: 9500 Btu/h \nCông suất tiêu thụ: 745 W \nCường độ dòng điện: 3.4 A\n ERR: 3.54 W/W \nInverter : Có Kích thước máy trong ( DxRxC): 726x210x291 (mm) \nKhối lượng thực máy trong/ khối lượng đóng gói: 8.2/10.3 Kg \nKích thước máy ngoài (DxRxC): 835x300x540 (mm) \nKhối lương thực máy ngoài / khối lượng đóng gói: 21.7/23.2 kg \nLoại gas/ khối lượng nạp: R32/0.38 \nÁp suất thiết kế: 4.3/1.7 Mpa \nChiều dài đường ống tối đa: 25m \nChênh lệch độ cao tối đa: 10m Phạm vi lành lạnh hiệu quả : 12~18 m2 \nHiệu suất năng lượng : 4.48 CSPF \nBảo hành 3 năm cho sản phẩm \nBảo hành 5 năm cho máy nén \nSuất xứ : Thái lan\ngiá: 6014184',
#  'PRICE ': 10000000"""
response_rules = ''

result = llm2(query_text, response_rules, 'faaiwe', 'tiu', 'qwe')
print(result)