
from ultralytics import YOLO

from PIL import Image
# import cv2
# import matplotlib.pyplot as plt

import os
import numpy as np


class ObjectDetector:
    def __init__(self) -> None:
        # 적절한 YOLOv8 모델 파일 경로로 변경
        self.model = YOLO('yolov8n.pt')

    def get_object_images(self, image: Image.Image) -> list[Image.Image]:
        # image_path = os.path.join(image_path)
        # original_image = Image.open(image_path)
        results = self.model(image)

        # 크롭
        cropped_img_list = []
        for i, xyxy in enumerate(results[0].boxes.xyxy):
            left, top, right, bottom = map(int, xyxy)
            cropped_img = image.crop((left, top, right, bottom))
            cropped_img_list.append(cropped_img)
            # print(type(cropped_img))

        # show_images(cropped_img_list)
        return cropped_img_list






