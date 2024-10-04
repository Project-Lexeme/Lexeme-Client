from flask import Flask, request, jsonify, render_template_string
import spacy
import typing 
import requests
from openai import OpenAI

app = Flask(__name__)
nlp = spacy.load("en_core_web_sm")
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

def get_embedding(text, model="model-identifier"):
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model=model).data[0].embedding

def get_lm_studio_response(prompt):
    try:
        response = client.chat.completions.create(
            model="local-model",  # Replace with the appropriate model identifier
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error getting LM Studio response: {e}")
        return None

@app.route('/', methods=['GET', 'POST'])
def await_post():
    if request.method == 'POST':
        data = request.json
        text = data.get('text', '')
        print(f"Received text: {text}")

        # Process the text using spaCy
        doc = nlp(text)

        # Extract named entities
        entities = [{'text': ent.text, 'label': ent.label_} for ent in doc.ents]

        # Extract tokens and their parts of speech
        tokens = [{'text': token.text, 'pos': token.pos_} for token in doc]

        # Perform sentiment analysis (basic implementation)
        sentiment = 'positive' if doc.sentiment > 0 else 'negative' if doc.sentiment < 0 else 'neutral'

        # Get embedding from LM Studio
        embedding = get_embedding(text)

        # Get response from LM Studio
        lm_studio_response = get_lm_studio_response(text)

        # Print the LM Studio response to the terminal
        print(f"LM Studio response: {lm_studio_response}")

        # Prepare the response
        response = {
            'original_text': text,
            'entities': entities,
            'tokens': tokens,
            'sentiment': sentiment,
            'embedding': embedding,
            'lm_studio_response': lm_studio_response
        }

        # Post the processed data to another server
        try:
            post_url = "http://127.0.0.1:5001/"  # Assuming this is the URL from post.py
            post_response = requests.post(post_url, json=response)
            if post_response.status_code == 200:
                print("Successfully posted processed data to server")
            else:
                print(f"Failed to post data. Status code: {post_response.status_code}")
        except requests.RequestException as e:
            print(f"Error posting data: {e}")

        return jsonify(response)
    
    elif request.method == 'GET':
        # Create a simple HTML template to display the chat history with auto-refresh
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>NLP Processing Server</title>
            <script>
                function refreshPage() {
                    location.reload();
                }
                setInterval(refreshPage, 5000); // Refresh every 5 seconds
            </script>
        </head>
        <body>
            <h1>Welcome to the NLP processing server</h1>
            <p>Send a POST request with JSON data containing a 'text' field to process.</p>
            <h2>Chat History:</h2>
            <ul>
            {% for message in chat_history %}
                <li><strong>{{ message.role }}:</strong> {{ message.content }}</li>
            {% endfor %}
            </ul>
        </body>
        </html>
        """
        return render_template_string(html_template, chat_history=app.config.get('chat_history', []))

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('text', '')
    conversation = request.json.get('conversation', [])
    
    conversation.append({"role": "user", "content": user_input})
    
    try:
        response = client.chat.completions.create(
            model="local-model",
            messages=conversation,
            max_tokens=150
        )
        ai_response = response.choices[0].message.content
        conversation.append({"role": "assistant", "content": ai_response})
        
        # Print the AI's response to the terminal
        print(f"AI response: {ai_response}")
        
        # Use the AI's response as the new prompt
        new_prompt = ai_response
        
        # Get a new response based on the AI's previous response
        new_response = client.chat.completions.create(
            model="local-model",
            messages=conversation + [{"role": "user", "content": new_prompt}],
            max_tokens=150
        )
        new_ai_response = new_response.choices[0].message.content
        conversation.append({"role": "assistant", "content": new_ai_response})
        
        # Print the new AI response to the terminal
        print(f"New AI response: {new_ai_response}")
        
        # Store the conversation history in the app config
        if 'chat_history' not in app.config:
            app.config['chat_history'] = []
        app.config['chat_history'].extend(conversation)
        
        return jsonify({
            "conversation": conversation,
            "ai_response": new_ai_response
        })
    except Exception as e:
        print(f"Error in chat route: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5001, debug=True)