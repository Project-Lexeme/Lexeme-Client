import shutil
import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
import pip
import spacy
from spacy.cli import download
import config
import os
from pathlib import Path
import sys


def make_dirs():
    path = config.get_data_directory()
    subtitle_path = Path(os.path.join(path, 'subtitles'))
    subtitle_path.mkdir(parents=True, exist_ok=True)
    prompt_path = Path(os.path.join(path, 'prompts'))
    prompt_path.mkdir(parents=True, exist_ok=True)
    populate_prompts()

def populate_prompts():
     if getattr(sys, 'frozen', False):
        prompt_dir = os.path.join(sys._MEIPASS, 'data', 'prompts')
        for f in os.listdir(prompt_dir):
            if f.endswith('.csv'):
                source_file = os.path.join(sys._MEIPASS, 'data', 'prompts', f)
                target_file = os.path.join(config.get_data_directory(), 'prompts', f)
            # Copy the .csv file to the target directory
            shutil.copy(source_file, target_file)
            print(f'Copied: {source_file} to {target_file}')
    

def install_and_load_nlp_lang(module_name): 

    if getattr(sys, 'frozen', False):
        model_path = os.path.join(sys._MEIPASS, 'spacy', 'data', f'{module_name}') #, fr'{module_name}[-.0-9]*') # _MEIPASS is temp directory, zh_core_web_sm is passed in .spec file to be stored in spacy/data/module name and config is stored in module name- version subdirectory
        
    else:
        if module_name in spacy.util.get_installed_models():
        # Attempt to import the module as test of whether it's there
            module_name in spacy.util.get_installed_models()
        else:
            # If the module is not found, install it
            print(f"{module_name} not found. Installing...")
            download(module_name)
        model_path = module_name
    return spacy.load(model_path)

def get_language_and_proficiency():
    
    try: lang, prof = config.get_config_default_language_and_proficiency()
     
    except Exception as e:
        print(f"Couldn't find '{e}' portion of config")
        lang, prof = 'Select Language', 'Select Proficiency' 
    
    selected_values = {"language": lang, "proficiency": prof}

    # Function to handle submission of both selections
    def submit_selection():
        selected_values['language'] = language_var.get()
        selected_values['proficiency'] = proficiency_var.get()
        root.quit()

    # Create the main window
    root = tk.Tk()
    root.title("Language and Level Selector")

    #TODO: add support for NLTK for languages not covered by SpaCy
    # language code values are [OCR lang code,SpaCy code]
    language_codes = {"English":["eng", "en_core_web_sm"], "Spanish":["spa", 'es_core_news_sm'] , "French":["fra","fr_core_news_sm"], 
                      "German":["deu","de_core_news_sm" ], "Chinese Simplified":["chi_sim", "zh_core_web_sm"], 
                      "Chinese Traditional":["chi_tra", "zh_core_web_sm"] , "Japanese":["jpn", "ja_core_news_sm"], 
                      "Korean":["kor","ko_core_news_sm"], "Russian":['rus',"ru_core_news_sm"]}
    proficiencies = ['No proficiency','Memorized proficiency','Elementary proficiency','Limited working proficiency','General professional proficiency','Advanced professional proficiency']


    languages = [lang for lang in language_codes.keys()]
   

    language_var = tk.StringVar(value=languages[0])     # Set to first language as default otherwise this breaks
    proficiency_var = tk.StringVar(value=proficiencies[0])  # Set to first proficiency as default otherwise breaks

    # Create the first dropdown (combobox)
    language_combobox = ttk.Combobox(root, textvariable=language_var, values=languages)
    language_combobox.set(lang)  # Set default text
    # language_combobox.bind("<<ComboboxSelected>>", update_second_dropdown)  # Bind event
    language_combobox.pack(padx = 10, pady=10)

    # Create the second dropdown (combobox)
    second_dropdown = ttk.Combobox(root, textvariable=proficiency_var, values=proficiencies)
    second_dropdown.set(prof)  # Set default text
    second_dropdown.pack(padx = 10, pady=10)

    # Create a submit button
    submit_button = tk.Button(root, text="Submit", command=submit_selection)
    submit_button.pack(pady=20)

    

    # Start the Tkinter event loop
    root.mainloop()
    
    config.set_config_default_language_and_proficiency(selected_values['language'], selected_values['proficiency'])
    root.destroy()
    return (selected_values['language'], [language_codes[selected_values['language']][0], language_codes[selected_values['language']][1], selected_values['proficiency']])

#print(get_config())