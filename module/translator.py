import tkinter as tk
# from transformers import MarianMTModel, MarianTokenizer
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer
import torch
import threading

# 번역된 텍스트 레이블을 전역 변수로 관리
translated_text_label = None

# 중국어에서 영어로 번역하는 모델 초기화
# model_name = 'Helsinki-NLP/opus-mt-en-ko'
# tokenizer = MarianTokenizer.from_pretrained(model_name)
# model = MarianMTModel.from_pretrained(model_name)
model_name = 'facebook/m2m100_418M'
tokenizer = M2M100Tokenizer.from_pretrained(model_name)
model = M2M100ForConditionalGeneration.from_pretrained(model_name)

# GPU 사용 가능 시 GPU로 모델 이동
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

WINDOW_WIDTH = 400
WINDOW_HEIGHT = 300

def open_subtitle_window():
    """번역된 텍스트를 표시하는 창을 엽니다."""
    global translated_text_label
    window = tk.Toplevel()
    window.title("Translated Text")
    window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

    translated_text_label = tk.Label(window, text="", wraplength=300, font=("Helvetica", 14), justify="left")
    translated_text_label.pack(padx=20, pady=20)

    def on_close():
        """창이 닫힐 때 번역 텍스트 레이블을 초기화합니다."""
        global translated_text_label
        translated_text_label = None
        window.destroy()

    window.protocol("WM_DELETE_WINDOW", on_close)

def update_translator_text(text):
    """텍스트를 번역하여 창에 표시합니다."""
    global translated_text_label
    if translated_text_label:
        translated_text_label.config(text="번역 중...")
        # 번역을 별도의 스레드에서 수행
        threading.Thread(target=perform_translation, args=(text,)).start()

def perform_translation(text):
    """텍스트를 번역하고 결과를 업데이트합니다."""
    try:
        translated_text = translate(text)
    except Exception as e:
        translated_text = f"번역 중 오류 발생: {e}"
    
    # GUI 업데이트는 메인 스레드에서 수행
    if translated_text_label:
        # Tkinter는 메인 스레드에서만 GUI 업데이트가 가능하므로, after 메서드를 사용
        translated_text_label.after(0, lambda: translated_text_label.config(text=translated_text))

def translate(text, target_lang='ko'):
    """주어진 텍스트를 번역하여 반환합니다."""
    if not text.strip():
        return ""
    # 소스 언어 설정 (자동 감지 가능)
    # M2M-100은 소스 언어를 자동 감지할 수 있지만, 명시적으로 설정할 수도 있습니다.
    # 예: 영어에서 한국어로 번역
    src_lang = "en"  # 소스 언어 코드 (예: 영어)
    tgt_lang = target_lang  # 타겟 언어 코드 (예: 한국어)

    tokenizer.src_lang = src_lang
    encoded = tokenizer(text, return_tensors="pt").to(device)
    generated_tokens = model.generate(**encoded, forced_bos_token_id=tokenizer.get_lang_id(tgt_lang))
    translated_text = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]
    return translated_text

def create_translation_window():
    """번역 창을 생성합니다."""
    window = tk.Toplevel()
    window.title("AI Translator")
    window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

    # 입력 텍스트 라벨 및 텍스트 박스
    input_label = tk.Label(window, text="번역할 중국어 텍스트:", font=("Helvetica", 12))
    input_label.pack(pady=10)

    input_text = tk.Text(window, height=5, width=50, font=("Helvetica", 12))
    input_text.pack(padx=20)

    # 번역된 텍스트를 표시할 창 열기 버튼
    show_button = tk.Button(window, text="번역된 텍스트 보기", font=("Helvetica", 12),
                            command=open_subtitle_window)
    show_button.pack(pady=10)

    # 텍스트 변경 시 자동 번역 기능 추가
    def on_text_change(event=None):
        """텍스트가 변경될 때 호출되는 함수."""
        text = input_text.get("1.0", tk.END).strip()
        update_translator_text(text)

    # 텍스트 변경을 감지하기 위해 KeyRelease 이벤트에 바인딩
    input_text.bind("<KeyRelease>", on_text_change)

    return window
