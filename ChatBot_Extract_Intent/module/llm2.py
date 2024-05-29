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
from ChatBot_Extract_Intent.config_app.config import get_config
from pathlib import Path
from langchain.schema import messages_from_dict, messages_to_dict
from typing import Any, Dict, List
from langchain_core.messages.human import HumanMessage

config_app = get_config()

os.environ['OPENAI_API_KEY'] = config_app["parameter"]["openai_api_key"]
llm = ChatOpenAI(model_name=config_app["parameter"]["gpt_model_to_use"], temperature=config_app["parameter"]["temperature"])

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
    
    def load_memory_variables(self, inputs) -> Dict:
        """Return history buffer."""

        buffer: Any = self.buffer[-self.k * 2 :] if self.k > 0 else []
        string_messages = []
        for m in buffer:
            if isinstance(m, HumanMessage):
                message = f"{m.content}"
                string_messages.append(message)
        string_messages.append(self.response_rules)

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


def initialize_chat_conversation(conv_memory, snippets_memory, response_rules) -> ConversationChain:
    prompt_header = """You are a product information lookup support, your task is to answer customer questions based on the technical paragraphs provided and history chat.
    The following passages may help you answer the questions:
    {snippets}
    Respond to the customer's needs based on the passages.
    All your answers must be in Vietnamese.
    {history} 
    Customer: {input}
    """

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

def llm2(query_text, response_rules):
    print('=====llm2======')
    print('response_rules:',response_rules)
    prompt_header = """You are a product information lookup support, your task is to answer customer questions based on the technical paragraphs provided. Note that you need to answer in Vietnamese.
    The following passages may help you answer the questions:
    {snippets}
    Respond to the customer's needs based on the passages.
    For questions that are not in the document, please express your lack of information and respond politely to the customer.
    Provide specific answers, using only information from the documents. Do not mix in information from outside sources.
    All your answers must be in Vietnamese.zz
    Customer: {input}
    """
    prompt = PromptTemplate.from_template(template = prompt_header)
    chain = prompt | llm

    result = chain.invoke({"snippets": response_rules, "input" : query_text})

    content = result.content
    return content