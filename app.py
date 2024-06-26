import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi import FastAPI, UploadFile, Form, File
import requests
import time
from chat import predict_rasa_llm
from ChatBot_Extract_Intent.module.search_product import product_seeking
from ChatBot_Extract_Intent.config_app.config import get_config
from get_product_inventory import get_inventory
import io
import librosa
import soundfile

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
    Image: UploadFile = File(None),
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
    print("check_file", Image)
    # print("check voice", Voice)
    # Case 1: Image is provided
    if Image:
        # Save the image locally
        data = await Image.read()
        file_path = f'./Retrieval_Vit_STT/test_image/{Image.filename}'
        with open(file_path, 'wb') as f:
            f.write(data)
        # image_data = await Image.read()
        url = "http://127.0.0.1:8000/process_image/"
        
        # Prepare the files and data to be sent
        with open(file_path, "rb") as f_image:
          files = {"data_type": f_image}
          data = {"type": "image"}
          response = requests.post(url, data=data, files=files)
        # response = requests.post("http://127.0.0.1:8000/process-image/",files={"file": image_data})
          if response.status_code == 200:
              process_image = response.json()
              print(process_image)
              results["content"] = process_image
          return results

    if Voice:
        src_output = './ChatBot_Extract_Intent/data/test_voice/test.wav'
        with open(src_output, "wb+") as file_wav:
            file_wav.write(Voice.file.read())
        # y, s = librosa.load(src_output, sr=16000)
        # soundfile.write(src_output, y, s)
        url = "http://127.0.0.1:8000/process_image/"
        with open(src_output, "rb") as f_wav:
            files = {"data_type": f_wav}
            data = {"type": "audio"}
            response = requests.post(url,data=data, files=files)

            if response.status_code == 200:
                process_voice = response.json()
            print('speech_2_text:',process_voice)
            # predict llm
            chat_out = predict_rasa_llm(process_voice, IdRequest, NameBot, User)

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