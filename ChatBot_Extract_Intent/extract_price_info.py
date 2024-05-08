import os, re
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts.few_shot import FewShotPromptTemplate
from langchain.prompts.prompt import PromptTemplate
from ChatBot_Extract_Intent.config_app.config import get_config
from langchain.chains import LLMChain
import time
import pandas as pd

config_app = get_config()

os.environ['OPENAI_API_KEY'] = config_app["parameter"]["openai_api_key"]
llm = ChatOpenAI(model_name=config_app["parameter"]["gpt_model_to_use"], temperature=config_app["parameter"]["temperature"])
path = config_app['parameter']['data_private']
data = pd.read_excel(path)
data = data.fillna(0)
def split_sentences(text_input):
    # First, create the list of few shot examples.
    examples = [
        {
            "command":"Tôi muốn mua hai chiếc máy lọc không khí giá 5 triệu",
            "object": ["Tôi muốn mua hai chiếc máy lọc không khí giá 5 triệu"],
        },
        {
            "command": "Tôi muốn mua tủ lạnh tầm 600 nghìn và bếp từ 1 triệu",
            "object": ["Tôi muốn mua tủ lạnh tầm 600 nghìn", "bếp từ 1 triệu"],
        },
        {
            "command": "Tôi muốn mua nồi cơm điện, máy hút bụi, máy lọc không khí với số tiền từ 8 triệu đến 9 triệu",
            "object": ["Tôi muốn mua nồi cơm điện, máy hút bụi, máy lọc không khí với số tiền từ 8 triệu đến 9 triệu"],
        },
        {
            "command": "Mua lò vi sóng, máy giặt, tủ lạnh với số tiền 10 triệu và giới thiệu giúp tôi sản phẩm điều hòa giá rẻ nhất hiện nay",
            "object": ["Mua lò vi sóng, máy giặt, tủ lạnh với số tiền 10 triệu", "giới thiệu giúp tôi sản phẩm điều hòa giá rẻ nhất hiện nay"],
        },
        {
            "command":"Cho tôi 4 máy lọc không khí giá tầm 20 triệu và 3 tủ lạnh, 5 máy giặt với tổng giá trị 50 triệu",
            "object": ["Cho tôi 4 máy lọc không khí giá tầm 20 triệu", "3 tủ lạnh, 5 máy giặt với tổng giá trị 50 triệu"],
        },
        {
            "command": "Cho tôi 4 máy lọc không khí Daiki với giá tiền phù hợp từ 7 triệu đến 15 triệu và mua nồi cơm điện, nồi chiên không dầu, bếp từ với số tiền khoảng 13,5 triệu",
            "object":["Cho tôi 4 máy lọc không khí Daiki với giá tiền phù hợp từ 7 triệu đến 15 triệu", "mua nồi cơm điện, nồi chiên không dầu, bếp từ với số tiền khoảng 13,5 triệu"],
        },
        {
            "command": "Tôi muốn mua sản phẩm tivi số lượng 3 cái với giá đắt nhất, điều hòa 2 cái với số tiền là 20 triệu",
            "object": ["Tôi muốn mua sản phẩm tivi số lượng 3 cái với giá đắt nhất", "điều hòa 2 cái với số tiền là 20 triệu"],
        },
        {
            "command": "Đèn năng lượng mặt trời giá 15 triệu, nồi cơm điện 4 triệu, máy giặt 10 triệu",
            "object": ["Đèn năng lượng mặt trời giá 15 triệu", "nồi cơm điện 4 triệu", "máy giặt 10 triệu"],
        }
    ]

    example_formatter_template = """
        Input command from user: {command}
        The information extracted from above command:\n
        ----
        {object}
    """

    example_prompt = PromptTemplate(
        input_variables=["command", "object"],
        template=example_formatter_template,
    )

    few_shot_prompt = FewShotPromptTemplate(
        # These are the examples we want to insert into the prompt.
        examples=examples,
        # This is how we want to format the examples when we insert them into the prompt.
        example_prompt=example_prompt,
        # The prefix is some text that goes before the examples in the prompt.
        # Usually, this consists of intructions.
        prefix="Extract detailed information for an input command asking about product price. Return the corresponding object. Below are some examples:",
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

def search_obj_val(text_input):
    # First, create the list of few shot examples.
    examples = [
        {
            "command": "Tôi muốn mua tủ lạnh tầm 600 nghìn",
            "object": ["1 tủ lạnh"],
            "value": ["600 nghìn"],
        },
        {
            "command": "Mua lò vi sóng và máy giặt với số tiền 10 triệu",
            "object": ["1 lò vi sóng", "1 máy giặt"],
            "value": ["10 triệu"],
        },
        {
            "command":"Cho tôi xem các loại nồi cơm điện có giá từ 2 triệu đến 3 triệu đồng",
            "object": ["1 nồi cơm điện"],
            "value": ["2 triệu đến 3 triệu đồng"],
        },
        {
            "command": "Với số tiền 30 triệu tôi mua được ti vi, tủ lạnh ,điều hòa không?" ,
            "object": ["1 ti vi", "1 tủ lạnh", "1 điều hòa"],
            "value": ["30 triệu"],
        },
        {
            "command": "Cho tôi 4 máy lọc không khí Daiki với giá tiền phù hợp từ 7 triệu đến 15 triệu",
            "object":["4 máy lọc không khí"],
            "value": ["7 triệu đến 15 triệu"]
        },
        {
            "command": "Tôi muốn mua sản phẩm tivi số lượng 3 cái, điều hòa 2 cái với số tiền hiện tại tôi có là 20 triệu",
            "object": ["3 tủ lạnh", "2 điều hòa"],
            "value": ["20 triệu"]
        },
        {
            "command": "Đèn năng lượng mặt trời, bếp từ với 15 triệu",
            "object": ["1 Đèn năng lượng mặt trời", "1 bếp từ"],
            "value": ["15 triệu"],
        },
        {
            "command": "Nồi chiên không dầu và điều hòa với 4 triệu",
            "object": ["1 Nồi chiên không dầu",  "1 điều hòa"],
            "value": ["4 triệu"],
        }
    ]

    example_formatter_template = """
        Input command from user: {command}
        The information extracted from above command:\n
        ----
        {object}\n{value}
    """

    example_prompt = PromptTemplate(
        input_variables=["command", "object", "value"],
        template=example_formatter_template,
    )

    few_shot_prompt = FewShotPromptTemplate(
        # These are the examples we want to insert into the prompt.
        examples=examples,
        # This is how we want to format the examples when we insert them into the prompt.
        example_prompt=example_prompt,
        # The prefix is some text that goes before the examples in the prompt.
        # Usually, this consists of intructions.
        prefix="Extract detailed information for an input command asking about product price. Return the corresponding object and value. Below are some examples:",
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

def parse_price_range(value):
    pattern = r"(?P<prefix>\b(dưới|trên|từ|đến|khoảng)\s*)?(?P<number>\d+(?:,\d+)*)\s*(?P<unit>triệu|nghìn|tr|k)?\b"

    min_price = 0
    max_price = float('inf')
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


def find_product(object, value):
    object = object.split(',')

    # change price of product from str to int
    min_price, max_price = parse_price_range(value)

    # take product from DB
    
    list_product = []
    number_product = []
    a = []
    cnt = 0
    for row in data.index:
        for name_product in object:
            name_product = name_product.strip()[1:-1]
            if data['GROUP_PRODUCT_NAME'][row].lower() in name_product.lower() and (row == 0 or data['GROUP_PRODUCT_NAME'][row-1] != data['GROUP_PRODUCT_NAME'][row]):
                a = []
                cnt += 1

                # take the product list
                for row_2 in range(row, data.shape[0]):
                    if data['GROUP_PRODUCT_NAME'][row_2].lower() == data['GROUP_PRODUCT_NAME'][row].lower():
                        a.append([data['PRODUCT_INFO_ID'][row_2], data['PRODUCT_NAME'][row_2], data['RAW_PRICE'][row_2], data['COMMISSION_3'][row_2]])
                list_product.append(a)

                # take number of product in input
                number_product.append(int(name_product.split(' ')[0]))


    # sort product from highest price to lowest
    def key_sort(s):
        return s[2]
    sort_product = []
    for i in range(0,cnt):
        a = sorted(list_product[i], key = key_sort, reverse=True)
        sort_product.append(a)
    
    # backtrack to find products that satisfy the condition
    result = []
    if sort_product == []:
        return result
    def BT(dem, sum):
        if dem == cnt and sum <= max_price and sum >= min_price:
            return True
        if sum > max_price or dem >= len(sort_product):
            return False
        for product in sort_product[dem]:
            check = BT(dem+1, sum+number_product[dem]*product[2])
            if check:
                a = product
                a.append(number_product[dem])
                result.append(a)
                return True
    BT(0, 0)
    return result

def find_level(total_price, list_product):
    # take product from DB
    result = []

    for product in list_product:
        for row in data.index:
            if data['PRODUCT_INFO_ID'][row] == product[0]:
                ans = product
                if data['THRESHOLD_1'][row] == '':
                    ans.append(0)
                    ans.append('GÓI MUA SẮM MỨC 3')
                    result.append(ans)
                    continue
                if data['THRESHOLD_1'][row] == 0:
                    ans.append(0)
                    ans.append('GÓI MUA SẮM MỨC 3')
                else:
                    price_level1 = int(data['THRESHOLD_1'][row].split('>')[1].strip().split('triệu')[0].strip())*1000000
                    price_level2 = int(data['THRESHOLD_2'][row].split('-')[0].strip().split(' ')[-1])*1000000
                    if total_price >= price_level1:
                        ans.append(data['COMMISSION_1'][row])
                        ans.append('GÓI MUA SẮM MỨC 1')
                        ans[2] = data['VAT_PRICE_1'][row]
                    elif total_price >= price_level2:
                        ans.append(data['COMMISSION_2'][row])
                        ans.append('GÓI MUA SẮM MỨC 2')
                        ans[2] = data['VAT_PRICE_2'][row]
                    else:
                        ans.append(0)
                        ans.append('GÓI MUA SẮM MỨC 3')
                
                result.append(ans)
    return result


def take_product(text_input):

    t1 = time.time()
    # text nhu cau
    out_text = 'Dựa trên yêu cầu của bạn:'
    # get the satisfied product list
    list_input = split_sentences(text_input)[2:-2].split("'")
    list_product = []
    print('list_input', list_input)
    obj_list = []
    for input in list_input:
        if len(input) < 4:
            continue
        obj_val = search_obj_val(input)
        print('check object', obj_val)

        _object = obj_val.split('\n')[1][1:-1]
        _value = obj_val.split('\n')[2][1:-1]

        out_text += '\n\t- {} với giá {}'.format(_object.replace("'", ""),_value.replace("'", ""))

        for j in _object.split("'"):
            s = j.strip()
            if s == '' or s == ',':
                continue
            obj_list.append(s[2:].strip())

        product = find_product(_object, _value)
        for j in product:
            list_product.append(j)
    
    print('check list_product:',list_product)
    # product level calculation
    total_price = 0
    for product in list_product:
        total_price += product[2]*product[4]
    list_value = find_level(total_price, list_product)

        
    if len(list_value)>0:
        # embed to dict into list
        out_text += '\n\nĐể phù hợp với ngân sách và nhu cầu sử dụng của bạn, VCC Bot đề xuất sản phẩm sau:'
        list_key = ["product_code", "product_name", "product_price", "commission_saler", "amount", "commission_implementer", "level"]
        result = [{list_key[i]: row[i] for i in range(len(list_key))} for row in list_value]
        total_price = 0
        total_commission_saler = 0
        total_commission_implementer = 0
        for x in result:
            out_text += '\n\t+ Với {} {}: {}VND - {}'.format(x['amount'],x['product_name'],x['product_price'],x['level'])
            if int( x['commission_saler']) != 0 and int(x['commission_implementer']) != 0:
                out_text += '\n\t\t(Hoa hòng bán hàng nhận được là: {}VND và hoa hồng triển khai nhận được là: {}VND)'.format(x['commission_saler'],x['commission_implementer'])
            else:
                out_text += '\n\t\t(Hiện tại không có chính sách hoa hồng cho sản phẩm này)'
            # total prices
            total_price += float(x['product_price'])
            total_commission_saler += float(x['commission_saler'])
            total_commission_implementer += float(x['commission_implementer'])
        out_text += '\n\nTổng giá trị của gói sản phẩm này là {}VND, giúp bạn tiết kiệm và đáp ứng đầy đủ nhu cầu sử dụng.'.format(str(total_price))
        out_text += '\nNếu có bất kỳ câu hỏi hoặc yêu cầu nào khác, vui lòng liên hệ với VCC Bot. VCC Bot luôn sẵn lòng hỗ trợ.'
    else:
        out_text += '\nTôi không thể đáp ứng yêu cầu của bạn.'
        out_text += '\nNếu có bất kỳ câu hỏi hoặc yêu cầu nào khác, vui lòng liên hệ với VCC Bot. VCC Bot luôn sẵn lòng hỗ trợ.'
    
    return out_text