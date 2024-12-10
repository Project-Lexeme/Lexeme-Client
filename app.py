import webbrowser
from flask import Flask, request, jsonify, send_from_directory, render_template
import os
import platform
import subprocess
import pandas as pd
import spacy
from screen_recorder import ScreenRecorder
from language_data import LanguageData
import screenshot_text_extractor, prompt_generator, config
import LLMserver
import logger
import startup
from datetime import datetime

import subtitle_upload_parser

app = Flask(__name__)

# Define the upload folder
UPLOAD_FOLDER = 'uploads'
# Create the upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

_recorder = None
_cfg = None
_most_recent_prompt = (None, None) # tuple containing (prompt_csv_filepath, empty_prompt)

_language_data = None # lazy global


def set_recorder(recorder: ScreenRecorder) -> None:
    global _recorder
    _recorder = recorder

def set_cfg(cfg) -> None:
    global _cfg
    _cfg = cfg

def instantiate_screen_recorder() -> None:
    OCR_settings = _cfg['SettingsOCR']
    _config = r"{}".format(OCR_settings['tesseract_configuration'])
    _time_between_screencaps = float(OCR_settings['time_between_screenshots'])
    _preprocessors = int(OCR_settings['num_of_preprocessors'])
    set_recorder(ScreenRecorder(ocr_lang_code=_language_data.ocr_lang_code,
                                nlp_lang_code=_language_data.nlp_lang_code, 
                                nlp_model=_language_data.nlp_model, 
                                preprocessors=_preprocessors, minimum_confidence=70,
                                config=_config, time_between_screencaps=_time_between_screencaps))
    print("ScreenRecorder is set up")

@app.route('/prompt-feedback', methods=['POST']) # TODO:
def get_prompt_feedback():
    data = request.get_json()
    prompt = prompt_generator.get_most_most_recent_prompt()
    response = data.get('response')
    # Process the response here, e.g., update database or perform logic
    print(f'Response received: {response}')
    
    logger.log_prompt_feedback(prompt[0], prompt[1], response)
    prompt_generator.set_most_recent_prompt(None, None) # clear the most recent prompt

    return jsonify({'status': 'success', 'received': response})

    # print(answer)
    
@app.route('/lesson', methods=['GET'])
def get_lesson(): # # TODO: figure out how to use get_lesson to feed the type of lesson (unique values in the first column 'Type' of prompt CSVs)
    choice = request.args.get('subtitle') or request.args.get('choice') or 'No choice provided'

    prompt_type = request.args.get('prompt_type', 'Any')
    if choice.endswith('.csv'): # naive way to check if they asked for an individual term or a subtitled csv file
        text = logger.get_subtitles_csv(choice)
        for sentence in text:
            terms = prompt_generator.find_parts_of_speech_in_sentence(sentence, ['NOUN', 'ADJ', 'VERB'], _language_data.nlp_model)
            if len(terms) > 0:
                logger.log_terms(terms, 'Number of touches', nlp_lang_code=_language_data.nlp_lang_code, ocr_lang_code=_language_data.ocr_lang_code)
    prompt = prompt_generator.generate_prompt_from_choice(choice, prompt_type)

    llm_response = LLMserver.post_prompt_to_LLM(prompt, _language_data.language, _language_data.proficiency)
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
    learner_profile = logger.get_terms(ocr_lang_code=_language_data.ocr_lang_code, all=True)
    prompt_types = prompt_generator.get_prompt_types(isTerm=True)
    return render_template('learner_profile.html', csv_data=learner_profile, prompt_types=prompt_types)

