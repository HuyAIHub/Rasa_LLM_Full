# import psycopg2
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import os,re
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts.few_shot import FewShotPromptTemplate
from langchain.prompts.prompt import PromptTemplate
from ChatBot_Extract_Intent.config_app.config import get_config
# from config_app.config import get_config
from langchain.chains import LLMChain
from difflib import get_close_matches
import csv
import numpy as np
from openai import OpenAI
# from ChatBot_Extract_Intent.extract_price_info import take_product
import random
import pandas as pd
from unidecode import unidecode
import time
config_app = get_config()

os.environ['OPENAI_API_KEY'] = config_app["parameter"]["openai_api_key"]
llm = ChatOpenAI(model_name=config_app["parameter"]["gpt_model_to_use"], temperature=config_app["parameter"]["temperature"])
client = OpenAI(api_key=config_app["parameter"]["openai_api_key"])
ELASTIC_HOST = "http://10.248.243.105:9200"
df = pd.read_csv("/data/Production/SLuan_elastic_LLM/ChatBot_Extract_Intent/data/product_final_31_5.csv")

def split_sentences(text_input):
    examples = config_app['parameter']['example_input']
    example_formatter_template = """
        input text from user: {input_text}

        correct input and insert command below:
        command: {command}

        the information extracted from above command

        object: {object}
        value: {value}
        power: {power}
        weight: {weight}
        volume: {volume}
        intent: {intent}
    """

    example_prompt = PromptTemplate(
        input_variables=["input_text", "command", "object", "value", "power", "weight", "volume", "intent"],
        template=example_formatter_template,
    )

    few_shot_prompt = FewShotPromptTemplate(
        # These are the examples we want to insert into the prompt.
        examples=examples,
        # This is how we want to format the examples when we insert them into the prompt.
        example_prompt=example_prompt,
        # The prefix is some text that goes before the examples in the prompt.
        prefix="Please correct the following sentence for correct spelling and lowercase. Return the correctly spelled sentence.",
        # The suffix is some text that goes after the examples in the prompt.
        suffix="input command from user: {input_text}\ninformation corrected for spelling from the above command",
        # The input variables are the variables that the overall prompt expects.
        input_variables=["input_text"],
        # The example_separator is the string we will use to join the prefix, examples, and suffix together with.
        example_separator="\n\n",
    )

    # Print the formatted prompt for debugging purposes (optional)
    # print(few_shot_prompt.format(input_text="Mua den nang luong mat troi giá 15 triệu"))

    chain = LLMChain(llm=llm, prompt=few_shot_prompt)

    result = chain.run(input_text=text_input)
    
    return result.lower()

def extract_info(chuoi):
    chuoi = split_sentences(chuoi)
    variables = {}
    lines = chuoi.strip().split('\n')
    for line in lines:
        parts = line.split(':')
        if len(parts) == 2:
            key = parts[0].strip()
            value = parts[1].strip()
            if key == 'object':
                # Xử lý phần object
                # Loại bỏ các dấu ngoặc và khoảng trắng
                value = value.replace('[', '').replace(']', '').strip()
                # Tách các giá trị theo dấu phẩy
                object_list = [item.strip().strip("'") for item in value.split(',') if item.strip()]
                variables[key] = object_list
            else:
                variables[key] = value
    return variables

def get_embedding(text, model="text-embedding-ada-002"):
   text = text.replace("\n", " ")
   return client.embeddings.create(input = [text], model=model).data[0].embedding

def init_elastic(df, index_name, hosts):
    # Create the client instance
    client = Elasticsearch([hosts])

    # Define the mappings
    mappings = {
        "properties": {
            "PRODUCT_INFO_ID": {"type": "text"},
            "GROUP_PRODUCT_NAME": {"type": "text"},
            "SPECIFICATION_BACKUP": {"type": "text"},
            "POWER": {"type": "float"},
            "WEIGHT": {"type": "float"},
            "VOLUME": {"type": "float"},
            "RAW_PRICE": {"type": "integer"}
        }
    }

    # Create the index with mappings
    if not client.indices.exists(index=index_name):
        client.indices.create(index=index_name, body={"mappings": mappings})
        # Index documents
        for i, row in df.iterrows():
            doc = {
                "PRODUCT_INFO_ID": row["PRODUCT_INFO_ID"],
                "GROUP_PRODUCT_NAME": row["GROUP_PRODUCT_NAME"],
                "SPECIFICATION_BACKUP": row["SPECIFICATION_BACKUP"],
                "POWER": row["POWER"],
                "WEIGHT": row["WEIGHT"],
                "VOLUME": row["VOLUME"],
                "RAW_PRICE": row["RAW_PRICE"]
            }
            client.index(index=index_name, id=i, document=doc)

        client.indices.refresh(index=index_name)
        print(f"Index {index_name} created.")
    else:
        print(f"Index {index_name} already exists.")

    return client

def parse_price_range(value):
    pattern = r"(?P<prefix>\b(dưới|trên|từ|đến|khoảng)\s*)?(?P<number>\d+(?:,\d+)*)\s*(?P<unit>triệu|nghìn|tr|k|kg|l|lít|W|w)?\b"

    min_price = 0
    max_price = 100000000
    for match in re.finditer(pattern, value, re.IGNORECASE):
        prefix = match.group('prefix') or ''
        number = float(match.group('number').replace(',', ''))
        unit = match.group('unit') or ''

        if unit.lower() in ['triệu','tr']:
            number *= 1000000
        elif unit.lower() in ['nghìn','k']:
            number *= 1000

        if prefix.lower().strip() == 'dưới':
            max_price = min(max_price, number)
        elif prefix.lower().strip() == 'trên':
            min_price = min(max_price, number)
        elif prefix.lower().strip() == 'từ':
            min_price = min(max_price, number)
        elif prefix.lower().strip() == 'đến':
            max_price = max(min_price, number)
        else:  # Trường hợp không có từ khóa
            min_price = number * 0.9
            max_price = number * 1.1

    if min_price == float('inf'):
        min_price = 0
    print('min_price, max_price:',min_price, max_price)
    return min_price, max_price
