import customtkinter as ctk
from tkinter import simpledialog  # CustomTkinter does not have its own dialogs yet, so we still use this
import pygetwindow as gw
import pyautogui
import time
import re
import threading
import config
import logger
import prompt_generator
import screenshot_text_extractor
import os

import startup


def clean_filename(title) -> str:  # Replace invalid characters with underscores or remove them
    return re.sub(r'[<>:"/\\|?*. ]', '_', title)

class DrawRectangleApp:
    def __init__(self, root, left, top, width, height) -> None:
        self.root = root
        self.root.attributes("-topmost", True)  # Always on top
        self.root.attributes("-alpha", 0.5)     # Transparent background
        self.root.attributes("-fullscreen", True)

        self.canvas = ctk.CTkCanvas(root, bg='white', highlightthickness=0)
        self.canvas.pack(fill=ctk.BOTH, expand=True)

        self.rect_start = None
        self.rect = None
        self.coords = None
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

    def on_button_press(self, event) -> None:
        self.rect_start = (event.x, event.y)
        self.rect = self.canvas.create_rectangle(event.x, event.y, event.x, event.y, outline="blue", width=2)

    def on_mouse_drag(self, event) -> None:
        self.canvas.coords(self.rect, self.rect_start[0], self.rect_start[1], event.x, event.y)

    def on_button_release(self, event) -> None:
        self.rect_end = (event.x, event.y)
        start_x, start_y, end_x, end_y = self.rect_start[0], self.rect_start[1], event.x, event.y
        if self.rect_start[0] > event.x:  # handles if rectangle was drawn with origin NOT at top-left
            start_x = event.x
            end_x = self.rect_start[0]
        if self.rect_start[1] > event.y:
            start_y = event.y
            end_y = self.rect_start[1]

        self.coords = (start_x, start_y, end_x, end_y)
        self.canvas.delete(self.rect)  # Remove the rectangle from the canvas
        self.root.destroy()  # Close the drawing window
        print(f"Rectangle coordinates per on_button_release: {self.rect_start}, {self.rect_end}")


def draw_rectangle(root) -> None:
    rect = DrawRectangleApp(root)
    root.mainloop()
    return


