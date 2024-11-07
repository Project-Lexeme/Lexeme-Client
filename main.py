import app

''' 
TODO: look closer at how choices get passed back and forth 
TODO: refactor, clean - DO IT. don't be lazy. Big rocks are prompt_generator
TODO: work on screen recorder OCR performance
    genetic based OCR
TODO: add support for multiple monitors - Desktopmagic library for python - wil be a headache.
TODO: learner_profile page should have hoverable popups for dictionary information
TODO: store dicts in data/dictionaries
    cedict_ts.u8
    https://github.com/Badestrand/russian-dictionary
    https://github.com/garfieldnate/kengdic/blob/master/kengdic.tsv
    
TODO: create common dictionary type 

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

    