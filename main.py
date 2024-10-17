from flask import Flask, request, jsonify, send_from_directory, render_template
import spacy
import os
import spacy
import screenshot_text_extractor, prompt_generator
from screen_recorder import ScreenRecorder #select_window, capture_window, clean_filename,
import LLMserver
import logger

# TODO: feed it to an LLM with a prompt explaining that it's subtitles from a movie without a lot of other context, may be multiple characters talking, take its best guess about what the situation is and explain in target language - prompt_generator.py to fuse things together
# TODO: check out Koboldcpp for a means to deploy LLM server 
# TODO: add app.route for LLM response and <div> object in index.html HERE 

app = Flask(__name__)
nlp = spacy.load("zh_core_web_sm") # TODO: pass this into the prompt generator?

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
    term = request.args.get('choice', 'No choice provided')

    # TODO: vary this prompt using the prompt generator functions
    prompt = f"""Could you define what the term {term} means.  
    Please give me 1 example sentence in simplified Chinese, 
    then give me a multiple choice question in simplified Chinese (without pinyin or English) 
    asking to define {term} with the answers (again, without pinyin or English) being all single sentence definitions of other terms. 
    Please use realistic distractors but make the correct answer unambiguous. Please state which the correct answer is.
    can you format the Questions with the term {term}
    giving me the correct answer below given the term {term} the script under the answer column, and the correct answer has to be within the A to D answer pool
    Finally, end the response by asking, "Did you get it right?" but with a slight variation. Can you also use an HTML paragraph formatting, one line after the next, line break after each paragraph?
    can you make 
    with the format "答案是：[insert answer here]"
    
    can you also add supplimentary information to help the language user learn the language in a simplified manner, and give a hint to the user so they can get the correct answer.
    
    """

    llm_response = LLMserver.post_prompt_to_LLM(prompt)
    return render_template('lesson.html', choice=term, llm_response=llm_response)

@app.route('/review-choices')
def get_review_choices():
    choices = logger.get_terms()    
    return jsonify(choices)


@app.route('/choices', methods=['GET'])
def get_choices(part_of_speech='NOUN'):
    text = screenshot_text_extractor.read_text_from_image(filepath=f"E:/ProjectLexeme_Server/uploads/Screenshot.png", language=language, preprocessing=False, minimum_confidence=50)
    choices = prompt_generator.find_parts_of_speech_in_sentence(text, part_of_speech, nlp) # TO DO: Make this legit later - be able to pass in POS as arg
    for choice in choices: logger.log_term(choice, 'Number of touches')
    return jsonify(choices)

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

if __name__ == '__main__':
    recorder = ScreenRecorder(language='chi_sim', use_preprocessing=True, minimum_confidence=50, config=r'', time_between_screencaps=1) #'--oem 3 --psm 11 -l chi_sim'
    nlp = spacy.load("zh_core_web_sm")
    app.run(port=5000)