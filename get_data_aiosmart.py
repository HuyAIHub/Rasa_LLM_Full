import requests
import pandas as pd

# Thay thế {{API Url}} và {{Store Code}} bằng giá trị thực tế
api_url = "https://aiohomes.com.vn/rest/storeview_smart/V1/products"
params = {
    "searchCriteria[currentPage]": 1,
    "searchCriteria[pageSize]": 10000,
    "searchCriteria[filter_groups][0][filters][0][field]": "website_id",
    "searchCriteria[filter_groups][0][filters][0][value]": 2,
    "searchCriteria[filter_groups][0][filters][0][condition_type]": "eq",
    "fields": "items[id,sku,name,price,status,type_id,created_at,updated_at,weight,custom_attributes]"
}

# Thay thế token_bearer bằng token thực tế của bạn nếu cần xác thực
headers = {
    "Authorization": "Bearer 50s6s7r6d2zay1zvknfa3qfr41g1oedt",
    "Content-Type": "application/json"  # Đảm bảo tiêu đề đúng
}

# Hàm để lấy giá trị của custom attribute
def get_custom_attribute(custom_attributes, attribute_code):
    for attribute in custom_attributes:
        if attribute['attribute_code'] == attribute_code:
            return attribute['value']
    return None

def extract_from_json(data):
# Danh sách các sản phẩm
    items = data.get('items', [])

    # Danh sách các trường cần lấy
    fields = [
        'id', 'sku', 'name','short_description', 'price', 'status', 'type_id', 'created_at', 'updated_at', 'weight',
        'url_key', 'options_container', 'msrp_display_actual_price_type', 'tax_class_id',
        'category_ids', 'required_options', 'has_options', 'producingcountryname',
        'manufacturername', 'wattagestr', 'unittype', 'manufacturer', 'color', 'length',
        'width', 'height', 'goodsid', 'production_time', 'delivery_time'
    ]


    # Tạo danh sách để chứa dữ liệu
    extracted_data = []

    for item in items:
        item_data = {field: item.get(field) for field in fields if field in item}
        custom_attributes = item.get('custom_attributes', [])
        
        for field in fields:
            if field not in item_data:
                item_data[field] = get_custom_attribute(custom_attributes, field)

        extracted_data.append(item_data)

    # Chuyển đổi dữ liệu thành DataFrame
    df = pd.DataFrame(extracted_data)

    # Lưu DataFrame vào file Excel
    df.to_excel('magento_data.xlsx', index=False)



response = requests.get(api_url, params=params,headers=headers,verify=False)

if response.status_code == 200:
    data = response.json()
    extract_from_json(data)
    print(data)
else:
    print(f"Error: {response.status_code}")
    print(response.text)