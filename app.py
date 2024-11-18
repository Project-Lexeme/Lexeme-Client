import webbrowser
from flask import Flask, request, jsonify, send_from_directory, render_template
import os
import spacy
from screen_recorder import ScreenRecorder
import screenshot_text_extractor, prompt_generator, config
import LLMserver
import logger
import setup_pytesseract
import startup

app = Flask(__name__)

# Define the upload folder
UPLOAD_FOLDER = 'uploads'
# Create the upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

_recorder = None
_nlp = None
_cfg = None
_language = None # TODO: use Language class to make the handling of language info cleaner

def set_recorder(recorder: ScreenRecorder) -> None:
    global _recorder
    _recorder = recorder

def set_nlp(nlp: spacy.Language) -> None:
    global _nlp
    _nlp = nlp

def set_cfg(cfg) -> None:
    global _cfg
    _cfg = cfg

def set_language(language) -> None:
    global _language
    _language = language

@app.route('/submit-response', methods=['POST']) # need to inherit choice from URL
def log_student_response_to_lesson():
    data = request.get_json()
    term = data.get('choice')
    response = data.get('response')
    # Process the response here, e.g., update database or perform logic
    print(f'Response received: {response}')
    
    if response == 'yes':
        logger.log_term(term, on='Number correct', language=_language)
        return "Keep it up!"
    elif response == 'no':
        logger.log_term(term, on="Number incorrect", language=_language)
        return "I'll add it to the list of terms to review" # TODO: think about the list of terms to review  
    return jsonify({'status': 'success', 'received': response})

    # print(answer)
    

@app.route('/lesson', methods=['GET'])
def get_lesson(): # # TODO: figure out how to use get_lesson to feed the type of lesson (unique values in the first column 'Type' of prompt CSVs)
    choice = request.args.get('choice', 'No choice provided')
    prompt_type = request.args.get('prompt_type', 'Any')
    if choice.endswith('.csv'): # naive way to check if they asked for an individual term or a subtitled csv file
        text = logger.get_subtitles_csv(choice)
        for sentence in text:
            terms = prompt_generator.find_parts_of_speech_in_sentence(sentence, ['NOUN', 'ADJ', 'VERB'], _nlp)
            for term in terms:
                logger.log_term(term, 'Number of touches', language=_language)
    print(prompt_type)
    prompt = prompt_generator.generate_prompt_from_choice(choice, prompt_type)

    llm_response = LLMserver.post_prompt_to_LLM(prompt, _language) # TODO: 
    return render_template('lesson.html', choice=choice, llm_response=llm_response)

@app.route('/review-choices')
def get_review_choices():
    choices = logger.get_terms() 
    prompt_types = prompt_generator.get_prompt_types(isTerm=True)   
    return jsonify({"choices": choices, "prompt_types": prompt_types})

@app.route('/get-subtitle-files')
def get_subtitle_files():
    file_extension = '.csv' 
    subtitle_directory = os.path.join(config.get_data_directory(), 'subtitles')
    choices = [f for f in os.listdir(subtitle_directory) if os.path.isfile(os.path.join(subtitle_directory, f)) and f.endswith(file_extension)]
    prompt_types = prompt_generator.get_prompt_types(isTerm=False)
    print(f'choices: {choices}, prompt_types: {prompt_types}')
    return jsonify({"choices": choices, "prompt_types": prompt_types})

@app.route('/get-learner-profile')
def get_learner_profile():
    learner_profile = logger.get_terms(all=True)
    prompt_types = prompt_generator.get_prompt_types(isTerm=True)
    return render_template('learner_profile.html', csv_data=learner_profile, prompt_types=prompt_types)


@app.route('/choices', methods=['GET']) # DEPRECATED
def get_choices(part_of_speech='NOUN'):
    text = screenshot_text_extractor.read_text_from_image(filepath=f"{os.getcwd()}/uploads/Screenshot.png", language=_language, preprocessing=False, minimum_confidence=50)
    choices = prompt_generator.find_parts_of_speech_in_sentence(text, part_of_speech, _nlp) # TO DO: Make this legit later - be able to pass in POS as arg
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

    return jsonify({'message': 'Image received and processed'}), 200

@app.route('/begin-recording', methods=['POST'])
def begin_recording():
    print("begin_recording flask function called")
    if _recorder is None:
        # Set up the screen recorder
        language, codes_and_proficiency =  startup.get_language_and_proficiency()
        lang_code, nlp_lang, proficiency = codes_and_proficiency
        set_language(lang_code)
        set_recorder(ScreenRecorder(language=lang_code, preprocessors=3, use_comparative_preprocessing=True, minimum_confidence=70, config=r'', time_between_screencaps=.6))
        print("ScreenRecorder is set up")
        set_nlp(startup.install_and_load_nlp_lang(nlp_lang))
        setup_pytesseract.setup_tessdata(lang_code)
    if _recorder.start_recording():
        return jsonify({"status":"success", "message":"Recording started"})
    return jsonify({"status":"error", "message":"Recording already started"})

@app.route('/stop-recording', methods=['POST'])
def stop_recording():
    if _recorder.stop_recording():
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


def start_app():
    startup.make_dirs()
    set_cfg(config.get_config())
    print("Config loaded successfully!")
    language, codes_and_proficiency =  startup.get_language_and_proficiency()
    lang_code, nlp_lang, proficiency = codes_and_proficiency
    #print(f"You chose {language} at a {proficiency} level!") # not currently doing anything with language/nlp_lang
    set_language(lang_code)
    set_nlp(startup.install_and_load_nlp_lang(nlp_lang))
    print("SpaCy installed, imported, and loaded")
    print("Setting up PyTesseract now... Checking for installation")
    setup_pytesseract.set_tesseract_cmd()
    print("Checking for language data for your language...")
    setup_pytesseract.setup_tessdata(lang_code)
    print("PyTesseract set up!")
    #recorder = ScreenRecorder(language=lang_code, use_preprocessing=False, minimum_confidence=70, config=r'', time_between_screencaps=.8) ## TODO: revisit preprocess, explore pytesseract config files
    #set_recorder(recorder)
    #print("ScreenRecorder is set up")
    webbrowser.open('http://127.0.0.1:5000/')
    app.run(port=5000)