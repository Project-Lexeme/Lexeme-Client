import app

''' 
TODO: refactor, clean - DO IT. don't be lazy. Big rocks are prompt_generator
TODO: add support for multiple monitors - Desktopmagic library for python - wil be a headache.
TODO: add Language class that has properties for all the different things a language touches (e.g. self.nlp versus self.spacy for nlp.language and spacy.language respectively)
TODO: add feedback mechanism for prompts - user should be able to select 'yes' or 'no' that they enjoyed the prompt output
        - instead of completely randomly pulling from prompts, use probability distribution based on resulting prompt score ^ 
        
TODO: ADD TUTORIAL
TODO: MODIFY THE GENERATE LESSON TO ALLOW A GENERATE A "ANY TYPE" BASED ON BLANK
TODO: ADD FUNCTION TO LESSON PAGE WITH EXISTING PARTS OF SPEECH TOOLTIPS RETRIEVER
TODO: ALLOW FOR GENERATE LESSON AFTER RECORDING IS FINISHED        
TODO: FIX SCREENSHOT BUTTON TO ONLY USE BOUNDING BOX
TODO: ALLOW THE ABILITY TO ADJUST BOUNDING BOX
TODO: CREATE A SETTINGS PAGE TO MODIFY CONFIGURATIONS
TO THINK: ABILITY TO SET PROFILE GROUPINGS
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
to compile all:
    ./compile_all_languages.bat

to compile individual language:
    python -m PyInstaller spec/{language}.spec /main.py 
    --noconfirm to skip output overwrite warning

'''

if __name__ == '__main__':
    app.start_app()

    