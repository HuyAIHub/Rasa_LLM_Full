import pandas as pd
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import os,re
# Địa chỉ của Elasticsearch của bạn, mặc định là http://localhost:9200
ELASTIC_HOST = "http://10.248.243.105:9200"

# Tạo client Elasticsearch
client = Elasticsearch(hosts=[ELASTIC_HOST])

# # Đường dẫn đến file Excel của bạn
# excel_file = "/data/Production/Rasa_LLM_Full/ChatBot_Extract_Intent/data/product_final_204_oke.xlsx"

# # Đọc dữ liệu từ file Excel vào DataFrame của Pandas
# df = pd.read_excel(excel_file)
# df = df.fillna('')
# # Chuyển đổi DataFrame thành dạng JSON để lưu vào Elasticsearch
# json_data = df.to_dict(orient="records")

# # Tạo index trong Elasticsearch (nếu cần)
# index_name = "test"
# if not client.indices.exists(index=index_name):
#     client.indices.create(index=index_name)

# # Lưu trữ dữ liệu vào Elasticsearch
# for data in json_data:
#     client.index(index=index_name, body=data)

df = pd.read_csv("/data/Production/Rasa_LLM_Full_luan/product_final_204204.csv")
df1 = df.copy()
df1['GROUP_PRODUCT_NAME'] = df1['GROUP_PRODUCT_NAME'].str.cat(df1['PRODUCT_NAME'], sep=' , ').str.lower()

def get_embedding(text, model="text-embedding-ada-002"):
   text = text.replace("\n", " ")
   return client.embeddings.create(input = [text], model=model).data[0].embedding

def init_elastic(embedding_df, index_name, hosts):
    es = Elasticsearch(hosts=[ELASTIC_HOST])

    # Define the mappings
    indexMapping={
        "properties":{
            "PRODUCT_INFO_ID": {"type": "text"},
            "GROUP_PRODUCT_NAME": {"type": "text"},
            "GROUP_PRODUCT_NAME_vector": {
                "type":"dense_vector",
                "dims": 1536,
                "index":True,
                "similarity": "cosine"},
            "SPECIFICATION_BACKUP": {"type": "text"},
            "POWER": {"type": "float"},
            "WEIGHT": {"type": "float"},
            "VOLUME": {"type": "float"},
            "RAW_PRICE": {"type": "integer"}
        }
    }


    # Create the index with mappings
    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name, mappings=indexMapping)
        # Index documents
        embedding_df['GROUP_PRODUCT_NAME_vector'] = embedding_df.GROUP_PRODUCT_NAME_vector.apply(eval).apply(np.array)
        docs = embedding_df.to_dict("records")
        print(docs)
        for doc in docs:
            try:
                es.index(index=index_name, document=doc, id=doc["PRODUCT_INFO_ID"])
            except Exception as e:
                print(e)
                print(f"Index {index_name} created.")
    else:
        print(f"Index {index_name} already exists.")

    return es

def parse_price_range(value):
    pattern = r"(?P<prefix>\b(dưới|trên|từ|đến|khoảng)\s*)?(?P<number>\d+(?:,\d+)*)\s*(?P<unit>triệu|nghìn|tr|k|kg|l|lít|W|w)?\b"

    min_price = 0
    max_price = 10000000
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

def search_products(client, index_name, product_name=None, value=None, power=None, weight=None, volume=None, intent=None):
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
    # if intent == 'cheepest':
    #   cheapest_sort = [
    #       {"RAW_PRICE": {"order": "asc"}}
    #   ]
    #   query["sort"] = cheapest_sort
    #   query["size"] = 5
    # Execute the search query
    try:
        res = client.search(index=index_name, body=query)
        return res
    except Exception as e:
        print(f"Error searching for {product_name}: {e}")
    return res
    



