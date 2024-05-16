import os,re
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts.few_shot import FewShotPromptTemplate
from langchain.prompts.prompt import PromptTemplate
from ChatBot_Extract_Intent.config_app.config import get_config
from langchain.chains import LLMChain
from difflib import get_close_matches
import csv
from ChatBot_Extract_Intent.extract_price_info import take_product
import random
import pandas as pd

config_app = get_config()

os.environ['OPENAI_API_KEY'] = config_app["parameter"]["openai_api_key"]
llm = ChatOpenAI(model_name=config_app["parameter"]["gpt_model_to_use"], temperature=config_app["parameter"]["temperature"])

path=config_app['parameter']['data_private']
df = pd.read_excel(path)
df = df.fillna(0)

with open('ChatBot_Extract_Intent/data/product_final_204_oke.xlsx - Sheet1.csv', 'r') as file:
    reader = csv.DictReader(file)
    data = list(reader)

def split_sentences(text_input):
    examples = config_app['parameter']['example_input']

    example_formatter_template = """
        Input command from user: {command}
        The information extracted from above command:\n
        command: {command}\n
        demand: {demand}\n
        object:  {object}\n
        value: {value}
    """

    example_prompt = PromptTemplate(
        input_variables=["command", "demand","object", "value"],
        template=example_formatter_template,
    )

    few_shot_prompt = FewShotPromptTemplate(
        # These are the examples we want to insert into the prompt.
        examples=examples,
        # This is how we want to format the examples when we insert them into the prompt.
        example_prompt=example_prompt,
        # The prefix is some text that goes before the examples in the prompt.
        # Usually, this consists of intructions.
        prefix="Extract detailed information for customer needs. Returns the corresponding object. Here are some examples:",
        # The suffix is some text that goes after the examples in the prompt.
        # Usually, this is where the user input will go
        suffix="Input command from user: {command}\nThe information extracted from above command::",
        # The input variables are the variables that the overall prompt expects.
        input_variables=["command"],
        # The example_separator is the string we will use to join the prefix, examples, and suffix together with.
        example_separator="\n\n",
    )

    # print(few_shot_prompt.format(command="Mua đèn năng lượng mặt trời giá 15 triệu"))

    chain = LLMChain(llm=llm, prompt=few_shot_prompt)

    return chain.run(command=text_input)



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

# Hàm xử lý yêu cầu
def process_command(demands,list_product):
    print('======process_command======')
    lst_mua = ['mua','quan tâm','giá','tìm','thích','bán']
    lst_so_luong = ['số lượng','bao nhiêu','mấy loại']
    # demands = extract_info(command)
    print("info:",demands)
    
    # if ((demands['demand'].lower() in lst_mua) and len(demands['value']) >= 1) or (len(demands['value']) >= 1 and len(demands['object']) > 0 and len(demands['demand']) == 0):
    #     return [0, handle_buy(demands)]
    # elif (demands['demand'].lower() in lst_mua) and len(demands['value']) == 0:
    #     return handle_interest(demands)
    # elif demands['demand'].lower() in lst_so_luong:
    #     return handle_count(demands)
    if (demands['demand'].lower() in lst_mua) and len(demands['value']) >= 1:
        return [0, handle_buy(demands)]
    elif (demands['demand'].lower() in lst_mua) and len(demands['value']) == 0:
        return [0, handle_interest(demands)]
    elif demands['demand'].lower() in lst_so_luong:
        return [0, handle_count(demands)]
    else:
        return handle_tskt(demands, list_product)


def handle_buy(demands):
    print('======handle_buy======')
    # Xử lý yêu cầu
    matching_products = []
    for product in data:
        product_name = product['PRODUCT_NAME'].lower()
        group_name = product['GROUP_PRODUCT_NAME'].lower()
        specifications = re.sub(r'[^a-zA-Z0-9]', '', product['SPECIFICATION_BACKUP'].lower())
        if any(obj.lower() in group_name for obj in demands["object"]) and re.sub(r'[^a-zA-Z0-9]', '', demands["value"].lower()) in specifications:
            matching_products.append(product)

    # Trả kết quả vào một chuỗi
    result_string = ""
    if matching_products:
        result_string += f"{demands['demand'].capitalize()} {', '.join(demands['object'])} từ {demands['value'].title()} tìm thấy:\n"
        for product in matching_products[:config_app['parameter']['num_product']]:  # Chỉ lấy 5 sản phẩm đầu tiên
            result_string += f"- {product['PRODUCT_NAME']} - Giá: {product['RAW_PRICE']} VNĐ\n"
            result_string += f"  Thông số kỹ thuật: {product['SPECIFICATION_BACKUP']}\n"
    else:
        # Tìm các giá trị gần đúng với "value" trong cột SPECIFICATIONS_BACKUP
        value_possibilities = set(re.sub(r'[^a-zA-Z0-9]', '', product['SPECIFICATION_BACKUP'].lower()) for product in data)
        close_matches = get_close_matches(re.sub(r'[^a-zA-Z0-9]', '', demands["value"].lower()), value_possibilities)
        
        if close_matches:
            result_string += f"Không tìm thấy {' '.join(demands['object'])} từ {demands['value'].title()} trong dữ liệu.\n"
            result_string += f"Có thể bạn muốn tìm kiếm:\n"
            for match in close_matches:
                result_string += f"- {' '.join(demands['object'])} {match.title()}\n"
        else:
            # result_string += f"Không tìm thấy {' '.join(demands['object'])} từ {demands['value'].title()} trong dữ liệu."
            result_string = take_product(demands)
    return result_string

