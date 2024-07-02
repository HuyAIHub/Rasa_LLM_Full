from ultralytics import YOLO
from PIL import Image
import numpy as np
import time
import base64
from io import BytesIO
from PIL import Image, ImageOps, ExifTags
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
from ChatBot_Extract_Intent.config_app.config import get_config
import cv2

config_app = get_config()

# Hàm chuyển đổi base64 thành hình ảnh PIL
def url_to_image(image_base64):
    # Giải mã dữ liệu base64
    image_content = base64.b64decode(image_base64)
    # Chuyển dữ liệu thành ảnh PIL
    image_pil = Image.open(BytesIO(image_content))
    input_img = ImageOps.exif_transpose(image_pil)  # Tránh bị xoay
    input_img.save('check.jpg')
    return input_img

# Hàm vẽ các đối tượng phát hiện được lên ảnh và lưu lại
def draw_boxes(image, boxes, labels, confidences, threshold):
    image_np = np.array(image)
    for box, label, confidence in zip(boxes, labels, confidences):
        if confidence > threshold:
            x1, y1, x2, y2 = map(int, box)
            # Vẽ hộp chữ nhật xung quanh đối tượng
            cv2.rectangle(image_np, (x1, y1), (x2, y2), (0, 255, 0), 3)  # Độ dày hộp chữ nhật là 3
            print('labels:',labels)
            label_text = f'{label}: {confidence:.2f}'
            # Đặt kích thước chữ và độ dày chữ
            font_scale = 1.0
            font_thickness = 2
            # Tính toán kích thước của text box để hiển thị nhãn chính xác
            (text_width, text_height), baseline = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)
            
            # Đảm bảo text box không bị tràn viền
            text_x1 = x1
            text_y1 = y1 - text_height - baseline
            text_x2 = x1 + text_width
            text_y2 = y1

            if text_y1 < 0:  # Nếu text box tràn ra khỏi ảnh ở phía trên
                text_y1 = y1 + text_height + baseline
                text_y2 = y1 + text_height + baseline + text_height
            
            # Vẽ nền cho text box
            cv2.rectangle(image_np, (text_x1, text_y1), (text_x2, text_y2), (0, 255, 0), -1)
            # Vẽ text lên ảnh
            cv2.putText(image_np, label_text, (x1, text_y2 - baseline), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 255), font_thickness)
    
    output_image = Image.fromarray(image_np)
    output_image.save('output.jpg')

# Hàm dự đoán đối tượng bằng YOLOv8
def yolov8_predictor(image_base64, threshold=config_app['yolo_params']['conf_thres']):
    print("==========yolov8============")
    t0 = time.time()
    image_pil = url_to_image(image_base64)
    image_pil.save('check2.jpg')
    model = YOLO(config_app['yolo_params']['weight_path'])  # load a custom model

    results = model(image_pil, verbose=False)
    result = results[0]
    if len(result.boxes) == 0:
        return 0

    boxes = [box.xyxy[0].tolist() for box in result.boxes]
    class_ids = [box.cls[0].item() for box in result.boxes]
    confidences = [box.conf[0].item() for box in result.boxes]
    labels = [config_app['yolo_params']['classes'][int(class_id)] for class_id in class_ids]
    
    # Vẽ các đối tượng lên ảnh
    draw_boxes(image_pil, boxes, labels, confidences, threshold)
    print('labels:',labels)
    print('yolov8_predictor time: ', time.time() - t0)
    return labels