import requests


def sample_post():
    url = "http://127.0.0.1:5000"
    text = {"text": "Hello world"}
    requests.post(url, json=text)
    

sample_post()