def handle_interest(demands):
    print('======handle_interest======')
    # Xử lý yêu cầu quan tâm đến sản phẩm với giá trị cụ thể
    found_products = {}
    for product in data:
        product_name = product['PRODUCT_NAME'].lower()
        group_name = product['GROUP_PRODUCT_NAME'].lower()
        for keyword in demands['object']:
            if f" {keyword} " in f" {product_name} " or f" {keyword} " in f" {group_name} ":
                if keyword not in found_products:
                    found_products[keyword] = []
                found_products[keyword].append(product)

    # Tạo chuỗi kết quả tìm kiếm
    result_string = ""
    for keyword in demands['object']:
        if keyword in found_products:
            result_string += f"Sản phẩm '{keyword}' tìm thấy:\n"
            if found_products[keyword]:
                for product in found_products[keyword][:config_app['parameter']['num_product']]:  # In ra 3 sản phẩm đầu tiên
                    result_string += f"- {product['PRODUCT_NAME']} - Giá: {product['RAW_PRICE']}\n"
                    specifications = product['SPECIFICATION_BACKUP'].split('\n')
                    result_string += "  Thông số kỹ thuật:\n"
                    for spec in specifications[:5]:  # In ra 5 dòng đầu tiên của thông số kỹ thuật
                        result_string += f"    {spec}\n"
            else:
                result_string += f"- Rất tiếc, không có thông tin sản phẩm {keyword} nào trong dữ liệu của tôi.\n"
        else:
            result_string += f"Không tìm thấy sản phẩm '{keyword}'.\n"

    return result_string


def handle_count(demands):
    print('======handle_count======')
    # Xử lý yêu cầu về số lượng sản phẩm
    matching_products = []
    for product in data:
        group_name = product['GROUP_PRODUCT_NAME'].lower()
        if any(demands["object"][0].lower() in group_name for obj in demands["object"]):
            if demands["value"]:
                specifications = re.sub(r'[^a-zA-Z0-9]', '', product['SPECIFICATION_BACKUP'].lower())
                if re.sub(r'[^a-zA-Z0-9]', '', demands["value"].lower()) in specifications:
                    matching_products.append(product)
            else:
                matching_products.append(product)


    # Trả kết quả vào một chuỗi
    result_string = ""
    if matching_products:
        result_string += f"Số lượng {', '.join(demands['object'])} {demands['value']}: {len(matching_products)} sản phẩm\n"
    else:
        # Tìm các giá trị gần đúng với "value" trong cột SPECIFICATION_BACKUP
        value_possibilities = set(re.sub(r'[^a-zA-Z0-9]', '', product['SPECIFICATION_BACKUP'].lower()) for product in data)
        close_matches = get_close_matches(re.sub(r'[^a-zA-Z0-9]', '', demands["value"].lower()), value_possibilities)

        if close_matches:
            result_string += f"Không tìm thấy {' '.join(demands['object'])} {demands['value']} trong dữ liệu.\n"
            result_string += f"Có thể bạn muốn tìm kiếm:\n"
            for match in close_matches:
                result_string += f"- {' '.join(demands['object'])} {match.title()}\n"
        else:
            result_string += f"Không tìm thấy {' '.join(demands['object'])} {demands['value']} trong dữ liệu."

    return result_string

# Lấy 3 phần tử đầu tiên trong list_product
def take_top3_product(demands, list_product):
    print('======take_top3_product======')
    result_string = ''
    for name_product in demands['object']:
        result_string += f"Sản phẩm '{name_product}' tìm thấy:\n"
        for product in list_product[name_product][:3]:
            result_string += f"- {product['PRODUCT_NAME']} - Giá: {product['RAW_PRICE']} - Số lượng đã bán: {product['QUANTITY_SOLD']}\n"
            specifications = product['SPECIFICATION_BACKUP'].split('\n')
            result_string += "  Thông số kỹ thuật:\n"
            for spec in specifications[:5]:  # In ra 5 dòng đầu tiên của thông số kỹ thuật
                result_string += f"    {spec}\n"
    return result_string

