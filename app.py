from flask import Flask, request, jsonify, send_from_directory
import spacy
from PIL import Image
from io import BytesIO
import os
import spacy
import screenshot_text_extractor, prompt_generator
import LLMserver
import random


# TODO: add app.route for LLM response and <div> object in index.html



app = Flask(__name__)
nlp = spacy.load("zh_core_web_sm") # TODO: pass this into the prompt generator?

# Define the upload folder
UPLOAD_FOLDER = 'uploads'
# Create the upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def run_demo_with_LLM():
    ### DEMO PURPOSES ###
    language = 'chi_sim'
    text = screenshot_text_extractor.read_text_from_image(filepath=f"E:/ProjectLexeme_Server/uploads/Screenshot.png", language=language, preprocessing=True, minimum_confidence=50)
    
    prompt = prompt_generator.generate_prompt_from_sentence_and_part_of_speech(text)
    print(f'The prompt is: "{prompt}"')
    LLMserver.post_prompt_to_LLM(prompt)

@app.route('/choices', methods=['GET'])
def get_choices():
    text = screenshot_text_extractor.read_text_from_image(filepath=f"E:/ProjectLexeme_Server/uploads/Screenshot.png", language=language, preprocessing=False, minimum_confidence=50)
    choices = prompt_generator.find_parts_of_speech_in_sentence(text, 'NOUN', nlp) # TO DO: Make this legit later
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

    #run_demo()

    return jsonify({'message': 'Image received and processed'}), 200

# TODO: add app.route for LLM response and <div> object in index.html HERE

@app.route('/submit', methods=['POST'])
def submit_choice():
    data = request.get_json()  # Get the JSON data from the request body
    selected_choice = data.get('choice')
    print(selected_choice)
    scaffolded_prompts =  prompt_generator.load_scaffolded_prompts("beginner_scaffolded_prompts.csv")
    scaffolded_prompt = scaffolded_prompts[random.randint(0,len(scaffolded_prompts)-1)][0] 
    prompt = scaffolded_prompt.format(selected_choice) ## here
    
    response = {"message": f"This is your prompt: {prompt}"} ## TODO: change response
    return jsonify(response)

@app.route('/uploads/<filename>')
def get_uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    language = 'chi_sim'
    nlp = spacy.load("zh_core_web_sm")
    app.run(port=5000)