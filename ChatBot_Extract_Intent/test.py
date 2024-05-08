
import os
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts.few_shot import FewShotPromptTemplate
from langchain.prompts.prompt import PromptTemplate
from config_app.config import get_config
from langchain.chains import LLMChain
from difflib import get_close_matches
import csv

config_app = get_config()

os.environ['OPENAI_API_KEY'] = config_app["parameter"]["openai_api_key"]
llm = ChatOpenAI(model_name=config_app["parameter"]["gpt_model_to_use"], temperature=config_app["parameter"]["temperature"])

with open('data/product_final_204_oke.xlsx - Sheet1.csv', 'r') as file:
    reader = csv.DictReader(file)
    data = list(reader)

def split_sentences(text_input):
    examples = [
        {
            "command":"Tôi quan tâm tới sản phẩm điều hòa và Thiết bị Wifi",
            "demand":"quan tâm",
            "object": ["điều hòa", "Thiết bị Wifi"],
            "value":"",
        },
        {
            "command":"Tôi quan tâm tới sản phẩm điều hòa, máy giặt",
            "demand":"quan tâm",
            "object": ["điều hòa","máy giặt"],
            "value":"",
        },
        {
            "command":"Tôi quan tâm máy giặt lồng ngang",
            "demand":"quan tâm",
            "object": ["máy giặt"],
            "value":"lồng ngang",
        },
        {
            "command":"Tôi quan tâm tới sản phẩm điều hòa giá trên 10 triệu",
            "demand":"giá",
            "object": ["điều hòa"],
            "value":"trên 10 triệu",
        },
        {
            "command":"số lượng sản phẩm đèn năng lượng mặt trời",
            "demand":"số lượng",
            "object":["đèn năng lượng mặt trời"],
            "value":"",
        },
         {
            "command": "Số lượng sản phẩm điều hòa 2 chiều",
            "demand": "Số lượng",
            "object": ["điều hòa"],
            "value": "2 chiều"
        },
        {
            "command": "có bao nhiêu điều hòa 2 chiều",
            "demand": "bao nhiêu",
            "object": ["điều hòa"],
            "value": "2 chiều"
        },
        {
            "command":"Sản phẩm bếp từ nào bán chạy nhất",
            "demand":"bán",
            "object":["bếp từ"],
            "value":"chạy nhất",
        },
        {
            "command":"Sản phẩm bán chạy nhất là sản phẩm nào?",
            "demand":"bán",
            "object":[],
            "value":"chạy nhất",

        },
        {
            "command":"Bếp từ nào có công suất lớn nhất",
            "demand":"công suất",
            "object":["bếp từ"],
            "value":"lớn nhất",
        },
        {
            "command":"xin chào",
            "demand":"",
            "object":[],
            "value":"",
        },
        {
            "command":"so sánh điều hòa daikin và điều hòa LG tầm giá 10tr",
            "demand":"so sánh",
            "object":["điều hòa daikin","điều hòa LG"],
            "value":"10tr",
        },
        {
            "command":"bình đun nước có công suất trên 1000w",
            "demand":"công suất",
            "object":["bình đun nước"],
            "value":"trên 1000w",
        },
        {
            "command":"máy giặt có giá dưới 10 triệu",
            "demand":"giá",
            "object":["máy giặt"],
            "value":"dưới 10,000,000",
        },
        {
            "command":"Máy Giặt Aqua 9 Kg AQW-F91GT.S là lồng ngang hay lồng đứng",
            "demand":"",
            "object":["Máy Giặt Aqua 9 Kg AQW-F91GT.S"],
            "value":"lồng ngang hay lồng đứng",
        },
        {
            "command":"tôi muốn mua máy giặt lồng ngang",
            "demand":"mua",
            "object":["Máy Giặt"],
            "value":"lồng ngang",
        },
        {
            "command":"Máy lọc nước Karofi KAQ-U06V và Máy lọc nước Empire Nóng Nguội - 10 cấp lọc EPML038 cái nào tốt hơn?",
            "demand":"tốt hơn",
            "object":["Máy lọc nước Karofi KAQ-U06V", "Máy lọc nước Empire Nóng Nguội - 10 cấp lọc EPML038"],
            "value":"",
        },
        {
            "command":"Quạt sưởi không khí AIO Smart bảo hành trong bao lâu?",
            "demand":"bảo hành",
            "object":["Quạt sưởi không khí AIO Smart"],
            "value":"",
        },
        {
            "command":"Quạt sưởi không khí AIO Smart bảo hành trong bao lâu?",
            "demand":"bảo hành",
            "object":["Quạt sưởi không khí AIO Smart"],
            "value":"",
        },
        {
            "command": "Loại máy giặt nào là phổ biến nhất hiện nay?",
            "demand": "Loại",
            "object": ["máy giặt"],
            "value": "phổ biến nhất",
        },
        {
            "command": "máy giặt phổ biến nhất hiện nay là loại nào?",
            "demand": "Loại",
            "object": ["máy giặt"],
            "value": "phổ biến nhất",
        },
        {
            "command": "Thời gian sử dụng trung bình của Ghế massage daikiosan là bao lâu?",
            "demand": "Thời gian sử dụng trung bình",
            "object": ["Ghế massage daikiosan"],
            "value": "",
        }
    ]

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
def process_command(command):
    lst_mua = ['mua','quan tâm','tìm','thích','bán']
    lst_so_luong = ['số lượng','bao nhiêu']
    demands = extract_info(command)
    print("info:",demands)
    
    if (demands['demand'].lower() in lst_mua) and len(demands['value']) >= 1:
        return handle_buy(demands)
    elif (demands['demand'].lower() in lst_mua) and len(demands['value']) == 0:
        return handle_interest(demands)
    elif demands['demand'].lower() in lst_so_luong:
        return handle_count(demands)
    # elif demands['demand'].lower() == 'công suất':
    #     return handle_power(demands)
    elif demands['demand'].lower() == 'giá': # x
        return handle_price(demands)
    elif demands['demand'].lower() == 'loại':
        return handle_type(demands)
    elif demands['demand'].lower() == 'bảo hành':
        return handle_warranty(demands)
    elif demands['demand'].lower() == 'thời gian sử dụng trung bình':
        return handle_average_usage(demands)
    elif demands['demand'].lower() == 'tốt hơn':
        return handle_better(demands)
    else:
        return "Xin lỗi, tôi không hiểu yêu cầu của bạn."

