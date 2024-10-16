import tkinter as tk
import pygetwindow as gw
import pyautogui
import time
import re
import requests
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

def on_button_click(window_title, root):
    capture_window(window_title)
    root.destroy() 
    return window_title 


def select_window():
    def on_button_click(window_title):
        nonlocal selected_title
        selected_title = window_title
        root.quit()  # Close the GUI after selection

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