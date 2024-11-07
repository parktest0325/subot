import tkinter as tk
from module.ocr_capture import open_capture_window
from module.subtitle import open_subtitle_window
from module.record import open_recording_window
from module.extracted_text import open_text_display

def main_control_board():
    root = tk.Tk()
    root.title("Main Control Board")
    
    tk.Button(root, text="OCR Scanner", command=open_capture_window).pack()
    tk.Button(root, text="Screen Recording", command=open_recording_window).pack()
    tk.Button(root, text="Subtitle", command=open_subtitle_window).pack()
    tk.Button(root, text="DEBUG TEXT", command=open_text_display).pack()
    
    root.mainloop()

if __name__ == "__main__":
    main_control_board()
