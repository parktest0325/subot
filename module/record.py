import tkinter as tk
import cv2
import numpy as np
import pyautogui
import datetime
import os
import threading
import time

# 상수 및 글로벌 변수 설정
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
BORDER_SIZE = 5
is_recording = False
FRAME_RATE = 60

# 저장 디렉토리 설정
save_dir = "recordings"
os.makedirs(save_dir, exist_ok=True)

def open_recording_window():
    global is_recording
    window = tk.Toplevel()
    window.title("Screen Recording")
    window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
    window.attributes("-topmost", True)
    window.resizable(True, True)
    window.attributes("-transparentcolor", "white")

    # 컨트롤 프레임 생성: 저장 경로 입력 및 버튼들 포함 (상단 배치)
    control_frame = tk.Frame(window)
    control_frame.pack(fill="x", padx=10, pady=5)

    # 저장 경로 입력 필드 및 버튼 추가
    tk.Label(control_frame, text="Save Path:").grid(row=0, column=0, sticky="w", padx=5)
    save_path_entry = tk.Entry(control_frame, width=30)
    save_path_entry.grid(row=0, column=1, padx=5)

    # Start/Stop 버튼
    start_button = tk.Button(control_frame, text="Start Recording", bg="lightgray", fg="black",
                             activebackground="green", activeforeground="white",
                             command=lambda: start_recording(capture_frame, save_path_entry, start_button, stop_button))
    stop_button = tk.Button(control_frame, text="Stop Recording", bg="lightgray", fg="black",
                            activebackground="red", activeforeground="white",
                            command=lambda: stop_recording(capture_frame, start_button))
    start_button.grid(row=0, column=2, padx=5)
    stop_button.grid(row=0, column=3, padx=5)

    # 녹화 영역 지정 프레임 생성 (하단 배치)
    capture_frame = tk.Frame(window, bg="white", highlightbackground="gray", highlightthickness=BORDER_SIZE)
    capture_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def calculate_window_dimensions():
        global window_default_height, window_default_width
        window_default_height = window.winfo_rooty() - window.winfo_y()
        window_default_width = window.winfo_rootx() - window.winfo_x()
        print("Titlebar Height:", window_default_height, "Border Width:", window_default_width)

    window.after(10, calculate_window_dimensions)

    def update_capture_frame(event):
        # 프레임 크기를 창 크기에 맞춰 업데이트 (테두리 두께 고려)
        new_width = window.winfo_width() - 20
        new_height = window.winfo_height() - 120
        capture_frame.config(width=new_width, height=new_height)

    window.bind("<Configure>", update_capture_frame)

    window.mainloop()

def start_recording(capture_frame, save_path_entry, start_button, stop_button):
    global is_recording, window_default_height, window_default_width
    is_recording = True

    # 테두리 색상 변경 (녹화 중 빨간색)
    capture_frame.config(highlightbackground="red")

    # 버튼 색상 변경
    start_button.config(bg="black", fg="white")
    stop_button.config(bg="lightgray", fg="black")

    # 파일 저장 경로 설정
    save_path = save_path_entry.get() or "recording"
    
    # 녹화를 별도의 스레드에서 실행
    recording_thread = threading.Thread(target=record_screen, args=(capture_frame, os.path.join(save_dir, save_path)))
    recording_thread.start()

def stop_recording(capture_frame, start_button):
    global is_recording
    is_recording = False

    # 버튼 색상 변경
    start_button.config(bg="lightgray", fg="black")
    # 테두리 색상 변경 (녹화 중지 회색)
    capture_frame.config(highlightbackground="gray")

def record_screen(capture_frame, save_path):
    global is_recording
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out = cv2.VideoWriter(f"{save_path}_{timestamp}.avi", fourcc, FRAME_RATE, 
                          (capture_frame.winfo_width() - 2 * BORDER_SIZE, capture_frame.winfo_height() - 2 * BORDER_SIZE))

    # 각 프레임 간 시간 간격 계산
    frame_interval_ms = int(1000 / FRAME_RATE)  # 밀리초 단위

    while is_recording:
        # 현재 위치와 크기를 동적으로 계산
        x = capture_frame.winfo_rootx() + BORDER_SIZE
        y = capture_frame.winfo_rooty() + BORDER_SIZE
        width = capture_frame.winfo_width() - 2 * BORDER_SIZE
        height = capture_frame.winfo_height() - 2 * BORDER_SIZE
        region = (x, y, width, height)

        # 스크린샷 캡처 및 영상으로 변환
        img = pyautogui.screenshot(region=region)
        frame = np.array(img)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        out.write(frame)

        # OpenCV의 waitKey를 사용하여 프레임 간 간격 유지
        if cv2.waitKey(frame_interval_ms) & 0xFF == ord('q'):
            break
    
    out.release()
