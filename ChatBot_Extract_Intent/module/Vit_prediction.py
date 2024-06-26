import numpy as np
import pandas as pd
import torch
import matplotlib.pyplot as plt
from transformers import ViTImageProcessor, ViTForImageClassification
from transformers import CLIPModel, CLIPProcessor
from pathlib import Path
from PIL import Image
import gradio as gr
import psutil
import tqdm
import cv2
import time
import faiss
import json
import shutil
import os
from ChatBot_Extract_Intent.ImageVit_Retrival.ViT_Processor import ViT_Processor
from ChatBot_Extract_Intent.ImageVit_Retrival.CLIP_Processor import CLIP_Processor

def process_image_user(image_path):

    image = Image.open(image_path)
    # lưu query image 
    path_query = "query_image.png"
    if os.path.exists(path_query): 
        os.remove(path_query)
    image.save(path_query)

    ######################## OUPUT FOR ViT RETRIEVAL #######################
    process = ViT_Processor(image)
    path_images, image_names, distance_euclide = process.run()

    images_after_query = [Image.open(path_img) for path_img in path_images]
    grid_results_image = Image.open("results images query.png")
    
    # return f"Sản phẩm: {image_names} || {distance_euclide}", \
    #     grid_results_image
        
    return f"Sản phẩm: {image_names}"
# print(process_image_user("/home/oem/Documents/VCC/Chatbot/Luan_elastic_LLM/Vit_test/download.jpeg"))
# Tạo giao diện Gradio
# iface = gr.Interface(
#     fn=process_image_user,

#     inputs=[# gr.Textbox(lines=2, label="User", placeholder="Nhập yêu cầu của bạn tại đây."),
#             gr.Image(type="pil", label="Nhập ảnh của bạn tại đây")],
    
#     outputs=[
#         gr.Textbox(lines=2, label="By ViT|CLIP Retriver"),
#         gr.Image(type="pil", label="By ViT|CLIP Retriver"),
#     ],
#     title="Image Search Engine",
#     description="Upload an image and get query images",
# )
# # Chạy ứng dụng
# iface.launch(share=True)