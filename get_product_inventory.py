import requests
# URL của API
url = "http://wms.congtrinhviettel.com.vn/wms-service/service/magentoSyncApiWs/getListRemainStockV2"

# Dữ liệu cần gửi trong yêu cầu POST
def get_inventory(msp,mt=None):
    print('============get_inventory============')
    payload = {
        "source": {
            "goodsCode": msp,
            "provinceCode": mt
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
        
        if len(response_data['data']) == 0:
            return "Không thấy sản phẩm có mã " + msp + " trong kho, vui lòng kiểm tra lại sản phẩm bạn muốn tìm kiếm."
        # Kiểm tra nếu có dữ liệu trong phần 'data'
        if 'data' in response_data and response_data['data'] is not None:
            # Duyệt qua từng mục trong danh sách 'data'
            info_strings = []
            for item in response_data['data']:
                # Xử lý từng mục trong danh sách
                amount = item["amount"] if item["amount"] is not None else ""
                goods_name = item["goodsName"] if item["goodsName"] is not None else ""
                stock_name = item["stockName"] if item["stockName"] is not None else ""
                stock_address = item["address"] if item["address"] is not None else ""
                # In hoặc xử lý thông tin từng mục
                if stock_name != '' or stock_address !='':
                    info_string = (
                        f"Tên Kho : {stock_name}\n"
                        f"Địa chỉ cụ thể: {stock_address}\n"
                        f"Số lượng sản phẩm còn trong kho: {amount}\n"
                        "---------"
                    )
                    info_strings.append(info_string)

                # Kết hợp các chuỗi thành một chuỗi duy nhất
            final_string = "\n".join(info_strings)
            return final_string
    else:
        # In lỗi nếu có
        return "Hiện tại tôi không thể tra cứu thông tin hàng tồn kho của sản phẩm bạn đang mong muốn, xin vui lòng thử lại sau."