def handle_tskt(demands, list_product):
    # Xử lý yêu cầu tskt sản phẩm
    print('======handle_tskt======')
    lst_compare = ['so sánh','tốt hơn']

    if demands['value'] == '':
        for i in list_product:
            if len(list_product[i]) > 1:
                return [0,"Tôi cần tên cụ thể của  " + list_product[i][1]]
        if demands['demand'].lower() in lst_compare:
            return [1, take_top3_product(demands, list_product)]
        else:
            return [0, take_top3_product(demands, list_product)]
    else:
        result_string = ''
        for name_product in demands['object']:
            cnt = 0
            for product in list_product[name_product]:
                if demands['value'].lower() in product['SPECIFICATION_BACKUP'].lower():
                    if cnt == 0:
                        result_string += f"Sản phẩm '{name_product}' tìm thấy:\n"
                    result_string += f"- {product['PRODUCT_NAME']} - Giá: {product['RAW_PRICE']} - Số lượng đã bán: {product['QUANTITY_SOLD']}\n"
                    specifications = product['SPECIFICATION_BACKUP'].split('\n')
                    result_string += "  Thông số kỹ thuật:\n"
                    for spec in specifications[:5]:  # In ra 5 dòng đầu tiên của thông số kỹ thuật
                        result_string += f"    {spec}\n"
                    cnt += 1
                    if cnt == 3:
                        break
            if cnt == 0:
                return [1, take_top3_product(demands, list_product)]
        if demands['demand'].lower() in lst_compare:
            return [1, result_string]
        else:
            return [0, result_string]


def take_db(demands):
    print('======take_db======')
    list_product = {}
    print('demands:',demands)
    for name_product in demands['object']:
        product = []
        check_group = True

        # Find product by product name
        for index, row in df.iterrows():
            if name_product.lower() not in row['GROUP_PRODUCT_NAME'].lower() and name_product.lower() in row['PRODUCT_NAME'].lower():
                if name_product not in list_product:
                    list_product[name_product] = []
                list_product[name_product].append({'LINK_SP' : row['LINK_SP'],
                                                   'GROUP_PRODUCT_NAME' : row['GROUP_PRODUCT_NAME'],
                                                   'SPECIFICATION_BACKUP' : row['SPECIFICATION_BACKUP'],
                                                   'PRODUCT_NAME' : row['PRODUCT_NAME'],
                                                   'RAW_PRICE' : row['RAW_PRICE'],
                                                   'QUANTITY_SOLD' : row['QUANTITY_SOLD']})
                check_group = False
                break
        if not check_group:
            continue

        # Find product by group product name
        for index, row in df.iterrows():
            if name_product.lower() in row['GROUP_PRODUCT_NAME'].lower():
                if name_product not in list_product:
                    list_product[name_product] = []
                
                list_product[name_product].append({'LINK_SP' : row['LINK_SP'],
                                                   'GROUP_PRODUCT_NAME' : row['GROUP_PRODUCT_NAME'],
                                                   'SPECIFICATION_BACKUP' : row['SPECIFICATION_BACKUP'],
                                                   'PRODUCT_NAME' : row['PRODUCT_NAME'],
                                                   'RAW_PRICE' : row['RAW_PRICE'],
                                                   'QUANTITY_SOLD' : row['QUANTITY_SOLD']})
    # sort product from highest price to lowest
    def QUANTITY_SOLD_sort(s):
        return s['QUANTITY_SOLD']
    for i in list_product:
        list_product[i] = sorted(list_product[i], key = QUANTITY_SOLD_sort, reverse=True)
    
    return list_product

def search_db(command):
    '''
    0: return product
    1: return product for bot
    '''
    print('======search_db======')
    # If don't have object return type 0
    demands = extract_info(command)
    if demands['object'] == "":
        return [0, 'Bạn có thể cung cấp cho tôi tên của sản phẩm bạn muốn tìm hiểu không?']

    # take data from db
    list_product = take_db(demands)

    for name_product in demands['object']:
        if name_product not in list_product:
            return [0, "Xin lỗi vì hiện tại tôi chưa hiểu rõ nhu cầu của bạn về {}. Liệu bạn có thể cho tôi biết tên sản phẩm cụ thể bạn quan tâm để tôi có thể hỗ trợ bạn được không?".format(name_product)]
    
    if demands['demand'] == "" or demands['value'] == 'chạy nhất':
        type = 'SPECIFICATION_BACKUP' # 2: SPECIFICATION_BACKUP, default
        list_type = [
            ['RAW_PRICE', 'trieu', 'nghin'], # 4: RAW_PRICE
            ['QUANTITY_SOLD', 'ban chay nhat', 'nhieu luot mua', 'pho bien nhat','chay nhat'] # 5: QUANTITY_SOLD
        ]
        # Find type of demand
        for i in list_type:
            for j in range(1,len(i)):
                if i[j] in demands['value']:
                    type = j[0]
        # result = []
        if type == 'RAW_PRICE':
            return [1, take_product(demands['command'])]
        
        return [1,take_top3_product(demands, list_product)]
    else:
        
        return process_command(demands, list_product)