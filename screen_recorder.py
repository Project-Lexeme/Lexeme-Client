import tkinter as tk
import pygetwindow as gw
import pyautogui
import time
import re
import threading
import logger
import screenshot_text_extractor


def clean_filename(title):
    # Replace invalid characters with underscores or remove them
    return re.sub(r'[<>:"/\\|?*.]', '_', title)





class ScreenRecorder:
    def __init__(self, language, use_preprocessing, minimum_confidence, config, time_between_screencaps):
        self.is_recording = False
        self.record_thread = None
        self._recording_lock = threading.Lock()
        self.window_title = self.select_window()
        self.window = gw.getWindowsWithTitle(self.window_title)[0]
        self.language = language
        self.use_preprocessing = use_preprocessing
        self.minimum_confidence = minimum_confidence
        self.filename = clean_filename(self.window_title[:20] + str(time.localtime().tm_yday) + str(time.localtime().tm_hour)+ str(time.localtime().tm_min))
        self.config = config
        self.time_between_screencaps = time_between_screencaps

    def capture_screen(self):
        while self.is_recording:
            try:
                if self.window:
                    left, top = self.window.left, self.window.top
                    width, height = self.window.width, self.window.height
                    screenshot = pyautogui.screenshot(region=(left, top, width, height))
                    current_time = time.localtime()
                    current_time = time.strftime("%H:%M:%S", current_time)
                    filename = self.window_title[:20] + current_time
                    filename = clean_filename(filename)
                    screenshot.save(f"E:/projectlexeme_server/uploads/Screenshot.png")
                    #print(f"Screenshot saved at /uploads/Screenshot.png")
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
        text = screenshot_text_extractor.read_text_from_image(filepath=f"E:/ProjectLexeme_Server/uploads/Screenshot.png", language=self.language, preprocessing=self.use_preprocessing, minimum_confidence=self.minimum_confidence, config=self.config)
        logger.log_subtitle(text, self.filename)