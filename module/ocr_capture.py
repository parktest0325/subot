import tkinter as tk
import pytesseract
import pyautogui
from module.extracted_text import update_text_display
import threading
import time
import os

WINDOW_WIDTH = 400
WINDOW_HEIGHT = 300
BORDER_SIZE = 5
pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'
window_default_height = 0  # 초기화
window_default_width = 0  # 초기화

# 스크린샷 저장 디렉토리 및 카운트 설정
# save_dir = "screenshots"
# os.makedirs(save_dir, exist_ok=True)  # 저장할 디렉토리 생성
# screenshot_count = 1

def open_capture_window():
    global screenshot_count, titlebar_height
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

    # 타이틀바와 테두리 두께 계산
    def calculate_window_dimensions():
        global window_default_height, window_default_width
        window_default_height = window.winfo_rooty() - window.winfo_y()
        window_default_width = window.winfo_rootx() - window.winfo_x()
        print("Titlebar Height:", window_default_height, "Border Width:", window_default_width)

    # 창이 렌더링된 후 타이틀바 높이를 계산
    window.after(10, calculate_window_dimensions)

    def update_capture_frame(event):
        # 창 크기 변경 시 capture_frame 크기 업데이트
        new_width = window.winfo_width()
        new_height = window.winfo_height()
        capture_frame.place(width=new_width, height=new_height)

    # 창 크기 변경 시 update_capture_frame 호출
    window.bind("<Configure>", update_capture_frame)

    def continuous_ocr():
        global screenshot_count, window_default_height, window_default_width
        # 창이 열려 있는 동안 OCR 수행
        while window.winfo_exists():
            try:
                x = window.winfo_x() + window_default_width + BORDER_SIZE       # -1  테스트를 위해 1px 테두리 보이도록
                y = window.winfo_y() + window_default_height + BORDER_SIZE      # -1
                width = capture_frame.winfo_width() - BORDER_SIZE * 2   # +2
                height = capture_frame.winfo_height() - BORDER_SIZE * 2 # +2
                region = (x, y, width, height)

                screenshot = pyautogui.screenshot(region=region)
                text = pytesseract.image_to_string(screenshot)

                # [TEST] 스크린샷 저장
                # file_path = os.path.join(save_dir, f"screenshot{screenshot_count}.png")
                # screenshot.save(file_path)
                # screenshot_count += 1

                # OCR 결과를 update_text_display에 표시
                print(text)
                update_text_display(text)
                time.sleep(1)
            except tk.TclError:
                # 창이 닫히면 발생하는 예외를 무시하고 루프 종료
                print("Window closed. Stopping OCR.")
                break

    # 창이 닫힐 때 스레드 종료
    def on_close():
        window.destroy()  # 창 닫기

    window.protocol("WM_DELETE_WINDOW", on_close)
    # OCR 작업을 별도 스레드로 실행
    ocr_thread = threading.Thread(target=continuous_ocr, daemon=True)
    ocr_thread.start()

    window.mainloop()
