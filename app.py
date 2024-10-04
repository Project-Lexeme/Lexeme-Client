from flask import Flask, request, jsonify, send_from_directory
import spacy
from PIL import Image
from io import BytesIO
import os
import screenshot_text_extractor, prompt_generator
import LLMserver
# import typing 


app = Flask(__name__)
nlp = spacy.load("en_core_web_sm")

# Define the upload folder
UPLOAD_FOLDER = 'uploads'
# Create the upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def run_demo():
    ### DEMO PURPOSES ###
    language = 'chi_sim'
    text = screenshot_text_extractor.read_text_from_image(filepath=f"E:/ProjectLexeme_Server/uploads/Screenshot.png", language=language, preprocessing=False, minimum_confidence=50)
    
    prompt = prompt_generator.generate_prompt_from_sentence_and_part_of_speech(text)
    print(f'The prompt is: "{prompt}"')
    LLMserver.post_prompt_to_LLM(prompt)


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
    
    # could conveyor belt images here
    # Save the file to the designated folder
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    #run_demo()

    return jsonify({'message': 'Image received and processed'}), 200
    

@app.route('/uploads/<filename>')
def get_uploaded_file(filename):
    # conveyor belt the images
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# @app.route('/LLMResponse')
# def handleLLMResponse()


if __name__ == '__main__':
    app.run(port=5000)