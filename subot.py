import tkinter as tk
from module.ocr_scanner import open_ocr_window
from module.translator import open_subtitle_window
from module.record import open_recording_window
from module.debugger import open_debugtext_window

WINDOW_WIDTH = 300
WINDOW_HEIGHT = 200

def main_control_board():
    root = tk.Tk()
    root.title("Main Control Board")
    root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")  # 기본 창 크기 설정
    
    tk.Button(root, fg="white", bg="black" ,text="OCR Scanner", command=open_ocr_window).pack()
    # tk.Button(root, fg="white", bg="black" , text="Screen Recording", command=open_recording_window).pack()
    tk.Button(root, fg="white", bg="black" , text="Translator", command=open_subtitle_window).pack()
    tk.Button(root, fg="white", bg="black" , text="DEBUG TEXT", command=open_debugtext_window).pack()
    
    root.mainloop()

if __name__ == "__main__":
    main_control_board()
