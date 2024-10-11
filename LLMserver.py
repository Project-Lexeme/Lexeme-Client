# TODO
# check out sample/app2.py for what this might look like and deploy server in here. 
# currently we launch server from LMStudio and this is just a post request. 

# Example: reuse your existing OpenAI setup
from openai import OpenAI

# Point to the local server
def post_prompt_to_LLM(prompt:str):
    client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

    completion = client.chat.completions.create(
    model="mradermacher/aya-23-8B-GGUF",
    messages=[
        {"role": "system", "content": "You are a Chinese teacher teaching simplified Chinese to English learners. You always provide answers primarily in simplified Chinese but using easy-to-understand terms and examples. You occasionally use an English sentence to explain a difficult concept."},
        {"role": "user", "content": f"{prompt}"}
    ],
    temperature=0.3,
    )

    print(completion.choices[0].message.content)
    return completion.choices[0].message.content
