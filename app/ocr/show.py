import matplotlib.pyplot as plt
from PIL import Image, ImageOps
from matplotlib import font_manager, rc


# 한글 폰트를 설정 (Windows의 경우 맑은 고딕을 사용할 수 있습니다)
font_path = "C:/Windows/Fonts/malgun.ttf"  # Windows에서 한글 폰트 경로
font_name = font_manager.FontProperties(fname=font_path).get_name()
rc('font', family=font_name)

def show_image(img: Image.Image, caption=""):
    plt.imshow(img)
    plt.title(caption)
    plt.axis('off')
    plt.show()
    return

def show_images(cropped_img_list: list[Image.Image], captions=[]):
    
    if len(cropped_img_list) > 1:
        book_cnt = len(cropped_img_list)
        w, h = cropped_img_list[0].size

        height = 4
        if w < h:
            # 서브플롯 만들기
            fig, axes = plt.subplots(1, book_cnt, figsize=(height*book_cnt//3, height))
        else:
            fig, axes = plt.subplots(book_cnt, 1, figsize=(height, height*book_cnt//3))

        # 각 서브플롯에 이미지를 표시
        for i, (ax, img) in enumerate(zip(axes, cropped_img_list)):
            ax.imshow(img)
            if captions and i < len(captions):
                ax.set_title(captions[i])
            ax.axis('off')  # 축을 숨김
        # 이미지들 한 화면에 표시
        plt.show()
    elif len(cropped_img_list) == 1:
        if captions:
            show_image(cropped_img_list[0], captions[0])
        else:
            show_image(cropped_img_list[0])
    return