@app.route('/upload-subtitles', methods=['POST'])
def upload_srt():
     # Check if the file is present in the request
    if 'file' not in request.files:
        return jsonify({'error': 'No file attached'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Process the file here (e.g., parse the .srt file)
    begin_timestamp, end_timestamp = subtitle_upload_parser.get_subtitle_file_bookend_timestamps(file)
    print(f"Timestamps: {begin_timestamp / 60}, {end_timestamp / 60}")
    return jsonify({
        'slider_values': {'min': begin_timestamp / 60, 'max': end_timestamp / 60}
    })

@app.route('/choices', methods=['GET']) # DEPRECATED
def get_choices(part_of_speech='NOUN'):
    text = screenshot_text_extractor.read_text_from_image(filepath=f"{os.getcwd()}/uploads/Screenshot.png", language=_language_data.ocr_lang_code, preprocessing=False, minimum_confidence=50)
    choices = prompt_generator.find_parts_of_speech_in_sentence(text, part_of_speech, _language_data.nlp_model) # TO DO: Make this legit later - be able to pass in POS as arg
    return jsonify(choices)

@app.route('/adjust-bounding-box', methods=['POST'])
def adjust_bounding_box():
    if _recorder is None:
        instantiate_screen_recorder()
    else:
        _recorder.window = _recorder.get_rectangle()
    return jsonify({'status': 'success'})

@app.route('/upload', methods=['POST'])
def upload_image(): 
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
        instantiate_screen_recorder()
    if _recorder.start_recording():
        return jsonify({"status":"success", "message":"Recording started"})
    return jsonify({"status":"error", "message":"Recording already started"})

@app.route('/stop-recording', methods=['POST'])
def stop_recording():
    if _recorder.stop_recording():
        return jsonify({"status":"success", "message":"Recording stopped"})
    return jsonify({"status":"error", "message":"No recording in progress"})

@app.route('/take-screenshot', methods=['POST'])
def take_screenshot():
    if _recorder == None:
        instantiate_screen_recorder()
    try:
        # Create a screenshots directory if it doesn't exist1
        screenshot_dir = 'screenshots'
        os.makedirs(screenshot_dir, exist_ok=True)

        # Generate a unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        full_path = os.path.abspath(os.path.join(screenshot_dir, filename))

        # Take screenshot
        _recorder.take_screenshot()

        return jsonify({
            'message': filename,
            'path': full_path,
            'status': 'success'
        })
    except Exception as e:
        return jsonify({
            'message': f'Error taking screenshot: {str(e)}',
            'status': 'error'
        })
   
@app.route('/submit-subtitle-upload', methods=['POST'])
def submit_subtitle_upload():
    subtitle_file = request.files.get('subtitle_file')
    
    # Get the slider values and convert to seconds
    slider_from = int(float(request.form.get('slider_from'))) * 60 
    slider_to = int(float(request.form.get('slider_to'))) * 60 

    subtitle_file_contents = subtitle_file.read().decode('utf-8')
    print(f"subtitle file: {subtitle_file_contents}") 
    subtitles_dict = subtitle_upload_parser.get_times_and_subtitles_dict(subtitle_file_contents)
    filtered_subtitles = subtitle_upload_parser.filter_subtitles_based_on_timestamp(subtitles_dict, (slider_from, slider_to))
    
    subtitles_list = filtered_subtitles.split("\n")
    try:
        filename = subtitle_file.filename[:subtitle_file.filename.find(".")] + '.csv'
    except:
        filename = subtitle_file.filename + '.csv'
    filepath = os.path.join(config.get_data_directory(), "subtitles", f"{filename}")
    
    try:
        with open(filepath, "x", encoding='utf-8') as file:
            # Convert list to string and write to file
            file.write("\n".join(subtitles_list))
    except:
        with open(filepath, "w", encoding='utf-8') as file:
            # Convert list to string and write to file
            file.write("\n".join(subtitles_list))

    response = {"message": f"File uploaded successfully!"}
    return jsonify(response)

@app.route('/generate', methods=['POST'])
def submit_choice():
    data = request.get_json()  # Get the JSON data from the request body
    selected_subtitle = data.get('subtitle')
    
    response = {"message": f"Loading lesson plan for: {selected_subtitle}..."} ## TODO: change response
    return jsonify(response)

@app.route('/uploads/<filename>')
def get_uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/open-subtitles-folder', methods=['POST'])
def open_subtitles_folder():
    subtitles_path = os.path.normpath(f'{config.get_data_directory()}/subtitles/')

    # Ensure the directory exists
    os.makedirs(subtitles_path, exist_ok=True)

    # Platform-specific file explorer opening
    if platform.system() == 'Windows':
        subprocess.Popen(f'explorer "{subtitles_path}"', shell=True)
    elif platform.system() == 'Darwin':  # macOS
        subprocess.Popen(['open', subtitles_path])
    else:  # Linux and other Unix-like systems
        subprocess.Popen(['xdg-open', subtitles_path])

    return '', 204

@app.route('/open-configuration', methods=['POST'])
def open_configuration():
    subtitles_path = os.path.normpath(f'{config.get_data_directory()}/subtitles/')

    # Ensure the directory exists
    os.makedirs(subtitles_path, exist_ok=True)

    # Platform-specific file explorer opening
    if platform.system() == 'Windows':
        subprocess.Popen(f'explorer "{subtitles_path}"', shell=True)
    elif platform.system() == 'Darwin':  # macOS
        subprocess.Popen(['open', subtitles_path])
    else:  # Linux and other Unix-like systems
        subprocess.Popen(['xdg-open', subtitles_path])

    return '', 204

@app.route('/open-config-file', methods=['POST'])
def open_config_file():
    config_path = os.path.join(config.get_data_directory(), 'config.ini')

    if platform.system() == 'Windows':
        subprocess.Popen(f'notepad "{config_path}"', shell=True)
    elif platform.system() == 'Darwin':  # macOS
        subprocess.Popen(['open', '-t', config_path])
    else:  # Linux
        subprocess.Popen(['xdg-open', config_path])

    return '', 204

@app.route('/open-prompt-directory', methods=['POST'])
def open_prompt_directory():
    prompts_path = os.path.normpath(f'{config.get_data_directory()}/prompts/')

    # Ensure the directory exists
    os.makedirs(prompts_path, exist_ok=True)

    # Platform-specific file explorer opening
    if platform.system() == 'Windows':
        subprocess.Popen(f'explorer "{prompts_path}"', shell=True)
    elif platform.system() == 'Darwin':  # macOS
        subprocess.Popen(['open', prompts_path])
    else:  # Linux and other Unix-like systems
        subprocess.Popen(['xdg-open', prompts_path])

    return '', 204

def start_app():
    startup.make_dirs()
    set_cfg(config.get_config())
    global _language_data
    _language_data = LanguageData()
    print("Config loaded successfully!")
    webbrowser.open('http://127.0.0.1:5000/')
    app.run(port=5000)