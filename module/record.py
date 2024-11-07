import tkinter as tk
import cv2
import numpy as np
import pyautogui
import datetime

is_recording = False

def open_recording_window():
    global is_recording
    window = tk.Toplevel()
    window.title("Screen Recording")

    tk.Label(window, text="Save Path:").pack()
    save_path_entry = tk.Entry(window, width=50)
    save_path_entry.pack()

    def start_recording():
        global is_recording
        is_recording = True
        region = (100, 100, 640, 480)  # 녹화할 영역 (x, y, width, height)
        save_path = save_path_entry.get() or "recording"
        record_screen(region, save_path)

    def stop_recording():
        global is_recording
        is_recording = False

    tk.Button(window, text="Start Recording", command=start_recording).pack()
    tk.Button(window, text="Stop Recording", command=stop_recording).pack()

    window.mainloop()

def record_screen(region, save_path):
    global is_recording
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out = cv2.VideoWriter(f"{save_path}_{timestamp}.avi", fourcc, 20.0, (region[2], region[3]))

    while is_recording:
        img = pyautogui.screenshot(region=region)
        frame = np.array(img)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        out.write(frame)
    
    out.release()
