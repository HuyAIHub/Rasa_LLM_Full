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
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
config_app = get_config()

os.environ['OPENAI_API_KEY'] = config_app["parameter"]["openai_api_key"]
llm = ChatOpenAI(model_name=config_app["parameter"]["gpt_model_to_use"], temperature=config_app["parameter"]["temperature"])
client = OpenAI(api_key=config_app["parameter"]["openai_api_key"])
# ELASTIC_HOST = "http://10.248.243.105:9200"
ELASTIC_CLOUD_ID = "My_deployment:dXMtY2VudHJhbDEuZ2NwLmNsb3VkLmVzLmlvJDNhMTAxYThmYmRjNjQ1MDk4ZGIwMmM2ZDU1ZWU2MjU3JGYxMzhjMzZmMDI5YjRiZTc5NzhkZjUwNzhjZjZlMmU0"
ELASTIC_API_KEY = "Uk82aktwQUJLeFdtc05QTDlhRVQ6YXRGMjJ4ZFVTQm12NEp1UzU5SVNrZw=="
df = pd.read_excel("./ChatBot_Extract_Intent/data/23-6.xlsx")

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

def init_elastic(df, index_name,ELASTIC_CLOUD_ID,ELASTIC_API_KEY):
    # Create the client instance
    client = Elasticsearch(
    # For local development
    # hosts=["http://localhost:9200"]
    cloud_id=ELASTIC_CLOUD_ID,
    api_key=ELASTIC_API_KEY,
    )

    # Define the mappings
    mappings = {
        "properties": {
            "PRODUCT_INFO_ID": {"type": "text"},
            "LINK_SP": {"type" : "text"},
            "GROUP_PRODUCT_ID": {"type": "keyword"},
            "GROUP_PRODUCT_NAME": {"type": "text"},
            "PRODUCT_NAME" : {"type": "text"},
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
                "LINK_SP": row["LINK_SP"],
                "GROUP_PRODUCT_ID": row["GROUP_PRODUCT_ID"],
                "GROUP_PRODUCT_NAME": row["GROUP_PRODUCT_NAME"],
                "PRODUCT_NAME": row["PRODUCT_NAME"],
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
# input_text = "Robot"

def find_closest_match(input_str):
    list_product = ['Bàn là', 'Bình nước nóng', 'Bình đun nước',
       'Bếp từ', 'Công tắc, ổ cắm thông minh', 'Ghế massage daikiosan',
       'Lò vi sóng', 'Máy Giặt', 'Máy Sấy',
       'Máy lọc không khí', 'Máy lọc không khí, máy hút bụi',
       'Máy lọc nước', 'Máy xay', 'Nồi chiên không dầu', 'Nồi cơm điện',
       'Nồi áp suất', 'Robot hút bụi', 'Thiết bị Camera',
       'Thiết bị Webcam', 'Thiết bị Wifi', 'thiết bị gia dụng',
       'Điều hòa', 'Đèn Năng Lượng Mặt Trời']
    match = process.extractOne(input_str, list_product, scorer=fuzz.partial_ratio)

    # Check if the match is sufficiently close
    try:
      print(f"Có phải bạn tìm kiếm sản phẩm {match[0]}")
      if match[1] >= 80:
        return match[0]
    except Exception as e:
      print(f"Error searching for {input_str}: {e}")

def search_products(client, index_name, product_name=None, value=None, power=None, weight=None, volume=None):
    # Build the base query
    product = find_closest_match(product_name)
    print("check_product", product)
    # Create the Elasticsearch query if a product is found
    if product:
        query = {
              "query": {
                  "bool": {
                      "must": [
                          {
                              "match": {
                                  "GROUP_PRODUCT_ID": product
                              }
                          }
                      ]
                  }
                  },
              "size": 10
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
        # print("check search product", res)
    except Exception as e:
        print(f"Error searching for {product_name}: {e}")
    return res

def search_intent(client, index_name, product_name, intent, value):

    product = find_closest_match(product_name)
    print("check_product", product)

    order = "asc"  # Default order
    cheap_keywords = ["rẻ", "giá rẻ", "giá thấp", "bình dân", "tiết kiệm", "khuyến mãi", "giảm giá", "hạ giá", "giá cả phải chăng", "ưu đãi"]
    expensive_keywords = ["giá đắt", "giá cao", "xa xỉ", "sang trọng", "cao cấp", "đắt đỏ", "chất lượng cao", "hàng hiệu", "hàng cao cấp", "thượng hạng"]
    intent_user = cheap_keywords + expensive_keywords
    order = None
    for keyword in cheap_keywords:
        if keyword in intent.lower():
            order = "asc"
    for keyword in expensive_keywords:
        if keyword in intent.lower():
            order = "desc"

    if intent in intent_user:
      print("check intent price", intent)
      query = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "match": {
                                "GROUP_PRODUCT_ID": product
                            }
                        },
                        {
                            "match": {
                                "GROUP_PRODUCT_NAME": product_name
                            }
                        }
                    ]
                }
            },
            "sort": [
                {"RAW_PRICE": {"order": order}}
            ],
            "size": 10
        }

    else:
      print("check intent not price", intent)
      query = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "match": {
                                "GROUP_PRODUCT_ID": product
                            }
                        },
                        {
                            "match": {
                                "GROUP_PRODUCT_NAME": product_name
                            }
                        },
                        {
                            "match": {
                                "SPECIFICATION_BACKUP": intent
                            }
                        }
                    ]
                }
                },
            "size": 10
        }
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

        # Execute the search query
    try:
        response = client.search(index=index_name, body=query)
        return response
    except Exception as e:
        print(f"Error executing search: {e}")

