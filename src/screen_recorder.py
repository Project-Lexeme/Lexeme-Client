import customtkinter as ctk
import pyautogui
import time
import re
import threading
import os
import platform

from src import config
from src import logger
from src import screenshot_text_extractor
from src import natural_language_processing


def clean_filename(title) -> str:  # Replace invalid characters with underscores or remove them
    return re.sub(r'[<>:"/\\|?*. ]', '_', title)


class DrawRectangleApp:
    def __init__(self, root) -> None:
        self.root = root
        ###
        if platform.system() != 'Windows':
            self.root.wait_visibility(self.root)
        ###
        self.root.attributes("-topmost", True)  # Always on top
        self.root.attributes("-alpha", 0.5)  # Transparent background
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


# def draw_rectangle(root) -> None:
#     rect = DrawRectangleApp(root)
#     root.mainloop()
#     return


class ScreenRecorder:
    def __init__(self, ocr_lang_code: str, nlp_model, preprocessors: int, minimum_confidence: int, config, time_between_screencaps: float, nlp_lang_code) -> None:
        """Comprehensive screen recorder for screenshots and recording, and OCR that follows

        Args:
            ocr_lang_code (str): tesseract-friendly language code such as "chi_sim" or "rus"
            nlp_lang_code (str): NLP friendly language code such as "fra_news_core_sm"
            nlp_model (spacy.Language): loaded language model 
            preprocessors (int): number of different preprocessors to use for comparison against parent - should be in the range of 1-4 depending on CPU
            minimum_confidence (int): confidence level to filter out Tesseract token confidence - should be in the range of [0-100] with high confidence being 80+
            config (_type_): _description_
            time_between_screencaps (float): time between screencaps when recording
        """
        self.is_recording = False
        self.record_thread = None
        self._recording_lock = threading.Lock()
        self.window = self.get_rectangle()
        self.ocr_lang_code = ocr_lang_code
        self.nlp_lang_code = nlp_lang_code
        self.preprocessors = preprocessors
        self.minimum_confidence = minimum_confidence
        self.subtitle_filename = clean_filename(
            self.ocr_lang_code + '' + str(time.localtime().tm_yday) + '' + str(
                time.localtime().tm_hour) + '' + str(time.localtime().tm_min)) + '.csv'
        self.config = config
        self.time_between_screencaps = time_between_screencaps
        self.nlp_model = nlp_model
        self.most_recent_text_ocr = ''

    def get_rectangle(self) -> tuple[int, int, int, int]:
        """Allows user to draw a rectangle on the screen to choose bounding box

        Returns:
            tuple[int, int, int, int]: left, top, right, bottom
        """
        root = ctk.CTk()
        rect = DrawRectangleApp(root)
        root.mainloop()
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

    def take_screenshot(self) -> str: # send image through the ringer
        """For use with "Take Screenshot" button. Gets bounding boxes (sets them if need be) and takes a screenshot, logging the terms in the learner profile.
        
        <br>Uses an extra preprocessor if ScreenRecorder.
        
        Returns:
            str: text string derived from image
        """


        if not self.window:
            self.window = self.get_rectangle()

        left, top = self.window[0], self.window[1]
        width, height = self.window[2] - self.window[0], self.window[3] - self.window[1]
        screenshot = pyautogui.screenshot(region=(left, top, width, height))
        filename = self.ocr_lang_code + '' + str(time.localtime().tm_yday) + '' + str(
                time.localtime().tm_hour) + '' + str(time.localtime().tm_min)
        filepath = f"{os.getcwd()}/screenshots/{filename}.png"
        screenshot.save(filepath)
        text = screenshot_text_extractor.comparative_read_text_from_image(filepath=filepath,
                                                                          language=self.ocr_lang_code,
                                                                          minimum_confidence=self.minimum_confidence,
                                                                          config=self.config,
                                                                          number_of_preprocessors=self.preprocessors + 1,
                                                                          display_comparison=False)
        
        self.set_most_recent_text_ocr(text)

        if len(text) > 0:
            terms = natural_language_processing.find_parts_of_speech_in_sentence(text, ['NOUN', 'ADJ', 'VERB'], self.nlp_model)
            logger.log_terms(terms, 'Number of touches', nlp_lang_code=self.nlp_lang_code, ocr_lang_code=self.ocr_lang_code)
        return text

    def set_most_recent_text_ocr(self, text):
        self.most_recent_text_ocr = text
    
    def get_most_recent_text_ocr(self):
        return self.most_recent_text_ocr
    
    def start_recording(self) -> bool:
        self.subtitle_filename = self.prompt_for_filename()

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

    # TODO: currently, screencap subtitle file is opened and appended with every write. 
    # this needs to change to having a self.current_recording_subtitles list of subtitles so that the filename isn't needed until recording STOPS
    def log_screencap_subtitles(self) -> None: 
        text = screenshot_text_extractor.comparative_read_text_from_image(
            filepath=f"{os.getcwd()}/uploads/Screenshot.png", language=self.ocr_lang_code,
            minimum_confidence=self.minimum_confidence,
            config=self.config, number_of_preprocessors=self.preprocessors, display_comparison=False)
        self.set_most_recent_text_ocr(text)
        
        log_filepath = os.path.join(config.get_data_directory(), "subtitles", f"{self.subtitle_filename}")
        logger.log_subtitle(text, log_filepath)
        #print(f'Saved screencapture subtitles to {config.get_data_directory()}\\subtitles\\{self.subtitle_filename}')

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
        filename_var = ctk.StringVar(value=self.subtitle_filename)  # Initial value
        entry = ctk.CTkEntry(root, textvariable=filename_var, width=300)
        entry.pack(pady=10)

        # Variable to store the result
        result = [None]

        # Function to handle submission
        def submit():
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

if __name__ == "__main__":
    print("I should really test an instantiation of ScreenRecorder here")
    #screen_recorder = ScreenRecorder()
