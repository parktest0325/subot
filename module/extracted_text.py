import tkinter as tk

text_label = None

WINDOW_WIDTH = 400
WINDOW_HEIGHT = 300

def open_text_display():
    global text_label
    window = tk.Toplevel()
    window.title("DEBUG TEXT")
    window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

    text_label = tk.Label(window, text="", wraplength=300)
    text_label.pack()

    # 창이 닫힐 때 스레드 종료
    def on_close():
        global text_label
        text_label = None
        window.destroy()  # 창 닫기

    window.protocol("WM_DELETE_WINDOW", on_close)

def update_text_display(text):
    if text_label:
        text_label.config(text=text)