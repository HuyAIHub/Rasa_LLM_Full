import requests

# URL của API
url = "http://wms.congtrinhviettel.com.vn/wms-service/service/magentoSyncApiWs/getListRemainStockV2"

# Dữ liệu cần gửi trong yêu cầu POST
payload = {
    "source": {
        "goodsCode": "SMDEN000029",
        "provinceCode": "HNI"
    }
}

# Headers nếu có (ở đây để trống nếu không yêu cầu)
headers = {
    "Content-Type": "application/json"
}

# Gửi yêu cầu POST đến API
response = requests.post(url, json=payload, headers=headers)

# Kiểm tra mã trạng thái của phản hồi
if response.status_code == 200:
        # Chuyển đổi phản hồi sang dạng JSON
    response_data = response.json()
    # print(response_data)
    # Kiểm tra nếu có dữ liệu trong phần 'data'
    if 'data' in response_data and response_data['data'] is not None:
        # Duyệt qua từng mục trong danh sách 'data'
        for item in response_data['data']:
            # Xử lý từng mục trong danh sách
            stock_id = item.get('stockId', None)
            goods_id = item.get('goodsId', None)
            amount = item.get('amount', None)
            goods_code = item.get('goodsCode', None)
            goods_name = item.get('goodsName', None)
            stock_code = item.get('stockCode', None)
            stock_name = item.get('stockName', None)
            stock_address = item.get('address', None)
            # In hoặc xử lý thông tin từng mục
            # print(f"Stock ID: {stock_id}")
            # print(f"Goods ID: {goods_id}")
            print(f"Amount: {amount}")
            print(f"Goods Code: {goods_code}")
            print(f"Goods Name: {goods_name}")
            print(f"Stock Code: {stock_code}")
            print(f"Stock Name: {stock_name}")
            print(f"stock_address: {stock_address}")
            print("---------")
else:
    # In lỗi nếu có
    print(f"Error: {response.status_code}")