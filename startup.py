import shutil
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

def make_dirs() -> None:
    """
    Runs at app start to create subtitle, prompt, and dictionaries directories, then copy/pastes prompts/dictionaries if applicable
    """
    path = config.get_data_directory()
    
    subtitle_path = Path(os.path.join(path, 'subtitles'))
    subtitle_path.mkdir(parents=True, exist_ok=True)
    
    prompt_path = Path(os.path.join(path, 'prompts'))
    prompt_path.mkdir(parents=True, exist_ok=True)
    populate_prompts()

    dictionaries_path = Path(os.path.join(path, 'dictionaries'))
    dictionaries_path.mkdir(parents=True, exist_ok=True)
    populate_dictionaries()

def populate_prompts() -> None:
    """
    Checks if executable; if so, copy/pastes prompts from executable temp folder into permanent app data folder 
    """
    if getattr(sys, 'frozen', False):
        prompt_dir = os.path.join(sys._MEIPASS, 'data', 'prompts')
        for f in os.listdir(prompt_dir):
            if f.endswith('.csv'):
                source_file = os.path.join(sys._MEIPASS, 'data', 'prompts', f)
                target_file = os.path.join(config.get_data_directory(), 'prompts', f)
            # Copy the .csv file to the target directory
            shutil.copy(source_file, target_file)
            print(f'Copied: {source_file} to {target_file}')

def populate_dictionaries() -> None:
    """
    Checks if executable; if so, copy/pastes dictionaries from executable temp folder into permanent app data folder 
    """
    if getattr(sys, 'frozen', False):
        prompt_dir = os.path.join(sys._MEIPASS, 'data', 'dictionaries')
        for f in os.listdir(prompt_dir):
            if f.endswith('.csv'):
                source_file = os.path.join(sys._MEIPASS, 'data', 'dictionaries', f)
                target_file = os.path.join(config.get_data_directory(), 'dictionaries', f)
            # Copy the .csv file to the target directory
            shutil.copy(source_file, target_file)
            print(f'Copied: {source_file} to {target_file}')

def install_and_load_nlp_lang(module_name: str) -> spacy.Language:
    """Start-up sequence: checks for install and loads NLP lang, stripping the NLP pipeline of extraneous parts

    Args:
        module_name (str): spacy lang name, e.g. zh_core_web_sm

    Returns:
        spacy.Language: loaded lang model
    """
    if getattr(sys, 'frozen', False):
        model_path = os.path.join(sys._MEIPASS, 'spacy', 'data', f'{module_name}')
    else:
        if module_name in spacy.util.get_installed_models():
            pass
        else:
            print(f"{module_name} not found. Installing...")
            download(module_name)
        model_path = module_name
    nlp = remove_excess_nlp_pipeline_parts(spacy.load(model_path))    
    return nlp

def remove_excess_nlp_pipeline_parts(nlp_lang: spacy.Language):
    """Removes unnecessary pipeline componenets, e.g. NER, etc. This makes the NLP processing more efficient throughout

    Args:
        nlp_lang (spacy.Language): loaded Language model
    """
    # pipe_names = [pipe[0] for pipe in nlp_lang.pipeline]
    # for pipe in pipe_names:
    #     if pipe != 'tagger' and pipe != 'parser':  # Keep only the POS tagger and parser
    #         nlp_lang.remove_pipe(pipe)

    return nlp_lang

def get_language_and_proficiency() -> tuple[str, list[str]]:
    """
    Creates a GUI to select language and proficiency

    Returns:
        tuple[str, list[str]]: (language, [tesseract, SpaCy, proficiency])
    """
    # Try to fetch configuration or set defaults
    try:
        lang, prof = config.get_config_default_language_and_proficiency()
    except Exception as e:
        print(f"Couldn't find '{e}' portion of config")
        lang, prof = 'Select Language', 'Select Proficiency'

    # Store selected values (initially defaults)
    selected_values = {"language": lang, "proficiency": prof}

    # Function to handle submission of both selections
    def submit_selection() -> None:
        selected_values['language'] = language_combobox.get()
        selected_values['proficiency'] = proficiency_combobox.get()
        root.quit()

    # Create the main window
    root = ctk.CTk()
    root.title("Language and Level Selector")
    root.geometry(f"{400}x300")

    options_font = ctk.CTkFont("Courier New", size=18)

    language_codes = get_language_dicts()
    proficiencies = get_proficiencies()

    languages = [lang for lang in language_codes.keys()]

    # Create variables bound to the dropdowns
    language_var = ctk.StringVar(value=lang)  # Set initial value based on config or default
    proficiency_var = ctk.StringVar(value=prof)  # Set initial value based on config or default

    # Create the first dropdown (combobox) for language
    language_combobox = ctk.CTkComboBox(root, font=options_font, variable=language_var, values=languages, width=300)
    language_combobox.pack(padx=10, pady=20)

    # Create the second dropdown (combobox) for proficiency
    proficiency_combobox = ctk.CTkComboBox(root, font=options_font, variable=proficiency_var, values=proficiencies, width=300)
    proficiency_combobox.pack(padx=10, pady=20)

    # Create a submit button
    submit_button = ctk.CTkButton(root, text="Submit", font=options_font, command=submit_selection)
    submit_button.pack(pady=20)

    # Start the Tkinter event loop
    root.mainloop()
    root.destroy()

    # Once the loop ends, update the config with the selected values
    config.set_config_default_language_and_proficiency(selected_values['language'], selected_values['proficiency'])
    
    # Return the selected language and proficiency
    return (selected_values['language'],
            [language_codes[selected_values['language']][0],
             language_codes[selected_values['language']][1],
             selected_values['proficiency']])

def get_language_dicts():
    # Language and proficiency options 
    #{'Plain English' : ["tesseract","spacy"]}
    language_codes = { 
        "English": ["eng", "en_core_web_sm"],
        "Spanish": ["spa", 'es_core_news_sm'],
        "French": ["fra", "fr_core_news_sm"],
        "German": ["deu", "de_core_news_sm"],
        "Chinese Simplified": ["chi_sim", "zh_core_web_sm"],
        "Chinese Traditional": ["chi_tra", "zh_core_web_sm"],
        "Japanese": ["jpn", "ja_core_news_sm"],
        "Korean": ["kor", "ko_core_news_sm"],
        "Russian": ['rus', "ru_core_news_sm"],
        "Persian - Farsi": ["fa","fa_boot_sm"],
        "Persian - Dari": ["fa","fa_boot_sm"],
        "Arabic": ["ar","ar_boot_sm"],
        "Indonesian": ["in","in_boot_sm"],
        }
    
    if os.getenv("LEXEME_LANGUAGE") is not None:
        target_language = os.getenv("LEXEME_LANGUAGE")
        language_codes_keys = list(language_codes.keys())
        target_language_codes_keys = [language_code_key for language_code_key in language_codes_keys if language_code_key.startswith(target_language)]
        target_language_codes_values = [language_codes[target_language_code_key] for target_language_code_key in target_language_codes_keys]
        language_codes = dict(zip(target_language_codes_keys, target_language_codes_values))

    return language_codes

def get_proficiencies():
    proficiencies = ['No proficiency', 'Memorized proficiency', 'Elementary proficiency',
                     'Limited working proficiency', 'General professional proficiency',
                     'Advanced professional proficiency']
    return proficiencies


if __name__ == "__main__":
    print("startup.py")
    os.environ["LEXEME_LANGUAGE"] = "Persian"
    get_language_dicts()