import shutil
import customtkinter
import customtkinter as ctk
import spacy
from spacy.cli import download
import config
import os
from pathlib import Path
import sys

# Initialize the appearance of customtkinter (light, dark, or system theme)
ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

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
        model_path = os.path.join(sys._MEIPASS, 'spacy', 'data', f'{module_name}')
    else:
        if module_name in spacy.util.get_installed_models():
            pass
        else:
            print(f"{module_name} not found. Installing...")
            download(module_name)
        model_path = module_name
    return spacy.load(model_path)

def get_language_and_proficiency():
    try:
        lang, prof = config.get_config_default_language_and_proficiency()
    except Exception as e:
        print(f"Couldn't find '{e}' portion of config")
        lang, prof = 'Select Language', 'Select Proficiency'

    selected_values = {"language": lang, "proficiency": prof}

    def submit_selection():
        selected_values['language'] = language_var.get()
        selected_values['proficiency'] = proficiency_var.get()
        root.quit()

    # Create the main window
    root = ctk.CTk()
    root.title("Language and Level Selector")
    root.geometry(f"{400}x300")

    options_font = customtkinter.CTkFont("Courier New", size = 18 )

    # Language and proficiency options
    language_codes = {"English": ["eng", "en_core_web_sm"], "Spanish": ["spa", 'es_core_news_sm'],
                      "French": ["fra", "fr_core_news_sm"], "German": ["deu", "de_core_news_sm"],
                      "Chinese Simplified": ["chi_sim", "zh_core_web_sm"],
                      "Chinese Traditional": ["chi_tra", "zh_core_web_sm"], "Japanese": ["jpn", "ja_core_news_sm"],
                      "Korean": ["kor", "ko_core_news_sm"], "Russian": ['rus', "ru_core_news_sm"]}
    proficiencies = ['No proficiency', 'Memorized proficiency', 'Elementary proficiency',
                     'Limited working proficiency', 'General professional proficiency',
                     'Advanced professional proficiency']

    languages = [lang for lang in language_codes.keys()]

    language_var = ctk.StringVar(value=languages[0])
    proficiency_var = ctk.StringVar(value=proficiencies[0])

    # Create the first dropdown (combobox)
    language_combobox = ctk.CTkComboBox(root, font=options_font, variable=language_var, values=languages, width=300)
    language_combobox.set(lang)  # Set default language
    language_combobox.pack(padx=10, pady=20)

    # Create the second dropdown (combobox)
    proficiency_combobox = ctk.CTkComboBox(root, font=options_font, variable=proficiency_var, values=proficiencies, width=300)
    proficiency_combobox.set(prof)  # Set default proficiency
    proficiency_combobox.pack(padx=10, pady=20)

    # Create a submit button
    submit_button = ctk.CTkButton(root, text="Submit", font=options_font, command=submit_selection)
    submit_button.pack(pady=20)

    # Start the Tkinter event loop
    root.mainloop()

    config.set_config_default_language_and_proficiency(selected_values['language'], selected_values['proficiency'])
    root.destroy()
    return (selected_values['language'], [language_codes[selected_values['language']][0], language_codes[selected_values['language']][1], selected_values['proficiency']])

# Test the function
#print(get_language_and_proficiency())
