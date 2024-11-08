from google_trans_new import google_translator
import tkinter as tk
from module.extracted_text import text_label

translator = google_translator()

def open_subtitle_window():
    window = tk.Toplevel()
    window.title("Subtitle Translation")

    tk.Label(window, text="Original Text:").pack()
    original_text_label = tk.Label(window, text="", wraplength=300)
    original_text_label.pack()

    tk.Label(window, text="Translated Text:").pack()
    translated_text_label = tk.Label(window, text="", wraplength=300)
    translated_text_label.pack()

    def translate_text():
        original_text = text_label.cget("text") if text_label else ""
        if original_text:
            translated_text = translate(original_text, "cn", "kr")
            translated_text_label.config(text=translated_text)

    tk.Button(window, text="Translate", command=translate_text).pack()

    window.mainloop()

def translate(text, source_lang="cn", target_lang="kr"):
    result = translator.translate(text, src=source_lang, dest=target_lang)
    return result.text
