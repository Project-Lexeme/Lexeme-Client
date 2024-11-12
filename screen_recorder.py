import tkinter as tk
from tkinter import simpledialog
from tkinter import dialog
import pygetwindow as gw
import pyautogui
import time
import re
import threading
import config
import logger
import screenshot_text_extractor
import os


def clean_filename(title):
    # Replace invalid characters with underscores or remove them
    return re.sub(r'[<>:"/\\|?*. ]', '_', title)


class DrawRectangleApp:
    def __init__(self, root, left, top, width, height):
        self.root = root
        self.root.attributes("-topmost", True)  # Always on top
        self.root.attributes("-alpha", 0.5)     # Transparent background
        self.root.attributes("-fullscreen", True)
        
        self.canvas = tk.Canvas(root, bg='white', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.rect_start = None
        self.rect = None
        self.coords = None
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        
    def on_button_press(self, event):
        self.rect_start = (event.x, event.y)
        self.rect = self.canvas.create_rectangle(event.x, event.y, event.x, event.y, outline="blue", width=2)

    def on_mouse_drag(self, event):
        self.canvas.coords(self.rect, self.rect_start[0], self.rect_start[1], event.x, event.y)
    
    def on_button_release(self, event):
        self.rect_end = (event.x, event.y)
        start_x, start_y, end_x, end_y = self.rect_start[0], self.rect_start[1], event.x, event.y
        if self.rect_start[0] > event.x: # handles if rectangle was drawn with origin NOT at top-left
            start_x = event.x
            end_x = self.rect_start[0]
        if self.rect_start[1] > event.y:
            start_y = event.y
            end_y = self.rect_start[1]

        self.coords = (start_x, start_y, end_x, end_y)
        self.canvas.delete(self.rect)  # Remove the rectangle from the canvas
        self.root.destroy()  # Close the drawing window
        print(f"Rectangle coordinates per on_button_release: {self.rect_start}, {self.rect_end}")


def draw_rectangle(root):
    rect = DrawRectangleApp(root)
    root.mainloop()
    return 

class ScreenRecorder:
    def __init__(self, language, use_preprocessing, minimum_confidence, config, time_between_screencaps, use_comparative_preprocessing):
        self.is_recording = False
        self.record_thread = None
        self._recording_lock = threading.Lock()
        self.window_title = self.select_window()
        self.window = self.get_rectangle()
        self.language = language
        self.use_preprocessing = use_preprocessing
        self.minimum_confidence = minimum_confidence
        self.use_comparative_preprocessing = use_comparative_preprocessing
        self.filename = clean_filename(self.language + '' + self.window_title[:10] + str(time.localtime().tm_yday) + '' + str(time.localtime().tm_hour) + '' + str(time.localtime().tm_min)) + '.csv'  # TODO: think about how to create folder for this
        self.config = config
        self.time_between_screencaps = time_between_screencaps

    def get_rectangle(self):
        root = tk.Tk()
        window = gw.getWindowsWithTitle(self.window_title)[0]
        rect = DrawRectangleApp(root, window.left, window.top, window.width, window.height) # TODO: ensure 'left' and 'top' are actually left and top, i.e. user started at top-left corner
        root.mainloop()
        print(rect.coords)
        
        return rect.coords
    
    def capture_screen(self):
        while self.is_recording:
            try:
                if self.window:
                    left, top = self.window[0], self.window[1]
                    width, height = self.window[2] - self.window[0], self.window[3]-self.window[1]
                    screenshot = pyautogui.screenshot(region=(left, top, width, height))
                    screenshot.save(f"{os.getcwd()}/uploads/Screenshot.png")
            except Exception as e:
                print(f"Error taking screenshot: {e}")
            self.log_screencap_subtitles()
            time.sleep(self.time_between_screencaps)

    def select_window(self):
        def on_button_click(window_title):
            nonlocal selected_title
            selected_title = window_title
            root.destroy()  # Close the GUI after selection

        root = tk.Tk()
        root.title("Select Window to Capture")

        available_windows = gw.getAllTitles()
        selected_title = None  # Variable to hold the selected title

        # Create a button for each window title
        for title in available_windows:
            if len(title) > 3:
                button = tk.Button(root, text=title, command=lambda t=title: on_button_click(t))
                button.pack(pady=5)

        root.mainloop()  # Start the GUI event loop

        return selected_title  # Return the selected window title
    
    def start_recording(self):
        self.filename = self.prompt_for_filename()
        
        with self._recording_lock:
            if not self.is_recording:
                self.is_recording = True
                self.record_thread = threading.Thread(target=self.capture_screen, daemon=True)
                self.record_thread.start()
                return True
            return False
        
    def stop_recording(self):
        with self._recording_lock:
            if self.is_recording:
                self.is_recording = False
                if self.record_thread: 
                    self.record_thread.join(timeout=5)
                    self.record_thread = None
                return True
            return False
        
    def log_screencap_subtitles(self):
        if self.use_comparative_preprocessing == True:
            text = screenshot_text_extractor.comparative_read_text_from_image(filepath=f"{os.getcwd()}/uploads/Screenshot.png", language=self.language, minimum_confidence=self.minimum_confidence, config=self.config, display_comparison=False)
        else:
            text = screenshot_text_extractor.read_text_from_image(filepath=f"{os.getcwd()}/uploads/Screenshot.png", language=self.language, preprocessing=self.use_preprocessing, minimum_confidence=self.minimum_confidence, config=self.config)
        
        logger.log_subtitle(text, f'{config.get_data_directory()}\\subtitles\\{self.filename}')
        print(f'Saved screencapture subtitles to {config.get_data_directory()}\\subtitles\\{self.filename}')

    def prompt_for_filename(self):
        # Create the main window (but don't display it)
        root = tk.Tk()
        root.withdraw()  # Hide the main window

        filename = simpledialog.askstring("File Name", "Enter the file name:", initialvalue=self.filename)
        # Return the filename (could be None if user cancels)
        return filename

#this = ScreenRecorder(language='chi_sim', use_preprocessing=True, minimum_confidence=50, config=r'--oem 3 -l chi_sim', time_between_screencaps=1)