import uvicorn
import os
import time
from llm_predict import predict_llm
from config_app.config import get_config
from utils.logging import Logger_Days
from fastapi import FastAPI
from module.search_product import product_seeking ,get_products_by_group
from module.yolov8_prediction import yolov8_predictor
from fastapi import FastAPI, File, UploadFile
from fastapi import FastAPI, UploadFile, Form, File
from main import process_command

config_app = get_config()

if not os.path.exists("./logs"):
    os.makedirs("./logs")
file_name = './logs/logs'
log_obj = Logger_Days(file_name)

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

    log_obj.info("-------------------------NEW_SESSION----------------------------------")
    log_obj.info("GuildID  = :" + " " + str(IdRequest)) 
    log_obj.info("User  = :" + " " + str(User))
    log_obj.info("NameBot  = :" + " " + str(NameBot))
    log_obj.info("InputText:" + " " + str(InputText)) # cau hoi
    # log_obj.info("IP_Client: " + str(request.client.host))
    log_obj.info("NumberRequest: " + str(numberrequest))
    print('InputText:',InputText)

    if Image:
        #phan loai theo hinh anh
        text1 = "Sản phẩm bạn đang quan tâm là {}? Một số thông tin về sản phẩm bạn đang quan tâm:\n{}"
        text2 = "Hiện tôi không có thông tin về sản phẩm bạn đang quan tâm."

        product_name = yolov8_predictor(Image)
        if product_name != 0:
            content = predict_llm(InputText, IdRequest, NameBot, User, log_obj)

            results["content"] = content
        else:
            results["content"] = text2
        return results
    else:
        # predict llm
        result = predict_llm(InputText,IdRequest, NameBot, User, log_obj)
        log_obj.info("Answer: " + str(result))

        results["content"] = result
        # tim san pham
        
        results = product_seeking(results = results, texts=results["content"])
    results['time_processing'] = str(time.time() - start_time)
    print(results)
    return results

uvicorn.run(app, host=config_app['server']['ip_address'], port=int(config_app['server']['port']))