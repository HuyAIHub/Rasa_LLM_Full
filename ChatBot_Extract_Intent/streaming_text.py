import pandas as pd
import time
from config_app.config import get_config
config_app = get_config()

path = config_app['parameter']['data_private']
df = pd.read_excel(path)
df = df.fillna('')


def product_seeking(results,texts):    
    start_time = time.time()
    max_products = config_app['parameter']['num_product']
    found_products = 0  # Đếm số lượng sản phẩm đã tìm thấy
    for index, row in df.iterrows():
        if found_products >= max_products:
#             # Đã tìm đủ số lượng sản phẩm tối đa, thoát khỏi vòng lặp
            break
        if row['PRODUCT_NAME'] and row['PRODUCT_NAME'] in texts:
            product =  {
                "code" : "",
                "name" : "",
                "link" : ""
            }
            product = {
                "code": row['PRODUCT_INFO_ID'],
                "name": row['PRODUCT_NAME'],
                "link": row['LINK_SP']
            }
            results["products"].append(product)
            found_products += 1
    execution_time = time.time() - start_time
    print("time to find product link: ",execution_time)
    # print('results:',results)
    return results
results = {
    "products" : [],
    "terms" : [],
    "content" : "",
    "status" : 200,
    "message": "",
    "time_processing":''
    }

x = product_seeking(results,'xin chào')
print(x)