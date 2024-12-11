import app

''' 
Long-term parking garage:
    - speech recognition implementation
    - add support for multiple monitors - Desktopmagic library for python - wil be a headache.
    - Investigate how to get around Tesseract installer requiring admin privileges to install
    - investigate concept of logins/user-specific profiles/etc.
    - investigate implementing SQLite for fast dictionary lookup
    - think about how dictionary contents with multiple meanings/contexts can be stored and recalled
    
Parking lot:
    - ADD FUNCTION TO LESSON PAGE WITH EXISTING TOOLTIPS RETRIEVER for definition, etc. Should be hoverable.
    - Tutorial/documentation
    - use formatted JSON response capabilities in LLM interface to get things like quiz answers in their own section.
    - implement structured output for quizzes, etc. - full implementation includes front-end handling of new json object e.g. requests.body.get("Answer")-esque stuff
    - support for Persian/other languages
    - support for farsi
    
Street parking:
    TODO investigate chinese pulling not noun phrases but just nouns
    TODO Generate lesson should generate 'any type' if lesson type dropdown is not selected
    TODO Generate summary button should pop up immediately after recording is stopped
    TODO investigate logger.get_terms assuming dtype (which can lead to strs being read as ints)
    TODO print most recent parsed text as popup instead of to terminal
    
Impound lot:
    - settings page        

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

    