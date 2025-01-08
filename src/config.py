import configparser
import os
from pathlib import Path
import sys
import tkinter as tk
from tkinter import simpledialog
from typing import Union

from src import LLMserver

'''
url: http://10.0.0.10:1234/V1
api_key: aya-23-8b@f16
model: aya-23-8b@f16
'''

# Define a global variable
data_dir = None


def get_data_directory() -> Path:
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


def get_config() -> configparser.ConfigParser:
    cfg = configparser.ConfigParser()
    data_dir = get_data_directory()
    try:
        with open(os.path.join(data_dir, 'config.ini'), 'r') as configfile:
            cfg.read_file(configfile)
            LLMserver.set_url(cfg["Server"]["base_url"])
            LLMserver.set_api_key(cfg["Server"]["api_key"])
            LLMserver.set_model(cfg['Server']['model'])

    except FileNotFoundError:
        init_config()

    return cfg



def init_config() -> None:
    cfg = configparser.ConfigParser()

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
    cfg['SettingsOCR'] = {'num_of_preprocessors': 3, 'tesseract_configuration': '--psm 7',
                          'time_between_screenshots': 0.8}
    cfg['Server'] = {'base_url': base_url, 
                     'api_key': api_key, 
                     'model': model}
    cfg['Language'] = {'language':'none',
                       'proficiency':'none'}
    
    data_dir = get_data_directory()
    with open(os.path.join(data_dir, 'config.ini'), 'w') as configfile:
        cfg.write(configfile)

    # Set values for LLMserver
    LLMserver.set_url(base_url)
    LLMserver.set_api_key(api_key)
    LLMserver.set_model(model)


def set_config_default_language_and_proficiency(lang: str, proficiency: str) -> None:
    cfg = configparser.ConfigParser()
    data_dir = get_data_directory()
    config_file_path = os.path.join(data_dir, 'config.ini')
    cfg.read(config_file_path)

    # Check if 'Language' section exists
    if not cfg.has_section('Language'):
        cfg.add_section('Language')  # Create the section if it doesn't exist

    # Set values for language and proficiency
    cfg['Language']['language'] = lang
    cfg['Language']['proficiency'] = proficiency

    try:
        # Write the updated configuration back to the file
        with open(config_file_path, 'w') as configfile:
            cfg.write(configfile)

    except: # FileNotFoundError
        init_config()


def get_config_default_language_and_proficiency() -> Union[list[str], list[None]]:
    cfg = configparser.ConfigParser()
    data_dir = get_data_directory()
    try:
        with open(os.path.join(data_dir, 'config.ini'), 'r') as configfile:
               cfg.read_file(configfile)
        if os.environ["Language"] is not None:
            lang_prof = [os.environ["LEXEME_LANGUAGE"], cfg['Language']['proficiency']]
        else:
            lang_prof = [cfg['Language']['language'], cfg['Language']['proficiency']]
    except FileNotFoundError: 
        lang_prof = [None, None]

    return lang_prof

def get_config_home_page_attributes():
    """return SettingsOCR, Server, and Language parts of config

    """
    cfg = configparser.ConfigParser()
    data_dir = get_data_directory()
    try:
        with open(os.path.join(data_dir, 'config.ini'), 'r') as configfile:
            cfg.read_file(configfile)
    except:
        init_config()
        with open(os.path.join(data_dir, 'config.ini'), 'r') as configfile:
            cfg.read_file(configfile)

    
    num_processors = cfg['SettingsOCR']['num_of_preprocessors']
    tesseract_configuration = cfg['SettingsOCR']['tesseract_configuration']
    time_between_screenshots = cfg['SettingsOCR']['time_between_screenshots']
    base_url = cfg['Server']['base_url']
    api_key = cfg['Server']['api_key']
    model = cfg['Server']['model']
    lang = cfg['Language']['language']
    prof = cfg['Language']['proficiency']

    return num_processors,tesseract_configuration,time_between_screenshots, base_url,api_key,model, lang, prof

def update_config_settings_from_webapp(config_settings):
    cfg = configparser.ConfigParser()
    data_dir = get_data_directory()
    try:
        with open(os.path.join(data_dir, 'config.ini'), 'r') as configfile:
            cfg.read_file(configfile)
    except:
        init_config()
        with open(os.path.join(data_dir, 'config.ini'), 'r') as configfile:
            cfg.read_file(configfile)

    num_processors, tesseract_configuration, time_between_screenshots, base_url, api_key, model, lang, prof = config_settings
    cfg.set('SettingsOCR','num_of_preprocessors', num_processors)
    cfg.set('SettingsOCR', 'tesseract_configuration', tesseract_configuration)
    cfg.set('SettingsOCR', 'time_between_screenshots', time_between_screenshots)
    cfg.set('Server','base_url',base_url)
    cfg.set('Server', 'api_key', api_key)
    cfg.set('Server', 'model', model)
    cfg.set('Language', 'language', lang)
    cfg.set('Language', 'proficiency', prof)
    
    
    try: 
        with open(os.path.join(data_dir, 'config.ini'), 'w') as config_file:
            cfg.write(config_file)
    except: print('error writing file!') 

if __name__ == '__main__':
    get_data_directory()
    get_config()
