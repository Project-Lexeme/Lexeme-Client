from flask import Flask, request, jsonify, send_from_directory, render_template
import spacy
import os
import screenshot_text_extractor, prompt_generator, startup, setup_pytesseract
from screen_recorder import ScreenRecorder 
import LLMserver
import logger
import subprocess
import sys
import webbrowser
import time

'''
TODO: check out Koboldcpp for a means to deploy LLM server 
TODO: review TODOs and fix things
TODO: look closer at how choices get passed back and forth
TODO: rework the subtitle.csv naming convention and work in a folder 
TODO: refactor, clean - DO IT. don't be lazy. Big rocks are prompt_generator
TODO: work on screen recorder OCR performance
TODO: add support for multiple monitors - Desktopmagic library for python - wil be a headache.
TODO: TEST packaging the thing up and launching from a clean environment. At home, maybe
TODO: add support for config file with LLM API info, potentially have user-input required with opening windows if no config file is found?

'''


app = Flask(__name__)
#nlp = spacy.load("zh_core_web_sm") #

# Define the upload folder
UPLOAD_FOLDER = 'uploads'
# Create the upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

        

@app.route('/submit-response', methods=['POST']) # need to inherit choice from URL
def log_student_response_to_lesson():
    data = request.get_json()
    term = data.get('choice')
    response = data.get('response')
    # Process the response here, e.g., update database or perform logic
    print(f'Response received: {response}')
    
    if response == 'yes':
        logger.log_term(term, on='Number correct')
        return "Keep it up!"
    elif response == 'no':
        logger.log_term(term, on="Number incorrect")
        return "I'll add it to the list of terms to review" # TODO: think about the list of terms to review  
    return jsonify({'status': 'success', 'received': response})

    # print(answer)
    

@app.route('/lesson', methods=['GET'])
def get_lesson(): # need to divide the multiple choice up into another prompt
    choice = request.args.get('choice', 'No choice provided')
    if choice.endswith('.csv'):
        text = logger.get_subtitles_csv(choice)
        print(f"this is in get lesson{text}")
        for sentence in text:
            print(f"this is the first sentence: {sentence}")
            terms = prompt_generator.find_parts_of_speech_in_sentence(sentence, 'NOUN', nlp)
            for term in terms:
                print(f"this is the first term: {term}")
                logger.log_term(term, 'Number of touches')
    prompt = prompt_generator.generate_prompt_from_choice(choice)

    llm_response = LLMserver.post_prompt_to_LLM(prompt)
    return render_template('lesson.html', choice=choice, llm_response=llm_response)

@app.route('/review-choices')
def get_review_choices():
    choices = logger.get_terms()    
    return jsonify(choices)

@app.route('/get-subtitle-files')
def get_subtitle_files(): #TODO: fix this to reflect changes in file saving function in logger
    file_extension = '.csv' 
    current_directory = os.getcwd()
    files = [f for f in os.listdir(current_directory) if os.path.isfile(f) and f.endswith(file_extension)]
    return files


@app.route('/choices', methods=['GET'])
def get_choices(part_of_speech='NOUN'):
    text = screenshot_text_extractor.read_text_from_image(filepath=f"E:/ProjectLexeme_Server/uploads/Screenshot.png", language=language, preprocessing=False, minimum_confidence=50)
    choices = prompt_generator.find_parts_of_speech_in_sentence(text, part_of_speech, nlp) # TO DO: Make this legit later - be able to pass in POS as arg
    
    return jsonify(choices)

@app.route('/upload', methods=['POST'])
def upload_image(): #TODO refactor to simplify if possible
    if 'image' not in request.files:
        print('error: No image file provided')
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']

    if file.content_type != 'image/png':
        print('file.contenttype is wrong')
        return jsonify({'error': 'Invalid file type, only PNG allowed'}), 400

    if file.filename == '':
        return 'No selected file', 400
    
    # Save the file to the designated folder
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    # NOTIONAL 
    text = screenshot_text_extractor.read_text_from_image(filepath=f"E:/ProjectLexeme_Server/uploads/Screenshot.png", language=language, preprocessing=True, minimum_confidence=70)
    logger.log_subtitle(text, 'subtitles.csv')
    # NOTIONAL

    return jsonify({'message': 'Image received and processed'}), 200

@app.route('/begin-recording', methods=['POST'])
def begin_recording(): 
    if recorder.start_recording():
        return jsonify({"status":"success", "message":"Recording started"})
    return jsonify({"status":"error", "message":"Recording already started"})

@app.route('/stop-recording', methods=['POST'])
def stop_recording():
    if recorder.stop_recording():
        return jsonify({"status":"success", "message":"Recording stopped"})
    return jsonify({"status":"error", "message":"No recording in progress"})
   
@app.route('/submit', methods=['POST'])
def submit_choice():
    data = request.get_json()  # Get the JSON data from the request body
    selected_choice = data.get('choice')
    
    response = {"message": f"Loading lesson plan for: {selected_choice}..."} ## TODO: change response
    return jsonify(response)

@app.route('/uploads/<filename>')
def get_uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')


def install_and_import_nlp_lang(module_name):
    try:
        # Attempt to import the module as test of whether it's there
        __import__(module_name)
    except ImportError:
        # If the module is not found, install it
        print(f"{module_name} not found. Installing...")
        subprocess.check_call([sys.executable, '-m', 'spacy', 'download', module_name])

if __name__ == '__main__':
    config = startup.get_config()
    language, nlp_lang, proficiency = startup.get_language_and_proficiency()
    install_and_import_nlp_lang(nlp_lang)
    nlp = spacy.load(nlp_lang) # this is passed in as arg here in main.py
    setup_pytesseract.setup_tessdata(language)
    recorder = ScreenRecorder(language=language, use_preprocessing=False, minimum_confidence=50, config=r'', time_between_screencaps=1) ## TODO: revisit preprocess, explore pytesseract config files
    webbrowser.open('http://127.0.0.1:5000/')
    app.run(port=5000)

    