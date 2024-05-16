import os
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts.few_shot import FewShotPromptTemplate
from langchain.prompts.prompt import PromptTemplate
from langchain.chains import LLMChain



os.environ['OPENAI_API_KEY'] = ''
llm = ChatOpenAI(model_name='gpt-3.5-turbo-16k', temperature=0)


def split_sentences(text_input):
    examples = [
        {
            "info": "My name is Alice, and my phone number is 0987654321. I live at 456 Le Loi Street, District 1, Ho Chi Minh City.",
            "name": "Alice",
            "address": "456 Le Loi Street, District 1, Ho Chi Minh City",
            "phone": "0987654321"
        },
        {
            "info": "You can call me David. My phone number is 0901234567, and I reside at 789 Nguyen Hue Street, District 3, Ho Chi Minh City.",
            "name": "David",
            "address": "789 Nguyen Hue Street, District 3, Ho Chi Minh City",
            "phone": "0901234567"
        },
        {
            "info": "I'm Lily, and my phone number is 0778899000. I live at 1010 Tran Hung Dao Street, District 5, Ho Chi Minh City.",
            "name": "Lily",
            "address": "1010 Tran Hung Dao Street, District 5, Ho Chi Minh City",
            "phone": "0778899000"
        },
        {
            "info": "My name's Jack, and my phone number is 0845678901. You can find me at 1212 Vo Van Tan Street, District 10, Ho Chi Minh City.",
            "name": "Jack",
            "address": "1212 Vo Van Tan Street, District 10, Ho Chi Minh City",
            "phone": "0845678901"
        },
        {
        "info": "Hello, I'm Megan. I'd like a Grande Caramel Frappuccino with extra whipped cream for delivery to 432 Palm Boulevard.",
        "name": "Megan",
        "address": "432 Palm Boulevard",
        "phone": ""
        },
        {
        "info": "Hi, I'm Ryan. Can I get a Venti Iced Coffee with classic syrup and a splash of cream delivered to 543 Spruce Street?",
        "name": "Ryan",
        "address": "543 Spruce Street",
        "phone": ""
        }
    ]

    example_formatter_template = """
    Input info from user: {info}
    The information extracted from above info:
    info: {info}
    name: {name}
    address: {address}
    phone: {phone}
    """

    example_prompt = PromptTemplate(
        input_variables=["info", "name", "address", "phone"],
        template=example_formatter_template,
    )

    few_shot_prompt = FewShotPromptTemplate(
        examples=examples,
        example_prompt=example_prompt,
        prefix="Extract detailed information for customer needs. Returns the corresponding object. Here are some examples:",
        suffix="Input info from user: {info}\nThe information extracted from above info:",
        input_variables=["info"],
        example_separator="\n\n",
    )

    chain = LLMChain(llm=llm, prompt=few_shot_prompt)

    return chain.run(info=text_input)

def extract_info(text):
    # Tách chuỗi thông tin bằng dấu cách
    parts = text.split()

    # Tìm vị trí của các từ khóa
    info_index = parts.index("info:") if "info:" in parts else -1
    name_index = parts.index("name:") if "name:" in parts else -1
    address_index = parts.index("address:") if "address:" in parts else -1
    phone_index = parts.index("phone:") if "phone:" in parts else -1

    # Trích xuất thông tin từ các vị trí tìm được
    info = " ".join(parts[info_index + 1 : name_index]).strip() if info_index != -1 else None
    name = " ".join(parts[name_index + 1 : address_index]).strip() if name_index != -1 else None
    address = " ".join(parts[address_index + 1 : phone_index]).strip() if address_index != -1 else None
    phone = " ".join(parts[phone_index + 1 :]).strip() if phone_index != -1 else None

    # Tạo dictionary chứa thông tin trích xuất
    extracted_info = {
        "info": info,
        "name": name,
        "address": address,
        "phone": phone
    }

    return extracted_info

text_input = '''Hi, I'm Alex. I'd like a Grande Green Tea Frappuccino with soy milk '''
result_split = split_sentences(text_input)
result = extract_info(result_split)

print('extract_info')
print(result)
