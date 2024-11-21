import app

''' 
TODO: refactor, clean - DO IT. don't be lazy. Big rocks are prompt_generator
TODO: add support for multiple monitors - Desktopmagic library for python - wil be a headache.
TODO: add Language class that has properties for all the different things a language touches (e.g. self.nlp versus self.spacy for nlp.language and spacy.language respectively)
'''

'''
Pedagogical notes:

-Prompts could include the use of previously touched terms as reinforcement - e.g. Give me a summary of x. Please use as many touched terms as possible.
-Pictures
-Prompts that broaden context around a target term by teaching related terms
'''

'''
to compile all:
    ./compile_all_languages.bat

to compile individual language:
    python -m PyInstaller spec/{language}.spec /main.py 
    --noconfirm to skip output overwrite warning

'''

if __name__ == '__main__':
    app.start_app()

    