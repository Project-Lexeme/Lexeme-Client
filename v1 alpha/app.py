from flask import Flask, request, jsonify
import spacy
import typing 


app = Flask(__name__)
nlp = spacy.load("en_core_web_sm")

# def print_processed_text(): 
    
#     return "<p>Hello, World! </p>"
# def handle_post(data):
#     text = data.get('text','')
#     return f"<p>{text}</p>"
@app.route('/', methods=['GET','POST'])
def await_post(): 
    if request.method == 'POST':
        
        data = request.json # calls request.get_json() with default args
        text = data.get('text','')
        print(f"{text} is the text object")
        
        
    
    return ""
    #doc = nlp(text)
    # Process and prepare your response
    #jsonify({"tokens": [token.text for token in doc]})
    




if __name__ == '__main__':
    app.run(port=5000)