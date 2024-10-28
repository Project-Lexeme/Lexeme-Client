# TODO
# check out sample/app2.py for what this might look like and deploy server in here. 
# currently we launch server from LMStudio and this is just a post request. 

# Example: reuse your existing OpenAI setup
from openai import OpenAI


global _url
global _api_key
global _model

def set_url(url):
    global _url
    _url = url

def set_api_key(api_key):
    global _api_key
    _api_key = api_key

def set_model(model):
    global _model
    _model = model 

# Point to the local server
def post_prompt_to_LLM(prompt:str):
    client = OpenAI(base_url=f"{_url}", api_key=f"{_api_key}")

    completion = client.chat.completions.create(
    model=f"{_model}",
    messages=[
        {"role": "system", "content": "You are a Chinese teacher teaching simplified Chinese to English learners. You always provide answers primarily in simplified Chinese but using easy-to-understand terms and examples. You occasionally use an English sentence to explain a difficult concept."},
        {"role": "user", "content": f"{prompt}"}
    ],
    temperature=0.3,
    )

    print(completion.choices[0].message.content)
    return completion.choices[0].message.content
