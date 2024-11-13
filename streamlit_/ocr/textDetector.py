import easyocr

from PIL import Image, ImageOps
import numpy as np
 

class TextDetector:
    def __init__(self) -> None:
        self.reader = easyocr.Reader(['ko','en'])

    def crop(self, object_image: Image.Image):
        img_arr = np.array(object_image)

        text_box_list = []
        prob_list = []

        result_td = self.reader.readtext(img_arr)
        for i, (bbox, text, prob) in enumerate(result_td):
            # print(bbox)

            # 좌상단과 우하단 좌표를 사용해 자를 수 있음
            x_min = int(min(bbox[0][0], bbox[1][0], bbox[2][0], bbox[3][0]))
            y_min = int(min(bbox[0][1], bbox[1][1], bbox[2][1], bbox[3][1]))
            x_max = int(max(bbox[0][0], bbox[1][0], bbox[2][0], bbox[3][0]))
            y_max = int(max(bbox[0][1], bbox[1][1], bbox[2][1], bbox[3][1]))

            # 이미지 자르기 (좌표는 (left, upper, right, lower))
            text_box = object_image.crop((x_min, y_min, x_max, y_max))
            text_box_list.append(text_box)
            prob_list.append(prob)
        return text_box_list, prob_list

    def filtering_title_box(self, text_box_list, prob_list):
        if not text_box_list:
            return [], [], [], []

        size_list = [sorted(b.size) for b in text_box_list]

        max_char_size = max(next(zip(*size_list)))
        char_size_range = [max_char_size*0.8, max_char_size*1.2]

        title_boxes = []
        title_probs = []
        etc_boxes = []
        etc_probs = []

        for tb, prob in zip(text_box_list, prob_list):
            if char_size_range[0] <= min(tb.size) <= char_size_range[1]:
                title_boxes.append(tb)
                title_probs.append(prob)
            else:
                etc_boxes.append(tb)
                etc_probs.append(prob)
        return title_boxes, title_probs, etc_boxes, etc_probs

    def crop_all(self, object_image: Image.Image):
        text_box_list, prob_list = self.crop(object_image)
        rt_text_box_list, rt_prob_list = self.crop(object_image.rotate(90, expand=True))

        tb_list = self.filtering_title_box(text_box_list, prob_list)
        rt_tb_list = self.filtering_title_box(rt_text_box_list, rt_prob_list)

        return tb_list, rt_tb_list
