import requests
import time
import random
from openai import OpenAI

client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

def generate_conversation_starter():
    starters = [
        "Hello! Let's discuss the future of artificial intelligence.",
        "What are your thoughts on renewable energy sources?",
        "How do you think technology will change education in the next decade?",
        "What's your opinion on the ethical implications of genetic engineering?",
        "How might space exploration benefit humanity in the long run?"
    ]
    return random.choice(starters)

def get_lm_studio_response(prompt, conversation):
    try:
        response = client.chat.completions.create(
            model="local-model",
            messages=conversation + [{"role": "user", "content": prompt}],
            max_tokens=150
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error getting LM Studio response: {e}")
        return None

def continuous_chat():
    url = "http://127.0.0.1:5001/chat"
    conversation = []
    
    # Initial conversation starter
    starter = generate_conversation_starter()
    conversation.append({"role": "user", "content": starter})
    current_prompt = starter
    
    while True:
        try:
            ai_response = get_lm_studio_response(current_prompt, conversation)
            if ai_response:
                conversation.append({"role": "assistant", "content": ai_response})
                
                response = requests.post(url, json={"text": current_prompt, "conversation": conversation})
                if response.status_code == 200:
                    print("Successfully sent data to the chat server")
                    print("Chat response:")
                    print(f"Previous: {current_prompt}")
                    print(f"AI: {ai_response}")
                    print("-" * 50)
                    
                    # Use the AI's response as the next prompt
                    current_prompt = ai_response
                    print(f"Next prompt: {current_prompt}")
                    
                    # Post all responses
                    print("All responses:")
                    for msg in conversation:
                        print(f"{msg['role'].capitalize()}: {msg['content']}")
                    print("-" * 50)
                    
                    # Post the new prompt to the server
                    response = requests.post(url, json={"text": current_prompt, "conversation": conversation})
                    if response.status_code == 200:
                        print("Successfully sent new prompt to the chat server")
                    else:
                        print(f"Failed to send new prompt. Status code: {response.status_code}")
                    
                    # Get a new response based on the AI's previous response
                    new_ai_response = get_lm_studio_response(current_prompt, conversation)
                    if new_ai_response:
                        conversation.append({"role": "user", "content": current_prompt})
                        conversation.append({"role": "assistant", "content": new_ai_response})
                        print(f"AI (continued): {new_ai_response}")
                        print("-" * 50)
                        
                        # Post the new AI response to the server
                        response = requests.post(url, json={"text": new_ai_response, "conversation": conversation})
                        if response.status_code == 200:
                            print("Successfully sent new AI response to the chat server")
                        else:
                            print(f"Failed to send new AI response. Status code: {response.status_code}")
                        
                        # Update the current prompt for the next iteration
                        current_prompt = new_ai_response
                else:
                    print(f"Failed to send data. Status code: {response.status_code}")
            else:
                print("Failed to get AI response")
        except requests.RequestException as e:
            print(f"Error sending data: {e}")
        
        time.sleep(1)  # Wait for 1 second before sending the next request

if __name__ == "__main__":
    continuous_chat()