
from ChatBot_Extract_Intent.config_app.config import get_config
import os
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts.prompt import PromptTemplate
from langchain import PromptTemplate

config_app = get_config()

os.environ['OPENAI_API_KEY'] = config_app["parameter"]["openai_api_key"]
llm = ChatOpenAI(model_name=config_app["parameter"]["gpt_model_to_use"], temperature=config_app["parameter"]["temperature"])

def llm2(query_text, response_rules):
    print('=====llm2======')
    print('response_rules:',response_rules)
    prompt_header = """You are a product information lookup support, your task is to answer customer questions based on the technical paragraphs provided. Note that you need to answer in Vietnamese.
    The following passages may help you answer the questions:
    {snippets}
    Respond to the customer's needs based on the passages.
    For questions that are not in the document, please express your lack of information and respond politely to the customer.
    Provide specific answers, using only information from the documents. Do not mix in information from outside sources.
    All your answers must be in Vietnamese.
    Customer: {input}
    """
    prompt = PromptTemplate.from_template(template = prompt_header)
    chain = prompt | llm

    result = chain.invoke({"snippets": response_rules, "input" : query_text})

    content = result.content
    return content