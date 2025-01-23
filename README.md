## TO RUN
To run, create/activate venv using requirements.txt and run from project root directory:
```
python main.py
```
In development environment, relevant SpaCy modules and Tesseract-OCR language support will be downloaded upon selection of a language when running the code.

As an executable, SpaCy modules need to be packaged up with the .exe because SpaCy has been unreliable to download modules adhoc. 

Because of the SpaCy constraint and to minimize the size of the .exe, each language is built out as its own separate executable despite being an easy technical lift to have one .exe for all languages.

To support a given language, a SpaCy POS tagger, LLM support, and Tesseract OCR support are all needed, and ideally the language also has a dictionary following the same format as the dictionaries in /data/dictionaries/. I have trained my own POS taggers for Arabic, Tagalog, Indonesian, and Persian (https://github.com/jdoerfler/ar-fa-id-tl-SpaCy-Training). These are far from optimal but their limits don't significantly detract from the performance of the app.

## TO USE
**You will need a hosted LLM to run this program.** When you launch the program for the first time, you will be prompted to put in the address of said LLM. Enter it exactly as you were given/have bootstrapped yourself. If you make an typo, you will get 404 errors or 500 errors when you generate a lesson depending on your typo.

If you're running from an .exe for the first time, you may need to exit after a minute and relaunch for the initial startup sequence to work.

When drawing the bounding box for screen recording, be generous with left and right bounds but tight with up/down bounds to save on computational overhead

Mess with the settings page, specifically the config values for "Tesseract Page Segmentation Modes" and the "Number of Preprocessors," to improve performance based on your machine and what you're watching. You might have to exit and relaunch for changes to take effect.

### TO WORK ON PROMPTS
If you want to change the prompts (add/remove them), you can go to the settings page and open up the prompt directory on your machine. When you make changes, do not create any leading or trailing whitespace were there was none before in the .csv. Back up the packaged prompt .csv. When you work on prompts, they may get lost upon next relaunch, so backup your changes and if you have a good prompt, open an issue on here and I'll add it to the prompts files.

## TO COMPILE EXECUTABLES
To add .exe support for a new language, check spec files (/spec/*.spec) and root compile_all_languages.bat to see how they're built using PyInstaller:
	
 	1. in Venv, use python interactive interpreter to download target spacy language
	
 	2. in venv/Lib/site-packages/target-language-directory, copy contents of versioned subdirectory into the parent target language directory
	
 	3. open up {language}.spec in spec/
	
 	4. add 'venv/Lib/site-packages/{target language spacy module name}', 'spacy/data/{target language spacy module name}'
	
 	5. add relevant dictionary - if it doesn't exist, find one online and parse it into correct format (e.g. de-en-enwiktionary.txt -> deu_dictionary.csv). see https://github.com/Project-Lexeme/Lexeme-Dictionaries

 	6. build that relevant .spec or all - good luck figuring out what directory to run it from to get relative paths correct
 	
  	7. cry
