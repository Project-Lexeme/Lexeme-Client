import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
import configparser
import LLMserver

# Function to update the second dropdown based on the selected language

def get_config(): # TODO
    config = configparser.ConfigParser()
    try: 
        with open('config.ini','r') as configfile:
            config.read_file(configfile)
            LLMserver.set_url(config["Server"]["base_url"])
            LLMserver.set_api_key(config["Server"]["api_key"])
            LLMserver.set_model(config['Server']['model'])

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
        config['General'] = {'debug': True, 'log_level': 'info'}
        config['Server'] = {
            'base_url': base_url,
            'api_key': api_key,
            'model': model
        }
        
        with open('config.ini', 'w') as configfile:
            config.write(configfile)

        # Set values for LLMserver
        LLMserver.set_url(base_url)
        LLMserver.set_api_key(api_key)
        LLMserver.set_model(model)

    return config

def get_language_and_proficiency():
    selected_values = {"language": None, "proficiency": None}
    
    def update_second_dropdown(event):
        options = ['No proficiency','Memorized proficiency','Elementary proficiency','Limited working proficiency','General professional proficiency','Advanced professional proficiency']

        # Update the second dropdown with the new options
        second_dropdown['values'] = options
        second_dropdown.set("")  # Clear previous selection

    # Function to handle submission of both selections
    def submit_selection():
        selected_values['language'] = language_var.get()
        selected_values['proficiency'] = second_var.get()
        root.destroy()

    # Create the main window
    root = tk.Tk()
    root.title("Language and Level Selector")

    #TODO: add support for NLTK for languages not covered by SpaCy
    # language code values are [OCR lang code,SpaCy code]
    language_codes = {"English":["eng", "en_core_web_sm"], "Spanish":["spa", 'es_core_news_sm'] , "French":["fra","fr_core_news_sm"], 
                      "German":["deu","de_core_news_sm" ], "Chinese Simplified":["chi_sim", "zh_core_web_sm"], 
                      "Chinese Traditional":["chi_tra", "zh_core_web_sm"] , "Japanese":["jpn", "ja_core_news_sm"], "Korean":["kor","ko_core_news_sm"], "Russian":['rus',"ru_core_news_sm"]}

    languages = [lang for lang in language_codes.keys()]
    # Variable to hold the selected language
    # Variables to hold the selected values
    language_var = tk.StringVar()
    second_var = tk.StringVar()

    # Create the first dropdown (combobox)
    language_combobox = ttk.Combobox(root, textvariable=language_var, values=languages)
    language_combobox.set("Select a language")  # Set default text
    language_combobox.bind("<<ComboboxSelected>>", update_second_dropdown)  # Bind event
    language_combobox.pack(padx = 10, pady=10)

    # Create the second dropdown (combobox)
    second_dropdown = ttk.Combobox(root, textvariable=second_var)
    second_dropdown.set("Select a proficiency level")  # Set default text
    second_dropdown.pack(padx = 10, pady=10)

    # Create a submit button
    submit_button = tk.Button(root, text="Submit", command=submit_selection)
    submit_button.pack(pady=20)

    # Start the Tkinter event loop
    root.mainloop()

    return language_codes[selected_values['language']][0], language_codes[selected_values['language']][1], selected_values['proficiency']

#print(get_config())