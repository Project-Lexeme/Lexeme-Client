from flask import Flask, request, jsonify, send_from_directory, render_template
import spacy
import os
import spacy
import screenshot_text_extractor, prompt_generator
import LLMserver
import random
import logger


# TODO: add app.route for LLM response and <div> object in index.html
# TODO: design scaffold for definition, examples, and a question
# 
# DONE: add all terms to touched_terms CSV for review



app = Flask(__name__)
nlp = spacy.load("zh_core_web_sm") # TODO: pass this into the prompt generator?

# Define the upload folder
UPLOAD_FOLDER = 'uploads'
# Create the upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/lesson', methods=['GET'])
def get_lesson():
    term = request.args.get('choice', 'No choice provided')
    prompt = f"""Could you define what the term {term} means, with the definition both in simplified Chinese and English. 
    Please give me 1 example sentence in simplified Chinese with an English description, 
    then give me a multiple choice question in simplified Chinese (without pinyin or English) 
    asking to define {term} with the answers (again, without pinyin or English) being all single sentence definitions of other terms that relate to {term}. 
    Please use realistic distractors but make the correct answer unambiguous. 
    Finally, end the response by asking, "Did you get it right?" but with a slight variation. Can you also add an HTML line break after each paragraph?"""
    llm_response = LLMserver.post_prompt_to_LLM(prompt)
    return render_template('lesson.html', choice=term, llm_response=llm_response)

@app.route('/choices', methods=['GET'])
def get_choices(part_of_speech='NOUN'):
    text = screenshot_text_extractor.read_text_from_image(filepath=f"E:/ProjectLexeme_Server/uploads/Screenshot.png", language=language, preprocessing=False, minimum_confidence=50)
    choices = prompt_generator.find_parts_of_speech_in_sentence(text, part_of_speech, nlp) # TO DO: Make this legit later - be able to pass in POS as arg
    for choice in choices: logger.log(choice, 'Number of touches')
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
    
    # print(selected_choice)
    # scaffolded_prompts =  prompt_generator.load_scaffolded_prompts("beginner_scaffolded_prompts.csv")
    # scaffolded_prompt = scaffolded_prompts[random.randint(0,len(scaffolded_prompts)-1)][0] 
    # prompt = scaffolded_prompt.format(selected_choice) ## here
    
    response = {"message": f"Loading lesson plan for: {selected_choice}..."} ## TODO: change response
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