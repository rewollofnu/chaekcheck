from transformers import TrOCRProcessor, VisionEncoderDecoderModel, AutoTokenizer
import unicodedata

from PIL.Image import Image
import math
import torch


class TextReader():
    def __init__(self) -> None:
        self.processor_ko = TrOCRProcessor.from_pretrained("ddobokki/ko-trocr")
        self.model_ko = VisionEncoderDecoderModel.from_pretrained("ddobokki/ko-trocr")
        self.tokenizer_ko = AutoTokenizer.from_pretrained("ddobokki/ko-trocr")
        return
    
    def read_text(self, text_box: Image) -> str:
        pixel_values = self.processor_ko(text_box.convert('RGB'), return_tensors="pt").pixel_values
        outputs = self.model_ko.generate(pixel_values, max_length=64, output_scores=True, return_dict_in_generate=True)

        # generated token ids
        generated_ids = outputs.sequences

        # 텍스트로 변환
        generated_text = self.tokenizer_ko.batch_decode(generated_ids, skip_special_tokens=True)[0]
        generated_text = unicodedata.normalize("NFC", generated_text)

        # 소프트맥스를 적용하여 각 토큰에 대한 확률을 계산
        logits = outputs.scores
        probs = [torch.softmax(logit, dim=-1) for logit in logits]

        # 로그 확률과 토큰 개수 초기화
        log_probs = 0.0
        n_tokens = len(generated_ids[0])

        # 마지막 확률값은 다음 타임스텝에서 나오므로 probs는 len(generated_ids[0]) - 1이 됨
        for i in range(n_tokens - 1):
            token_id = generated_ids[0][i + 1]  # 다음 타임스텝의 토큰에 해당하는 확률
            token_prob = probs[i][0, token_id].item()  # 해당 토큰의 확률값
            log_probs += torch.log(probs[i][0, token_id])  # 로그 확률을 더함

        # 로그 확률의 평균 구하기 (기하평균은 로그 확률의 평균을 구한 후 다시 지수화)
        if n_tokens - 1 > 0:
            geometric_mean_log_prob = log_probs / (n_tokens - 1)
        else:
            geometric_mean_log_prob = 0.0
        geometric_mean_prob = torch.exp(geometric_mean_log_prob).item()

        # print(f"Recognized Text: {generated_text}")
        # print(f"Geometric Mean Probability of the sequence: {geometric_mean_prob}")
        return generated_text, geometric_mean_prob
    
    def read_title_boxes(self, title_boxes: list[Image]):
        title_text_list = []
        title_prob_list = []

        for tb in title_boxes:
            generated_text, geometric_mean_prob = self.read_text(tb)
            title_text_list.append(generated_text)
            title_prob_list.append(geometric_mean_prob)

        return title_text_list, title_prob_list
    
    def get_title(self, title_boxes: list[Image]):
        title_text_list, title_prob_list = self.read_title_boxes(title_boxes)
        return title_text_list, title_prob_list

if __name__ == "__main__":
    pass