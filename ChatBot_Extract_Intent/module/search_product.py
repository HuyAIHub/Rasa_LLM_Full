import pandas as pd
import time
from ChatBot_Extract_Intent.config_app.config import get_config
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
    # print('results product_seeking:',results)
    return results

def product_seeking_terms(results,texts):    
    start_time = time.time()

    for index, row in df.iterrows():
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
            results["terms"].append(product)
    execution_time = time.time() - start_time
    print("time to find product link: ",execution_time)
    return results

# def get_products_by_group(results,group_name):
#     products = df[df['GROUP_PRODUCT_NAME'] == group_name][['PRODUCT_INFO_ID', 'PRODUCT_NAME']]
#     product_list = list(products.itertuples(index=False, name=None))

#     for idx, (product_id, product_name) in enumerate(product_list, start=1):
#         # Tạo một dictionary để lưu thông tin của sản phẩm
#         product = {
#             'code': product_id,
#             'name': product_name,
#         }
#         # Thêm sản phẩm vào danh sách products
#         results["products"].append(product)
#     return len(product_list), product_list



def get_products_by_group(results,group_name):
    products = df[df['GROUP_PRODUCT_NAME'] == group_name]
    if all(col in products.columns for col in ['PRODUCT_INFO_ID', 'PRODUCT_NAME', 'LINK_SP']):
        products = products[['PRODUCT_INFO_ID', 'PRODUCT_NAME', 'LINK_SP']]
        product_list = list(products.itertuples(index=False, name=None))
        for idx, (product_id, product_name,link) in enumerate(product_list, start=1):
            # Tạo một dictionary để lưu thông tin của sản phẩm
            product = {
                'code': product_id,
                'name': product_name,
                "link": link
            }
            # Thêm sản phẩm vào danh sách products
            results["products"].append(product)
        print('Tìm thấy {} sản phẩm'.format(len(product_list)))
        return len(product_list), product_list
    else:
        print('Không tìm thấy sản phẩm')
        return 0, []
    