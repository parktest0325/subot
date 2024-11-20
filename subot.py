import tkinter as tk
from module.ocr_scanner import open_ocr_window
from module.translator import open_subtitle_window
from module.debugger import open_debugtext_window
from module.custom_window import open_custom_window

WINDOW_WIDTH = 300
WINDOW_HEIGHT = 300

def main_control_board():
    root = tk.Tk()
    root.title("Main Control Board")
    root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")  # 기본 창 크기 설정

    # 버튼 상태를 관리할 변수 (재생: True, 정지: False)
    is_playing = tk.BooleanVar(value=False)

    def toggle_mode():
        """재생/정지 토글 버튼의 동작"""
        if is_playing.get():
            is_playing.set(False)
            toggle_button.config(text="Whisper Play", bg="green")
            print("Stopped")  # 실제 정지 동작 추가 가능
        else:
            is_playing.set(True)
            toggle_button.config(text="Whisper Stop", bg="red")
            print("Playing")  # 실제 재생 동작 추가 가능

    tk.Button(root, fg="white", bg="black", text="OCR Scanner", command=open_ocr_window).pack()
    tk.Button(root, fg="white", bg="black", text="Translator", command=open_subtitle_window).pack()
    tk.Button(root, fg="white", bg="black", text="DEBUG TEXT", command=open_debugtext_window).pack()
    tk.Button(root, fg="white", bg="black", text="Custom", command=open_custom_window).pack()

    # 재생/정지 토글 버튼
    toggle_button = tk.Button(
        root,
        fg="white",
        bg="green",
        text="Whisper Play",
        width=10,
        command=toggle_mode
    )
    toggle_button.pack()

    root.mainloop()

if __name__ == "__main__":
    main_control_board()