def search_db(command):
    demands = extract_info(command)
    print(demands)
    product_names = demands['object']
    values = [demands['value']]
    power = demands['power']
    weight = demands['weight']
    volume = demands['volume']
    intent = demands['intent']
    index_name = "test2"
    client = init_elastic(df,index_name, ELASTIC_CLOUD_ID,ELASTIC_API_KEY)
    
    if product_names == []:
        out_text = "bạn có thể cho tôi biết tên sản phẩm cụ thể bạn quan tâm để tôi có thể hỗ trợ bạn được không?"
        return 0
    result = []
    t1 = time.time()
    ok = 0
    if values == "":
        values = [None]*len(product_names)
    # print("check_values", values)
    for product_name, value in zip(product_names, values):
    # for product_name in product_names:
        print("check demands", product_name)
        if intent:
            resp = search_intent(client, index_name, product_name, intent, value)
            print(resp)
            ok = 1
        else:
            resp = search_products(client, index_name, product_name, value, power, weight, volume)
        result.append(resp)

    print(result)
    # result
    out_text = ""
    k = 1
    for product_name, product in zip(product_names, result):
        out_text += f"\n{k}. Với sản phẩm {product_name}:\n"
        k += 1
        
        try:
            for i, hit in enumerate(product['hits']['hits']):           
                check_score = hit.get('_score')
                product_details = hit['_source']
                print(check_score)
                
                if (check_score is None or (float(check_score) >= 9 and i < 10) and ok == 0):
                    out_text += f"{i + 1}. {product_details['PRODUCT_NAME']}\n"
                    out_text += f"Giá tiền: {product_details['RAW_PRICE']} VND\n"
                elif check_score is None or (float(check_score) >= 9 and i < 3):
                    out_text += f"\n{i + 1}. {product_details['PRODUCT_NAME']}\n"
                    out_text += f"Thông số kỹ thuật: {product_details['SPECIFICATION_BACKUP']}\n"
                # else:
                #     raise Exception ("Bạn có thể cho tôi biết thông số kỹ thuật cụ thể bạn quan tâm để tôi có thể hỗ trợ bạn được không?")
        
        except Exception as e:
            out_text += f"Đã xảy ra lỗi khi xử lý sản phẩm {product_name}: {str(e)}\n"

    print("Time search elastic", time.time() - t1)
    return out_text

# print(search_db("Tôi muốn mua điều hòa co gia khuyen mai"))
# print(df)