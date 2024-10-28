import configparser
import os
from pathlib import Path
import sys
import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
import LLMserver

# Define a global variable
data_dir = None

def get_data_directory():
    global data_dir  # Declare that we are using the global variable

    if getattr(sys, 'frozen', False):
    # If running as a bundled executable
        if data_dir is None:  # Initialize it only once
            if sys.platform.startswith('win'):
                # Windows
                data_dir = Path(os.getenv('APPDATA')) / 'Project Lexeme'
            else:
                # Linux and macOS
                data_dir = Path.home() / '.project_lexeme'

    else:
    # If running in a normal Windows Python environment
        data_dir = Path(os.getcwd()) / 'data'

        
    # Create the directory if it doesn't exist
    data_dir.mkdir(parents=True, exist_ok=True)
    
    return data_dir


def get_config(): # TODO
    cfg = configparser.ConfigParser()
    data_dir = get_data_directory()
    try: 
        with open(os.path.join(data_dir, 'config.ini'),'r') as configfile:
            cfg.read_file(configfile)
            LLMserver.set_url(cfg["Server"]["base_url"])
            LLMserver.set_api_key(cfg["Server"]["api_key"])
            LLMserver.set_model(cfg['Server']['model'])

    except FileNotFoundError: # this needs wrapped in a function and called instead of going here 
        
        def prompt_user_for_config():
            base_url = simpledialog.askstring("Input", "Enter the base URL:")
            api_key = simpledialog.askstring("Input", "Enter the API key:")
            model = simpledialog.askstring("Input", "Enter the model:")
            return base_url, api_key, model

        # Initialize tkinter
        root = tk.Tk()
        root.withdraw()  # Hide the main window

        # Get user input
        base_url, api_key, model = prompt_user_for_config()

        # Write the new config to the file
        cfg['General'] = {'debug': True, 'log_level': 'info'}
        cfg['Server'] = {
            'base_url': base_url,
            'api_key': api_key,
            'model': model
        }
        
        with open(os.path.join(data_dir, 'config.ini'), 'w') as configfile:
            cfg.write(configfile)

        # Set values for LLMserver
        LLMserver.set_url(base_url)
        LLMserver.set_api_key(api_key)
        LLMserver.set_model(model)

    return cfg