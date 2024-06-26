import requests

url = "http://127.0.0.1:8000/process_image/"


# Đường dẫn tới file ảnh
file_path = "/home/oem/Documents/VCC/Chatbot/Luan_elastic_LLM/ChatBot_Extract_Intent/data/test_image/test_image/dieuhoa.jpg"

with open(file_path, "rb") as f:
    print(f)
    files = {"data_type": f}
    data = {"type": "image"}
    response = requests.post(url, data=data, files=files)

print(response.json())