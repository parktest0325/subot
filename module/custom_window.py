import tkinter as tk

TRANSPARENT_COLOR = "#FF00FF"

def create_title_bar(window, parent_frame, title_text, title_bg_color, title_text_color, title_height):
    # 타이틀 바 프레임 생성 및 그리드 배치 (패딩 제거)
    title_bar = tk.Frame(parent_frame, bg=title_bg_color, height=title_height)
    title_bar.grid(row=0, column=0, sticky='nsew', padx=0, pady=0)
    title_bar.grid_propagate(False)  # 프레임의 크기 고정

    # 그리드의 첫 번째 행을 고정 높이로 설정
    parent_frame.grid_rowconfigure(0, weight=0)
    parent_frame.grid_columnconfigure(0, weight=1)

    # 타이틀 텍스트
    title_font_size = min(12, title_height // 4)  # 폰트 크기를 title_height의 절반으로 설정, 최소 8, 최대 12
    title_font = ("Arial", title_font_size)
    title_label = tk.Label(title_bar, text=title_text, bg=title_bg_color, fg=title_text_color, font=title_font)
    title_label.pack(side=tk.LEFT, padx=5, pady=0, anchor='w')

    # 닫기 버튼
    close_button = tk.Button(
        title_bar, text="X", command=window.destroy,
        bg=title_bg_color, fg=title_text_color, bd=0,
        font=title_font, activebackground=title_bg_color, activeforeground=title_text_color
    )
    close_button.pack(side=tk.RIGHT, padx=5, pady=0, anchor='e')

    # 창 이동 기능
    def start_move(event):
        window.start_x = event.x_root
        window.start_y = event.y_root

    def do_move(event):
        deltax = event.x_root - window.start_x
        deltay = event.y_root - window.start_y
        new_x = window.winfo_x() + deltax
        new_y = window.winfo_y() + deltay
        window.geometry(f"+{new_x}+{new_y}")
        window.start_x = event.x_root
        window.start_y = event.y_root

    # 이동 이벤트 바인딩
    title_bar.bind("<ButtonPress-1>", start_move)
    title_bar.bind("<B1-Motion>", do_move)

    def toggle_title_bar(show):
        """타이틀 바 표시/숨김 토글"""
        if show:
            # 타이틀 바를 보이게 설정
            title_bar.config(bg=title_bg_color)
            for widget in title_bar.winfo_children():
                widget.pack(side=tk.LEFT if widget == title_label else tk.RIGHT, padx=5)
        else:
            # 타이틀 바를 숨기면서 배경을 투명하게 설정
            title_bar.config(bg=TRANSPARENT_COLOR)
            for widget in title_bar.winfo_children():
                widget.pack_forget()

    # 마우스 이벤트를 통한 타이틀 바 표시/숨김
    window.bind("<Enter>", lambda event: toggle_title_bar(True))
    window.bind("<Leave>", lambda event: toggle_title_bar(False))

    # 초기 상태로 타이틀 바 숨기기
    toggle_title_bar(False)

    return title_bar

def create_capture_frame(window, parent_frame, window_width, window_height, window_min_width, window_min_height, title_height, border_color, border_width):
    """커스텀 프레임 생성"""
    # 캔버스 생성 (테두리 및 하이라이트 제거)
    canvas = tk.Canvas(parent_frame, bg=TRANSPARENT_COLOR, highlightthickness=0, borderwidth=0)
    canvas.grid(row=1, column=0, sticky='nsew', padx=0, pady=0)

    # 그리드의 두 번째 행을 확장 가능하도록 설정
    parent_frame.grid_rowconfigure(1, weight=1)

    # 테두리 그리기 함수
    def draw_border(width, height):
        canvas.delete('all')
        canvas.create_rectangle(
            border_width, border_width,
            width - border_width, height - border_width,
            outline=border_color, width=border_width
        )

    # 초기 테두리 그리기
    draw_border(window_width, window_height - title_height)

    def start_resize(event):
        window.current_width = window.winfo_width()
        window.current_height = window.winfo_height()
        window.start_x = event.x_root
        window.start_y = event.y_root

    def do_resize(event):
        deltax = event.x_root - window.start_x
        deltay = event.y_root - window.start_y
        new_width = max(window.current_width + deltax, window_min_width)
        new_height = max(window.current_height + deltay, window_min_height)
        window.geometry(f"{new_width}x{new_height}")
        draw_border(new_width, new_height - title_height)

    # 리사이즈 이벤트 바인딩
    canvas.bind("<ButtonPress-1>", start_resize)
    canvas.bind("<B1-Motion>", do_resize)
    return canvas

def open_custom_window(title_text="커스텀 창", title_bg_color="gray", title_text_color="white", title_height=32, window_width=400, window_height=300, window_min_width=100, window_min_height=100, border_color="red", border_width=3):
    """커스텀 창 열기"""
    # 새 창 생성
    window = tk.Toplevel()
    window.overrideredirect(True)  # 기본 타이틀 바 제거
    window.geometry(f"{window_width}x{window_height}")
    window.attributes("-topmost", True)
    window.attributes("-transparentcolor", TRANSPARENT_COLOR)
    window.wm_minsize(window_min_width, window_min_height)
    window.config(bg=TRANSPARENT_COLOR)

    # 컨테이너 프레임 생성 및 패딩 제거
    parent_frame = tk.Frame(window, bg=TRANSPARENT_COLOR)
    parent_frame.pack(fill='both', expand=True, padx=0, pady=0)

    # 그리드 설정
    parent_frame.grid_rowconfigure(0, minsize=title_height, weight=0)
    parent_frame.grid_rowconfigure(1, weight=1)
    parent_frame.grid_columnconfigure(0, weight=1)

    # 타이틀 바와 캡처 프레임 생성
    title_bar = create_title_bar(window, parent_frame, title_text, title_bg_color, title_text_color, title_height)
    canvas = create_capture_frame(window, parent_frame, window_width, window_height, window_min_width, window_min_height, title_height, border_color, border_width)
    return window, canvas