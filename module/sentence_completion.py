from transformers import AutoTokenizer, AutoModelForCausalLM, TextGenerationPipeline
import torch
import string
import re

device = 0 if torch.cuda.is_available() else -1

CHINESE_PUNCTUATION = "。？！，、；：“”‘’（）《》〈〉【】「」—…～·"

class SentenceBuffer:
    def __init__(self, model_name="uer/gpt2-distil-chinese-cluecorpussmall", device=device):
        # 모델 및 토크나이저 로드
        # self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        # self.model = AutoModelForCausalLM.from_pretrained(model_name).to("cpu")
        # self.text_generator = TextGenerationPipeline(self.model, self.tokenizer, device=device)
        self.buffer = []  # 텍스트 버퍼 초기화

    def remove_punctuation(self, text):
        """구두점 제거 함수"""
        return re.sub(r"[{}]".format(re.escape(string.punctuation)), "", text)

    def is_sentence_complete(self, new_text):
        """문장 완성 여부 확인 및 버퍼 관리"""
        # 버퍼에 새로운 텍스트 추가
        self.buffer.append(new_text)

        # # 텍스트 생성 방식
        # generated = self.text_generator(self.buffer, max_length=len(self.buffer) + 10, do_sample=False)
        # generated_text = self.remove_punctuation(generated[0]['generated_text'])

        # print(f">>>>    Buffer: {self.buffer}")
        # print(f">>>>    GENERA: {generated_text}")
        # if len(generated_text.strip()) == len(self.buffer.strip()):
        #     # 문장이 완성된 경우 버퍼 비우고 반환
        #     complete_sentence = self.buffer.strip()
        #     self.buffer = ""  # 버퍼 초기화
        #     return complete_sentence
        # else:
        #     # 문장이 미완성된 경우 버퍼 유지
        #     return None

        if len(self.buffer) == 3:
            complete_sentence = "".join(self.buffer)
            self.buffer.pop(0)
            return complete_sentence
        else:
            return None
