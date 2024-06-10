import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi import FastAPI, UploadFile, Form, File
import requests
import time
from chat import predict_rasa_llm
from ChatBot_Extract_Intent.module.search_product import product_seeking
from ChatBot_Extract_Intent.config_app.config import get_config
from get_product_inventory import get_inventory

config_app = get_config()

def hao_test(InputText,IdRequest,NameBot,User,GoodsCode = None,ProvinceCode = None,Image = None,Voice = None):
    results = {
    "products" : [],
    "terms" : [],
    "inventory_status": False,
    "content" : "",
    "status" : 200,
    "message": "",
    "time_processing":''
    } 
    # # try:
    if InputText == 'terms' or InputText == None and GoodsCode == None:
        results["terms"]= config_app['parameter']['rasa_bottom']
        results["content"] = "Xin chào! Mình là trợ lý AI của bạn tại VCC. Mình đang phát triển nên không phải lúc nào cũng đúng. Bạn có thể phản hồi để giúp mình cải thiện tốt hơn. Mình sẵn sàng giúp bạn với câu hỏi về chính sách và tìm kiếm sản phẩm. Hôm nay bạn cần mình hỗ trợ gì không?"
        return results

    if InputText != 'terms' and InputText != None:
        chat_out = predict_rasa_llm(InputText,IdRequest,NameBot,User)
        results['content'] = chat_out['out_text']
        results['terms'] = chat_out['terms']
        results['inventory_status'] = chat_out['inventory_status']
        results = product_seeking(results = results, texts=results['content'])
        return results

    if GoodsCode and InputText == None:
        results['content'] = get_inventory(GoodsCode,ProvinceCode)

    # else:
    #   results["content"]="""Xin chào! Mình là trợ lý AI của bạn tại VCC. Mình đang phát triển nên không phải lúc nào cũng đúng. Bạn có thể phản hồi để giúp mình cải thiện tốt hơn. Hôm nay bạn cần mình hỗ trợ gì hông? ^^"""


    print('===========results===========')
    print(results)
    return results


InputText = "bạn ở đâu"
IdRequest = "0506"
NameBot = "0506"
User = "0506"

hao_test(InputText,IdRequest,NameBot,User)