import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi import FastAPI, UploadFile, Form, File
import requests
import time
from chat import predict_rasa_llm
from ChatBot_Extract_Intent.module.search_product import product_seeking
from ChatBot_Extract_Intent.config_app.config import get_config
config_app = get_config()

app = FastAPI()

numberrequest = 0
@app.post('/llm')
async def post(InputText: str = Form(None),
                IdRequest: str = Form(...),
                NameBot: str = Form(...),
                User: str = Form(...),
                Image: str = Form(None),
                Voice: UploadFile = File(None)):
    start_time = time.time()
    global numberrequest
    numberrequest = numberrequest + 1
    print("numberrequest", numberrequest)
    results = {
    "products" : [],
    "terms" : [],
    "content" : "",
    "status" : 200,
    "message": "",
    "time_processing":''
    }
    # try:
    results["terms"]= [
    {
      "payload": "/Tôi đang quan tâm sản phẩm điều hòa?",
      "title": "Bạn đang quan tâm sản phẩm điều hòa?"
    },
    {
      "payload": "/Tôi muốn mua sản phẩm Đèn năng mặt trời với giá 10 triệu?",
      "title": " Bạn muốn mua sản phẩm Đèn năng mặt trời với giá 10 triệu?"
    },
    {
      "payload": "/Tôi muốn biết VCC bán những gì?",
      "title": "Bạn muốn biết VCC bán những gì?"
    },
    {
      "payload": "/Bạn đang quan tâm đến dịch vụ, chính sách của VCC?",
      "title": "Bạn đang quan tâm đến dịch vụ, chính sách của VCC?"
    }]

    results["content"]=["""Xin chào! Mình là trợ lý AI của bạn tại VCC. Mình đang phát triển nên không phải lúc nào cũng đúng. 
    Bạn có thể phản hồi để giúp mình cải thiện tốt hơn. 
    Hôm nay bạn cần mình hỗ trợ gì hông? ^^"""]

    chat_out = predict_rasa_llm(InputText,IdRequest,NameBot,User)
    results = product_seeking(results = results, texts=chat_out)
    results['content'] = chat_out['out_text']
    results['terms'] = chat_out['terms']
    print(results)
    return results

uvicorn.run(app, host="0.0.0.0", port=int(config_app['server']['port']))