# Các hàm xử lý cụ thể
import re
def handle_buy(demands):
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
        for product in matching_products:
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
            result_string = handle_price(demands)
    return result_string

def handle_interest(demands):
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
                for product in found_products[keyword][:3]:  # In ra 3 sản phẩm đầu tiên
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
def parse_price_range(value):
    pattern = r"(?P<prefix>\b(dưới|trên|từ|đến|khoảng)\s*)?(?P<number>\d+(?:,\d+)*)\s*(?P<unit>triệu|nghìn)?\b"

    min_price = 0
    max_price = float('inf')

    for match in re.finditer(pattern, value, re.IGNORECASE):
        prefix = match.group('prefix') or ''
        number = float(match.group('number').replace(',', ''))
        unit = match.group('unit') or ''

        if unit.lower() == 'triệu':
            number *= 1000000
        elif unit.lower() == 'nghìn':
            number *= 1000

        if prefix.lower().strip() == 'dưới':
            max_price = min(max_price, number)
        elif prefix.lower().strip() == 'trên':
            min_price = min(max_price, number)
        elif prefix.lower().strip() in ('từ', 'khoảng'):
            min_price = min(max_price, number)
        elif prefix.lower().strip() == 'đến':
            max_price = max(min_price, number)
        else:  # Trường hợp không có từ khóa
            min_price = min(min_price, number * 0.9)
            max_price = max(max_price, number * 1.1)

    if min_price == float('inf'):
        min_price = 0
    return min_price, max_price

def handle_price(demands):
    # Xử lý yêu cầu về giá của sản phẩm
        # Xử lý yêu cầu
    matching_products = []
    # if demands["demand"] == "giá":
    for product in data:
        group_name = product['GROUP_PRODUCT_NAME'].lower()
        if any(obj.lower() in group_name for obj in demands["object"]):
            raw_price_str = re.sub(r'[^0-9,]', '', product['RAW_PRICE'])
            raw_price = float(raw_price_str.replace(',', ''))
            min_price, max_price = parse_price_range(demands["value"].lower())
            if min_price <= raw_price <= max_price:
                matching_products.append(product)
    # else:
    #     return "Câu hỏi không liên quan đến giá sản phẩm."

    # Trả kết quả vào một chuỗi
    result_string = ""
    if matching_products:
        result_string += f"{demands['object'][0].title()} {demands['value']} tìm thấy:\n"
        for product in matching_products:
            result_string += f"- {product['PRODUCT_NAME']} - Giá: {product['RAW_PRICE']} VNĐ\n"
    else:
        result_string += f"Không tìm thấy {demands['object'][0]} {demands['value']} trong dữ liệu."

    return result_string

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

# Ví dụ sử dụng
#1
# command = "tôi muốn mua máy giặt lồng ngang"
# command = "tôi quan tâm máy lọc không khí công suất 30w"
# command = "tôi muốn tìm máy lọc không khí công suất 30w"
#2
# command = "tôi muốn tìm máy lọc không khí và điều hòa"
# command = "Bên bạn có bán đèn năng lượng mặt trời không?"
# 3
# command = 'Số lượng sản phẩm điều hòa 2 chiều'
# command = 'Số lượng đèn năng lượng mặt trời'
# command = 'Số lượng đèn năng lượng mặt trời dung lượng pin 16000'
# command = 'có bao nhiêu sản phẩm điều hòa 2 chiều'
# 4 
# command = 'Tôi muốn mua sản phẩm điều hòa dưới 10 triệu'
# command = 'Tôi muốn mua sản phẩm máy giặt có giá dưới 10 triệu 500 nghìn'
# command = 'Tôi muốn mua sản phẩm máy giặt có giá từ 5 triệu đến 8 triệu'
# command = 'Tôi muốn mua sản phẩm máy giặt có giá khoảng 10 triệu'
# command = 'Tôi muốn mua sản phẩm máy giặt lồng ngang có giá trên 10 triệu'  #=> fail
# 5

command = 'Tôi muốn mua sản phẩm máy giặt lồng ngang'  #=> fail


result = process_command(command)

print(result)