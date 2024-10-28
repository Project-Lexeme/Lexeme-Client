import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
import pip

# Function to update the second dropdown based on the selected language

def install_and_import(package):
    if hasattr(pip, 'main'):
        pip.main(['install', package])
    else:
        pip._internal.main(['install', package])

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