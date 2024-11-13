from ocr.objectDetector import ObjectDetector
from ocr.textDetector import TextDetector
from ocr.textReader import TextReader

import numpy as np
import time


od = ObjectDetector()
td = TextDetector()
tr = TextReader()


def get_titles(image):

    cropped_img_list = od.get_object_images(image)

    results = []
    title_list = []

    total_st_time = time.time()
    # $$$ for test
    for i, img in enumerate(cropped_img_list[:3]):
        print(i)
        st_time = time.time()

        # 텍스트 영역 탐지
        tb_list, rt_tb_list = td.crop_all(img)
        # 시간 측정
        td_time = time.time()
        print(f"Text Detect: {td_time-st_time}")

        # 원본 이미지
        text_box_list, td_prob_list, _etc_box, _etc_probs = tb_list
        title_text_list, tr_prob_list = tr.get_title(text_box_list)
        title_text = " ".join(title_text_list)
        original_set = [title_text, np.mean(td_prob_list), np.mean(tr_prob_list)]
        # 시간 측정
        tr_time = time.time()
        print(f"Text Read: {tr_time-td_time}, {len(text_box_list)}")

        # 회전한 이미지
        rt_text_box_list, rt_td_prob_list, _rt_etc_box, _rt_etc_probs = rt_tb_list
        rt_title_text_list, rt_tr_prob_list = tr.get_title(rt_text_box_list)
        rt_title_text = " ".join(rt_title_text_list)
        rotated_set = [rt_title_text, np.mean(rt_td_prob_list), np.mean(rt_tr_prob_list)]
        # 시간 측정
        rt_time = time.time()
        print(f"Rotation Read: {rt_time-tr_time}, {len(rt_text_box_list)}")

        # 결과 확인
        res = sorted([original_set, rotated_set], key=lambda x: (x[2], x[1]), reverse=True)
        # 시간 측정
        res_time = time.time()
        print(f"Choice Read: {res_time-rt_time}")

        # print(res)
        # print()
        results.append(res)
        title_list.append(res[0][0])
        # yield res[0][0]
    print(f'Finish reading : {time.time()- total_st_time}초')
    return title_list

def get_title(cropped_img):
    tb_list, rt_tb_list = td.crop_all(cropped_img)

    # 원본 이미지
    text_box_list, td_prob_list, _etc_box, _etc_probs = tb_list
    title_text_list, tr_prob_list = tr.get_title(text_box_list)
    title_text = " ".join(title_text_list)
    original_set = [title_text, np.mean(td_prob_list), np.mean(tr_prob_list)]

    # 회전한 이미지
    rt_text_box_list, rt_td_prob_list, _rt_etc_box, _rt_etc_probs = rt_tb_list
    rt_title_text_list, rt_tr_prob_list = tr.get_title(rt_text_box_list)
    rt_title_text = " ".join(rt_title_text_list)
    rotated_set = [rt_title_text, np.mean(rt_td_prob_list), np.mean(rt_tr_prob_list)]

    # 결과 확인
    res = sorted([original_set, rotated_set], key=lambda x: (x[2], x[1]), reverse=True)
    # print(res)
    return res[0][0]