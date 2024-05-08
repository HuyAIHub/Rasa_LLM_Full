import pandas as pd
import time
from config_app.config import get_config
config_app = get_config()

df = pd.read_excel(config_app["parameter"]["data_private"])
import csv

def parse_variables(chuoi):
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


def find_product(csv_path,products_to_find):
    # Đọc file CSV
    with open(csv_path, 'r') as file:
        reader = csv.DictReader(file)
        data = list(reader)

    found_products = {}
    for product in data:
        product_name = product['PRODUCT_NAME'].lower()
        group_name = product['GROUP_PRODUCT_NAME'].lower()
        for keyword in products_to_find:
            if f" {keyword} " in f" {product_name} " or f" {keyword} " in f" {group_name} ":
                if keyword not in found_products:
                    found_products[keyword] = []
                found_products[keyword].append(product)

    # Tạo chuỗi kết quả tìm kiếm
    result_string = ""
    for keyword in products_to_find:
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



# def parse_price_range(value):
#     pattern = r"(?P<prefix>\b(dưới|trên|từ|đến|khoảng)\s*)?(?P<number>\d+(?:,\d+)*)\s*(?P<unit>triệu|nghìn)?\b"

#     min_price = 0
#     max_price = float('inf')

#     for match in re.finditer(pattern, value, re.IGNORECASE):
#         prefix = match.group('prefix') or ''
#         number = float(match.group('number').replace(',', ''))
#         unit = match.group('unit') or ''

#         if unit.lower() == 'triệu':
#             number *= 1000000
#         elif unit.lower() == 'nghìn':
#             number *= 1000

#         if prefix.lower().strip() == 'dưới':
#             max_price = min(max_price, number)
#         elif prefix.lower().strip() == 'trên':
#             min_price = min(max_price, number)
#         elif prefix.lower().strip() == 'từ':
#             min_price = min(max_price, number)
#         elif prefix.lower().strip() == 'đến':
#             max_price = max(min_price, number)
#         else:  # Trường hợp không có từ khóa
#             min_price = number * 0.9
#             max_price = number * 1.1

#     if min_price == float('inf'):
#         min_price = 0
#     print('min_price, max_price:',min_price, max_price)
#     return min_price, max_price

# def handle_price(demands):
#     # Xử lý yêu cầu về giá của sản phẩm
#         # Xử lý yêu cầu
#     matching_products = []
#     # if demands["demand"] == "giá":
#     for product in data:
#         group_name = product['GROUP_PRODUCT_NAME'].lower()
#         if any(obj.lower() in group_name for obj in demands["object"]):
#             raw_price_str = re.sub(r'[^0-9,]', '', product['RAW_PRICE'])
#             raw_price = float(raw_price_str.replace(',', ''))
#             min_price, max_price = parse_price_range(demands["value"].lower())
#             if min_price <= raw_price <= max_price:
#                 matching_products.append(product)
#     # else:
#     #     return "Câu hỏi không liên quan đến giá sản phẩm."

#     # Trả kết quả vào một chuỗi
#     result_string = ""
#     if matching_products:
#         result_string += f"{demands['object'][0].title()} {demands['value']} tìm thấy:\n"
#         for product in matching_products:
#             result_string += f"- {product['PRODUCT_NAME']} - Giá: {product['RAW_PRICE']} VNĐ\n"
#     else:
#         result_string += f"Không tìm thấy {demands['object'][0]} {demands['value']} trong dữ liệu."

#     return result_string