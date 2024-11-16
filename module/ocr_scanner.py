import tkinter as tk
import pyautogui
from module.debugger import update_debugger_text
from module.translator import update_translator_text
import threading
import time
import numpy as np
import module.custom_window as custom_window

from paddleocr import PaddleOCR

WINDOW_WIDTH = 400
WINDOW_HEIGHT = 300
BORDER_WIDTH = 3
BORDER_COLOR = "green"

ocr = PaddleOCR(use_angle_cls=True, lang='ch', use_gpu=True) 

def open_ocr_window():
    window, canvas = custom_window.open_custom_window(title_text="OCR Scanner", window_width=WINDOW_WIDTH, window_height=WINDOW_HEIGHT, border_color=BORDER_COLOR, border_width=BORDER_WIDTH)

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
        previous_screen = None
        while window.winfo_exists():
            try:
                x = canvas.winfo_rootx()
                y = canvas.winfo_rooty()
                width = canvas.winfo_width()
                height = canvas.winfo_height()
                region = (x, y, width, height)

                screenshot = pyautogui.screenshot(region=region)
                if screenshot != previous_screen:
                    previous_screen = screenshot
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

    # OCR 작업을 별도 스레드로 실행
    ocr_thread = threading.Thread(target=continuous_ocr, daemon=True)
    ocr_thread.start()
