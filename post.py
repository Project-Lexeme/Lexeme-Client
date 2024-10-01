import requests
import prompt_generator


def sample_post():
    url = "http://127.0.0.1:5000"
    text = {"text": "Hello world"}
    requests.post(url, json=text)
    

prompt_generator.generate_prompts_from_scaffolded_prompts_and_sentences("beginner_scaffolded_prompts.csv", 'chinese_samples.csv')

#sample_post()