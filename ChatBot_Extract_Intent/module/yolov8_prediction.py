from ultralytics import YOLO
from PIL import Image
import numpy as np
import time
import base64
from io import BytesIO
from PIL import Image
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
from config_app.config import get_config
config_app = get_config()
# Load a model
def yolov8_predictor(image_base64,threshold = config_app['yolo_params']['conf_thres']):
    t0 = time.time()
    # Giải mã dữ liệu base64
    image_content = base64.b64decode(image_base64)
    # Chuyển dữ liệu thành ảnh PIL
    image_pil = Image.open(BytesIO(image_content))

    model = YOLO(config_app['yolo_params']['weight_path'])  # load a custom model

    results = model(image_pil,verbose=False)
    result = results[0]
    box = result.boxes[0]
    cords = box.xyxy[0].tolist()
    class_id = box.cls[0].item()
    conf = box.conf[0].item()
    if conf <= threshold:
        return 0
    # print('yolov8 check:',results[0].probs)
    name = config_app['yolo_params']['classes'][int(class_id)]
    print('Object:',name)
    print('yolov8_predictor time: ',time.time() - t0)
    return config_app['yolo_params']['classes'][int(class_id)]