class ScreenRecorder:
    def __init__(self, language, nlp, preprocessors, minimum_confidence, config, time_between_screencaps, use_comparative_preprocessing) -> None:
        '''
        language: 
        '''
        
        self.is_recording = False
        self.record_thread = None
        self._recording_lock = threading.Lock()
        self.window_title = self.select_window()
        self.window = self.get_rectangle()
        self.language = language
        self.preprocessors = preprocessors
        self.minimum_confidence = minimum_confidence
        self.use_comparative_preprocessing = use_comparative_preprocessing
        self.filename = clean_filename(self.language + '' + self.window_title[:10] + str(time.localtime().tm_yday) + '' + str(time.localtime().tm_hour) + '' + str(time.localtime().tm_min)) + '.csv'
        self.config = config
        self.time_between_screencaps = time_between_screencaps
        self.nlp = nlp

    def get_rectangle(self) -> tuple[int, int, int, int]:
        root = ctk.CTk()
        window = gw.getWindowsWithTitle(self.window_title)[0]
        rect = DrawRectangleApp(root, window.left, window.top, window.width, window.height)
        root.mainloop()
        print(rect.coords)

        return rect.coords

    def capture_screen(self) -> None:
        while self.is_recording:
            try:
                if self.window:
                    left, top = self.window[0], self.window[1]
                    width, height = self.window[2] - self.window[0], self.window[3] - self.window[1]
                    screenshot = pyautogui.screenshot(region=(left, top, width, height))
                    screenshot.save(f"{os.getcwd()}/uploads/Screenshot.png")
            except Exception as e:
                print(f"Error taking screenshot: {e}")
            self.log_screencap_subtitles()
            time.sleep(self.time_between_screencaps)

    def select_window(self) -> str:
        def on_button_click(window_title) -> None:
            nonlocal selected_title
            selected_title = window_title
            root.destroy()  # Close the GUI after selection

        root = ctk.CTk()
        root.title("Select Window to Capture")
        root.minsize(width=400, height=300)

        available_windows = gw.getAllTitles()
        selected_title = None  # Variable to hold the selected title

        # Create a button for each window title
        for title in available_windows:
            if len(title) > 3:
                button = ctk.CTkButton(root, text=title, command=lambda t=title: on_button_click(t))
                button.pack(pady=5)

        root.mainloop()  # Start the GUI event loop

        return selected_title  # type: ignore # Return the selected window title
    
    def take_screenshot(self) -> str: # send image through the ringer
        '''
        Takes a screenshot and returns the parsed text
        '''
        #try:
        if not self.window:
            self.window = self.get_rectangle()
        
        left, top = self.window[0], self.window[1]
        width, height = self.window[2] - self.window[0], self.window[3] - self.window[1]
        screenshot = pyautogui.screenshot(region=(left, top, width, height))
        screenshot.save(f"{os.getcwd()}/uploads/Screenshot.png")

        
        text = screenshot_text_extractor.comparative_read_text_from_image(
        filepath=f"{os.getcwd()}/uploads/Screenshot.png", language=self.language, minimum_confidence=self.minimum_confidence, 
        config=self.config, number_of_preprocessors=self.preprocessors, display_comparison=False)

        if len(text) > 0:
            # for v in startup.get_language_dicts().values():
            #     if v[0] == self.language:
            #         spacy_lang_code = v[1]
            terms = prompt_generator.find_parts_of_speech_in_sentence(text, ['NOUN', 'ADJ', 'VERB'], self.nlp) 
            for term in terms:
                logger.log_term(term, 'Number of touches', nlp_language_code=self.language)

        # except Exception as e:
        #     print(f"Error taking screenshot: {e}")
        #     text = ''
        return text


    def start_recording(self) -> bool:
        self.filename = self.prompt_for_filename()

        with self._recording_lock:
            if not self.is_recording:
                self.is_recording = True
                self.record_thread = threading.Thread(target=self.capture_screen, daemon=True)
                self.record_thread.start()
                return True
            return False

    def stop_recording(self) -> bool:
        with self._recording_lock:
            if self.is_recording:
                self.is_recording = False
                if self.record_thread:
                    self.record_thread.join(timeout=5)
                    self.record_thread = None
                return True
            return False

    def log_screencap_subtitles(self) -> None:
        text = screenshot_text_extractor.comparative_read_text_from_image(
            filepath=f"{os.getcwd()}/uploads/Screenshot.png", language=self.language, minimum_confidence=self.minimum_confidence, 
            config=self.config, number_of_preprocessors=self.preprocessors, display_comparison=False)

        logger.log_subtitle(text, f'{config.get_data_directory()}\\subtitles\\{self.filename}')
        print(f'Saved screencapture subtitles to {config.get_data_directory()}\\subtitles\\{self.filename}')


    def prompt_for_filename(self) -> str:
        # Create a custom Tkinter window for file name input
        root = ctk.CTk()  # CustomTkinter window
        root.title("File Name Prompt")
        root.geometry("400x200")  # Set window size
        root.minsize(400, 200)

        # Create a label for instructions
        label = ctk.CTkLabel(root, text="Enter the file name:", font=("Arial", 16))
        label.pack(pady=20)

        # Create an entry field for filename input
        filename_var = ctk.StringVar(value=self.filename)  # Initial value
        entry = ctk.CTkEntry(root, textvariable=filename_var, width=300)
        entry.pack(pady=10)

        # Variable to store the result
        result = [None]

        # Function to handle submission
        def submit() -> None:
            result[0] = filename_var.get().replace('.csv', '')  # Remove '.csv' if entered
            root.quit()  # Close the window

        # Create a submit button
        submit_button = ctk.CTkButton(root, text="Submit", command=submit)
        submit_button.pack(pady=20)

        # Run the GUI loop
        root.mainloop()
        root.destroy()

        # Return the filename with .csv extension
        return result[0] + '.csv' if result[0] else None


# Example instantiation
# this = ScreenRecorder(language='chi_sim', use_preprocessing=True, minimum_confidence=50, config=r'--oem 3 -l chi_sim', time_between_screencaps=1)
