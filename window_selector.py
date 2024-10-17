import tkinter as tk
import pygetwindow as gw
import pyautogui
import time
import re
import threading
import asyncio


def clean_filename(title):
    # Replace invalid characters with underscores or remove them
    return re.sub(r'[<>:"/\\|?*.]', '_', title)

def capture_window(window_title):
    try:
        print("0")
        print(f"{gw.getWindowsWithTitle(window_title)}")
        window = gw.getWindowsWithTitle(window_title)[0]
        print("1")
        window.activate()
        print("2")
        time.sleep(1)
        screenshot = pyautogui.screenshot(region=(window.left, window.top, window.width, window.height))
        print("3")
        current_time = time.localtime()
        print("4")
        current_time = time.strftime("%H:%M:%S", current_time)
        filename = window_title[:20] + current_time
        filename = clean_filename(filename)
        screenshot.save(f"E:/projectlexeme_server/uploads/Screenshot.png")
        print(f"Screenshot saved at /uploads/Screenshot.png")
    except IndexError:
        print(f"Window with title '{window_title}' not found.")

    asyncio.sleep(3)




class ScreenRecorder:
    def __init__(self):
        self.is_recording = False
        self.record_thread = None
        self._recording_lock = threading.Lock()
        self.window_title = self.select_window()
        self.window = gw.getWindowsWithTitle(self.window_title)[0]

    def capture_screen(self):
        while self.is_recording:
            try:
                if self.window:
                    left, top = self.window.left, self.window.top
                    width, height = self.window.width, self.window.height

                    
                    screenshot = pyautogui.screenshot(region=(left, top, left + width, top + height))
                    current_time = time.localtime()
                    current_time = time.strftime("%H:%M:%S", current_time)
                    filename = self.window_title[:20] + current_time
                    filename = clean_filename(filename)
                    screenshot.save(f"E:/projectlexeme_server/uploads/Screenshot.png")
                    #print(f"Screenshot saved at /uploads/Screenshot.png")
            except Exception as e:
                print(f"Error taking screenshot: {e}")
            
            time.sleep(3)

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