#---------------------------------------------
# def search_intent(client, index_name, product_name, intent):
#     if intent is None:
#         raise ValueError("Intent cannot be None. Please provide a valid intent.")

#     if "rẻ" in intent.lower():
#         order = "asc"
#     elif "đắt" in intent.lower():
#         order = "desc"
    
#     query = {
#         "query": {
#             "bool": {
#                 "must": []
#             }
#         },
#         "sort": [
#             {
#                 "RAW_PRICE": {
#                     "order": order
#                 }
#             }
#         ],
#         "size": 3
#     }
#     if product_name:
#         query["query"]["bool"]["must"].append({
#             "match": {
#                 "GROUP_PRODUCT_NAME": product_name
#             }
#         })
#     # print(query)
#     res = client.search(index=index_name, body=query)
#     return res
#------------------------------
def search_intent(client, index_name, product_name, intent):
    if intent is None:
        raise ValueError("Intent cannot be None. Please provide a valid intent.")

    # Default sort order
    sort_field = "RAW_PRICE"
    order = "asc"  # Default to ascending order

    # Adjust sorting based on intent
    if "rẻ" in intent.lower():
        order = "asc"
    elif "đắt" in intent.lower():
        order = "desc"
    elif "công suất lớn nhất" or "công suất cao nhất" in intent.lower():
        sort_field = "POWER"
        order = "desc"  # Highest power first
    elif "công suất nhỏ nhất" or "công suất thấp nhất" in intent.lower():
        sort_field = "POWER"
        order = "asc"  # Lowest power first

    # Build the query
    query = {
        "query": {
            "bool": {
                "must": []
            }
        },
        "sort": [
            {
                sort_field: {
                    "order": order
                }
            }
        ],
        "size": 3
    }
    
    # Add product name to the query if provided
    if product_name:
        query["query"]["bool"]["must"].append({
            "match": {
                "GROUP_PRODUCT_NAME": product_name
            }
        })

    # Execute the search
    res = client.search(index=index_name, body=query)
    return res
#==========
def search_products(client, index_name, product_name=None, value=None, power=None, weight=None, volume=None):
    # Build the base query
    query = {
        "query": {
            "bool": {
                "must": []
            }
        }
    }

    # Add product name to query
    if product_name:
        query["query"]["bool"]["must"].append({
            "match": {
                "GROUP_PRODUCT_NAME": product_name
            }
        })

    # Add intent-based filters
    if value:
        min_price, max_price = parse_price_range(value)
        price_filter = {
            "range": {
                "RAW_PRICE": {
                    "gte": min_price,
                    "lte": max_price
                }
            }
        }
        query["query"]["bool"]["must"].append(price_filter)

    if power:
        min_power, max_power = parse_price_range(power)
        power_filter = {
            "range": {
                "POWER": {
                    "gte": min_power,
                    "lte": max_power
                }
            }
        }
        query["query"]["bool"]["must"].append(power_filter)

    if weight:
        min_weight, max_weight = parse_price_range(weight)
        weight_filter = {
            "range": {
                "WEIGHT": {
                    "gte": min_weight,
                    "lte": max_weight
                }
            }
        }
        query["query"]["bool"]["must"].append(weight_filter)

    if volume:
        min_volume, max_volume = parse_price_range(volume)
        volume_filter = {
            "range": {
                "VOLUME": {
                    "gte": min_volume,
                    "lte": max_volume
                }
            }
        }
        query["query"]["bool"]["must"].append(volume_filter)

    try:
        res = client.search(index=index_name, body=query)
        
    except Exception as e:
        print(f"Error searching for {product_name}: {e}")
    return res

def search_db(command):
    demands = extract_info(command)
    print(demands)
    product_names = demands['object']
    value = demands['value']
    power = demands['power']
    weight = demands['weight']
    volume = demands['volume']
    intent = demands['intent']
    index_name = "test2"
    client = init_elastic(df,index_name, ELASTIC_HOST)
    
    if product_names == []:
        out_text = "bạn có thể cho tôi biết tên sản phẩm cụ thể bạn quan tâm để tôi có thể hỗ trợ bạn được không?"
        return 0
    result = []
    t1 = time.time()
    for product_name in product_names:
        if intent:
            resp = search_intent(client, index_name, product_name, intent)
        else:
            resp = search_products(client, index_name, product_name, value, power, weight, volume)
        result.append(resp)
        # print(result)
    out_text = '\n\nĐể phù hợp với ngân sách và nhu cầu sử dụng của bạn, VCC Bot đề xuất một số sản phẩm sau:'
    for product_name, product in zip(product_names,result):
        out_text += f"\nVới sản phẩm {product_name}:\n"
        object = product_name
        for i, hit in enumerate(product['hits']['hits']):
            check_score = hit['_score']
            product = hit['_source']
            
            if check_score is None or (float(check_score) >= 5.5 and i < 5):
                out_text += f"\n\nSản phẩm {i + 1}:\n"
                out_text += f"Tên sản phẩm: {product['GROUP_PRODUCT_NAME']} (ID: {hit['_id']})\n"
                out_text += f"Thông số kỹ thuật: {product['SPECIFICATION_BACKUP']}\n"
                out_text += f"Giá tiền: {product['RAW_PRICE']} VND\n"
    print("Time search elastic", time.time() - t1)
    return object,out_text

# print(search_db("den nang luong mat troi"))
# print(df)