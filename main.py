import app

''' 
TODO: look closer at how choices get passed back and forth 
TODO: refactor, clean - DO IT. don't be lazy. Big rocks are prompt_generator
TODO: expand genetic based OCR
TODO: add support for multiple monitors - Desktopmagic library for python - wil be a headache.
TODO: add Language class that has properties for all the different things a language touches (e.g. self.nlp versus self.spacy for nlp.language and spacy.language respectively)
'''

'''
Pedagogical notes:

-Prompts could include the use of previously touched terms as reinforcement - e.g. Give me a summary of x. Please use as many touched terms as possible.
-Pictures
-Prompts that broaden context around a target term by teaching related terms
-Specify context of terms or choose multiple contexts to define terms
-Think about poisoning 

'''

'''
to compile:
python -m PyInstaller main.spec main.py
'''

if __name__ == '__main__':
    app.start_app()

    