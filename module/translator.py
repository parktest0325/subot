import tkinter as tk
from transformers import pipeline
import torch
import threading

# GPU 사용 가능 시 GPU 설정
device = 0 if torch.cuda.is_available() else -1  # GPU 사용 가능 시 device=0, 아니면 CPU(-1)

# NLLB-200 모델을 위한 pipeline 초기화
translator = pipeline("translation", model="facebook/nllb-200-distilled-600M", device=device)

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 300

translated_text_label = None
last_text = ""  # 이전 텍스트를 저장할 전역 변수

def open_subtitle_window():
    print(torch.cuda.is_available())
    """번역된 텍스트를 표시하는 창을 엽니다."""
    global translated_text_widget
    window = tk.Toplevel()
    window.title("Translated Text")
    window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

    # 스크롤 가능한 텍스트 위젯 생성
    translated_text_widget = tk.Text(window, wrap="word", font=("Helvetica", 18), padx=20, pady=20)
    translated_text_widget.pack(fill="both", expand=True)

    # 텍스트 위젯의 스크롤바 설정
    scrollbar = tk.Scrollbar(translated_text_widget)
    translated_text_widget.config(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    scrollbar.config(command=translated_text_widget.yview)

    def on_close():
        """창이 닫힐 때 번역 텍스트 위젯을 초기화합니다."""
        global translated_text_widget
        translated_text_widget = None
        window.destroy()

    window.protocol("WM_DELETE_WINDOW", on_close)

def update_translator_text(text):
    """텍스트가 변경되었을 때 번역하여 창에 표시합니다."""
    global last_text
    if text != last_text:
        last_text = text  # 현재 텍스트를 last_text에 저장
        # 번역을 별도의 스레드에서 수행
        threading.Thread(target=perform_translation, args=(text,)).start()

def perform_translation(text):
    """텍스트를 번역하고 결과를 업데이트합니다."""
    try:
        translated_text = translate(text)
    except Exception as e:
        translated_text = f"번역 중 오류 발생: {e}"
    
    if translated_text_widget:
        # 이전 번역된 텍스트를 위쪽에 유지하고, 새로운 텍스트를 추가
        translated_text_widget.after(0, lambda: append_translated_text(translated_text))

def append_translated_text(translated_text):
    """새 번역을 추가하고, 텍스트 위젯의 맨 아래로 자동 스크롤합니다."""
    translated_text_widget.insert("end", translated_text + "\n\n")  # 새 번역 추가
    translated_text_widget.see("end")  # 새 번역이 보이도록 자동 스크롤
    
def translate(text, target_lang='kor_Hang'):
    """주어진 텍스트를 번역하여 반환합니다."""
    if not text.strip():
        return ""
    
    # pipeline에서 번역 수행
    translated_result = translator(text, src_lang="zho_Hans", tgt_lang=target_lang)
    translated_text = translated_result[0]['translation_text']
    return translated_text
