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
def post_prompt_to_LLM(prompt:str, target_language: str, proficiency: str):
    """Posts prompt to LLM

    Args:
        prompt (str): formatted prompt
        target_language (str): language_data.language
        proficiency (str): language_data.proficiency

    Returns:
        str: 'content' block of LLM response JSON
    """
    client = OpenAI(base_url=f"{_url}", api_key=f"{_api_key}")

    completion = client.chat.completions.create(
    model=f"{_model}",
    messages=[
        {"role": "system", "content": f"You are a {target_language} teacher teaching {target_language} to English-speaking learners who have a proficiency level of '{proficiency}'. Anytime I ask you to speak in the target language, I'm referring to {target_language}. Unless otherwise requested, you always provide answers primarily in {target_language} but using easy-to-understand terms and examples. You occasionally use an English sentence to explain a difficult concept."},
        {"role": "user", "content": f"{prompt}"}
    ],
    temperature=0.3,
    )

    print(completion.choices[0].message.content)
    return completion.choices[0].message.content

# set_url("http://10.0.0.16:1234/V1")
# set_model("aya-23-8b@f16:2")
# set_api_key('lm-studio')
# post_prompt_to_LLM("Testing here")