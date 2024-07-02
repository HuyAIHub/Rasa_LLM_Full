import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi import FastAPI, UploadFile, Form, File
import requests
import time
from chat import predict_rasa_llm
from ChatBot_Extract_Intent.module.search_product import product_seeking
from ChatBot_Extract_Intent.config_app.config import get_config
from ChatBot_Extract_Intent.module.yolov8_prediction import yolov8_predictor
from ChatBot_Extract_Intent.module.speech2text import speech_2_text,downsampleWav
from get_product_inventory import get_inventory
config_app = get_config()

app = FastAPI()

numberrequest = 0
@app.post('/llm')
async def post(
    InputText: str = Form(None),
    IdRequest: str = Form(...),
    NameBot: str = Form(...),
    User: str = Form(...),
    GoodsCode: str = Form(None),
    ProvinceCode: str = Form(None),
    Image: str = Form(None),
    Voice: UploadFile = File(None)
):
    start_time = time.time()
    global numberrequest
    numberrequest += 1
    print("numberrequest", numberrequest)
    
    results = {
        "products": [],
        "terms": [],
        "inventory_status": False,
        "content": "",
        "status": 200,
        "message": "",
        "time_processing": ''
    }

    # Case 1: Image is provided
    if Image:
        text2 = "Hiện tôi không có thông tin về sản phẩm bạn đang quan tâm."
        product_name = yolov8_predictor(Image)
        if product_name != 0:
            chat_out = predict_rasa_llm(product_name, IdRequest, NameBot, User)
            results["content"] = chat_out['out_text']
        else:
            results["content"] = text2
        results['time_processing'] = time.time() - start_time
        print(results)
        return results
    
    if Voice:
        src_output = './ChatBot_Extract_Intent/data/test_voice/test.wav'
        with open(src_output, "wb+") as file_object:
            file_object.write(Voice.file.read())
        downsampleWav(src_output, src_output)

        out_put = speech_2_text(src_output)
        print('speech_2_text:',out_put)
        # predict llm
        chat_out = predict_rasa_llm(out_put, IdRequest, NameBot, User)

        results.update({
            "content": chat_out['out_text'],
            "terms": chat_out['terms'],
            "inventory_status": chat_out['inventory_status']
        })
        # tim san pham
        results = product_seeking(results=results, texts=results['content'])
        print('results:',results)
        return results
    # Case 2: InputText is 'terms' or None and GoodsCode is None
    if InputText in ('terms', None) and GoodsCode is None:
        results["terms"] = config_app['parameter']['rasa_bottom']
        results["content"] = (
            "Xin chào! Mình là trợ lý AI của bạn tại VCC. "
            "Mình đang phát triển nên không phải lúc nào cũng đúng. "
            "Bạn có thể phản hồi để giúp mình cải thiện tốt hơn. "
            "Mình sẵn sàng giúp bạn với câu hỏi về chính sách và tìm kiếm sản phẩm. "
            "Hôm nay bạn cần mình hỗ trợ gì không?"
        )
    
    # Case 3: InputText is not 'terms' or None
    elif InputText not in ('terms', None):
        chat_out = predict_rasa_llm(InputText, IdRequest, NameBot, User)
        results.update({
            "content": chat_out['out_text'],
            "terms": chat_out['terms'],
            "inventory_status": chat_out['inventory_status']
        })
        results = product_seeking(results=results, texts=results['content'])
    
    # Case 4: GoodsCode is provided and InputText is None
    elif GoodsCode and InputText is None:
        results['content'] = get_inventory(GoodsCode, ProvinceCode)

    # Set processing time and return results
    results['time_processing'] = time.time() - start_time
    print(results)
    return results

uvicorn.run(app, host="0.0.0.0", port=int(config_app['server']['port']))