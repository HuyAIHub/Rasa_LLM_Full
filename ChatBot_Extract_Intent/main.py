
import os,re
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts.few_shot import FewShotPromptTemplate
from langchain.prompts.prompt import PromptTemplate
from ChatBot_Extract_Intent.config_app.config import get_config
from langchain.chains import LLMChain
from difflib import get_close_matches
import csv
from ChatBot_Extract_Intent.extract_price_info import take_product
from chat import predict_rasa_llm
import random

config_app = get_config()

os.environ['OPENAI_API_KEY'] = config_app["parameter"]["openai_api_key"]
llm = ChatOpenAI(model_name=config_app["parameter"]["gpt_model_to_use"], temperature=config_app["parameter"]["temperature"])

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
def process_command(command,IdRequest,NameBot,User):
    lst_mua = ['mua','quan tâm','tìm','thích','bán']
    lst_so_luong = ['số lượng','bao nhiêu','mấy loại']
    demands = extract_info(command)
    print("info:",demands)
    
    if ((demands['demand'].lower() in lst_mua) and len(demands['value']) >= 1) or (len(demands['value']) >= 1 and len(demands['object']) > 0 and len(demands['demand']) == 0):
        return handle_buy(demands)
    elif (demands['demand'].lower() in lst_mua) and len(demands['value']) == 0:
        return handle_interest(demands)
    elif demands['demand'].lower() in lst_so_luong:
        return handle_count(demands)
    elif demands['object'] == '':
        random_number = random.randint(0, 1)
        return config_app['parameter']['raw_answer'][random_number]
    # elif demands['demand'].lower() == 'loại':
    #     return handle_type(demands)
    # elif demands['demand'].lower() == 'bảo hành':
    #     return handle_warranty(demands)
    # elif demands['demand'].lower() == 'thời gian sử dụng trung bình':
    #     return handle_average_usage(demands)
    # elif demands['demand'].lower() == 'tốt hơn':
    #     return handle_better(demands)
    else:
        return predict_rasa_llm(demands["command"],IdRequest,NameBot,User,type='llm')


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

def handle_sale(demands):
    # Xử lý yêu cầu về sản phẩm bán chạy
    pass

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

def handle_power(demands):
    # Xử lý yêu cầu về công suất của sản phẩm
    pass

def handle_type(demands):
    # Xử lý yêu cầu về loại sản phẩm phổ biến
    pass

def handle_warranty(demands):
    # Xử lý yêu cầu về thời gian bảo hành
    pass

def handle_average_usage(demands):
    # Xử lý yêu cầu về thời gian sử dụng trung bình
    pass

def handle_better(objects):
    # Xử lý yêu cầu so sánh sản phẩm
    pass
