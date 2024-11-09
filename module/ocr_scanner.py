import tkinter as tk
# import pytesseract
# from PIL import ImageTk, Image, ImageDraw
# import os
import hashlib
import pyautogui
from module.debugger import update_debugger_text
from module.translator import update_translator_text
import threading
import time
import numpy as np

from paddleocr import PaddleOCR

WINDOW_WIDTH = 400
WINDOW_HEIGHT = 300
BORDER_SIZE = 5

# pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'
ocr = PaddleOCR(use_angle_cls=True, lang='ch', use_gpu=False) 

window_default_height = 0  # 초기화
window_default_width = 0  # 초기화

# 스크린샷 저장 디렉토리 및 카운트 설정
# save_dir = "screenshots"
# os.makedirs(save_dir, exist_ok=True)  # 저장할 디렉토리 생성
# screenshot_count = 1

def open_ocr_window():
    global window_default_width, window_default_height #, screenshot_count
    # 기본 설정
    window = tk.Toplevel()
    window.title("Screen Capture")
    window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
    window.attributes("-topmost", True)  # 항상 위에 표시
    window.resizable(True, True)  # 창 크기 조절 가능하도록 설정
    window.attributes("-transparentcolor", "white")  # 흰색을 투명하게 설정

    # OCR 영역을 나타내는 Frame 생성
    capture_frame = tk.Frame(window, bg="white", highlightbackground="green", highlightthickness=BORDER_SIZE)
    capture_frame.place(width=WINDOW_WIDTH, height=WINDOW_HEIGHT)  # 초기 위치 및 크기 설정

    # 창이 렌더링되기까지 대기
    # 렌더링 되기 전에 창 크기를 가져오면 0px로 나옴
    window.wait_visibility()
    # print("winfo_rooty:", window.winfo_rooty(), "y:", window.winfo_y())
    window_default_height = window.winfo_rooty() - window.winfo_y()
    window_default_width = window.winfo_rootx() - window.winfo_x()
    # print("Titlebar Height:", window_default_height, "Border Width:", window_default_width)

    def update_capture_frame(event):
        # 창 크기 변경 시 capture_frame 크기 업데이트
        new_width = window.winfo_width()
        new_height = window.winfo_height()
        capture_frame.place(width=new_width, height=new_height)

    # 창 크기 변경 시 update_capture_frame 호출
    window.bind("<Configure>", update_capture_frame)

    def calculate_image_hash(image):
        """이미지의 해시 값을 계산하여 반환합니다."""
        image_bytes = image.tobytes()  # 이미지 데이터를 바이트로 변환
        return hashlib.md5(image_bytes).hexdigest()  # MD5 해시 계산

    # OCR 후처리 함수 인식한 텍스트 size로 필터링
    def ocr_filter(results, min_width=40, min_height=45, min_confidence=0.6):
        """글자 크기와 신뢰도에 따른 필터링된 OCR 결과만 반환합니다."""
        filtered_results = []
        for line in results[0]:  # 각 라인에서 텍스트 정보 추출
            box, (text, confidence) = line[0], line[1]
            box_width = box[2][0] - box[0][0]
            box_height = box[2][1] - box[0][1]
            
            # 크기와 신뢰도 기준을 모두 만족하는 텍스트만 추가
            if box_width >= min_width and box_height >= min_height and confidence >= min_confidence:
                filtered_results.append(text)
        return filtered_results

    def continuous_ocr():
        global window_default_height, window_default_width #, screenshot_count

        # 창이 열려 있는 동안 OCR 수행
        previous_hash = None
        while window.winfo_exists():
            try:
                x = window.winfo_x() + window_default_width + BORDER_SIZE       # -1  테스트를 위해 1px 테두리 보이도록
                y = window.winfo_y() + window_default_height + BORDER_SIZE      # -1
                width = max(0, capture_frame.winfo_width() - BORDER_SIZE * 2)   # +2
                height = max(0, capture_frame.winfo_height() - BORDER_SIZE * 2) # +2
                region = (x, y, width, height)

                # 현재 스크린샷의 해시 값 계산
                screenshot = pyautogui.screenshot(region=region)
                current_hash = calculate_image_hash(screenshot)
                if current_hash != previous_hash:
                    previous_hash = current_hash
                    screenshot_np = np.array(screenshot)
                    result = ocr.ocr(screenshot_np) #, cls=True)  # cls=True로 설정하면 각 문자 회전각도 감지 및 보정. 자막이라 필요없다.
                    if result and result[0]:
                        filtered_texts = ocr_filter(result)
                        text = "\n".join(filtered_texts)
                        # text = pytesseract.image_to_string(screenshot)

                        # [TEST] 스크린샷 저장
                        # file_path = os.path.join(save_dir, f"screenshot{screenshot_count}.png")
                        # screenshot.save(file_path)
                        # screenshot_count += 1

                        # OCR 결과를 update_text_display에 표시하고 Translator로 전달 
                        # print(text)

                        # 검출된 영역 주변에 사각형 그릴 수 있으면 좋겠지만 Frame에서는 안되는 것 같다

                        # 결과 업데이트 
                        update_debugger_text(text)
                        update_translator_text(text)
                time.sleep(1)
            except tk.TclError as e:
                print("...", e)
                break

    # 창이 닫힐 때 스레드 종료
    def on_close():
        window.destroy()  # 창 닫기

    window.protocol("WM_DELETE_WINDOW", on_close)
    # OCR 작업을 별도 스레드로 실행
    ocr_thread = threading.Thread(target=continuous_ocr, daemon=True)
    ocr_thread.start()

    window.mainloop()
