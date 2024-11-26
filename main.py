import app

''' 
TODO: refactor, clean - DO IT. don't be lazy. Big rocks are prompt_generator
TODO: add support for multiple monitors - Desktopmagic library for python - wil be a headache.
TODO: ADD FUNCTION TO LESSON PAGE WITH EXISTING PARTS OF SPEECH TOOLTIPS RETRIEVER

TO THINK: ABILITY TO SET PROFILE GROUPINGS

v0.6 goals
TODO: ADD TUTORIAL
TODO: MODIFY THE GENERATE LESSON TO ALLOW A GENERATE A "ANY TYPE" BASED ON BLANK
TODO: ALLOW FOR GENERATE LESSON AFTER RECORDING IS FINISHED        
TODO: CREATE A SETTINGS PAGE TO MODIFY CONFIGURATIONS
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

    