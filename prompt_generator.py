import spacy
from spacy.pipeline.dep_parser import DEFAULT_PARSER_MODEL
import io
import csv
import random
import pandas as pd

# this prompt-generating script needs to take in a string, whether it be full sentences or whatever our OCR thing can gen up
# figure out what parts of speech are in there to derive nouns, verbs, etc. into meaningful prompts
# these parts of speech need to be stored in a database-like object (could just be a .csv)
# further thought could be given to what to do with these sentences/fragments that are spit out by OCR.
# process each image individually and add them as row to the CSV in here

# in unity game, create a timer that sends a screengrab every second
# when this screencap gets to the server, process each image individually and add them as row to the CSV in here



# def generate_from_sentence(sentence):
#     prompts = []
#     for s in sentence:
#         prompt = call_function_below(s)
#         prompts.append(prompt)
#    return prompts

# def find_noun_in_sentence():
    
    
#     return noun

# def generate_from_noun_and_scaffolded_prompt():
    
#     return prompt



# need to take in ONE STRING/ONE SENTENCE
def generate_prompts_from_scaffolded_prompts_and_sentences(scaffolded_prompts_csv_filename: str, sample_sentences_csv_filename: str) -> list:
    nlp = spacy.load("zh_core_web_sm")
    chinese_samples = load_chinese_samples_csv(sample_sentences_csv_filename)
    noun_list = []
    for s in chinese_samples:
        doc = nlp(s[0])
        for token in doc:
            #print(f"Token: {token.text}, POS: {token.pos_}, Dependency: {token.dep_}, Head: {token.head.text}") # Lemma: {token.lemma_} <- not used in Chinese
            if token.pos_ == 'NOUN':
                #TODO: get rid of nouns that just don't make damn sense
                noun_list.append(token.text)

    noun_list_len = len(noun_list)

    scaffolded_prompts = load_scaffolded_prompts(scaffolded_prompts_csv_filename)
    list_of_prompts = []
    for p in scaffolded_prompts: 
        target_vocab = noun_list[random.randint(0, noun_list_len)]
        f_str = p[0].format(target_vocab)
        list_of_prompts.append(f_str)
        print(f_str)

    return list_of_prompts # need to return ONE PROMPT


def load_chinese_samples_csv(file_name: str) -> list:
    with open(f"{file_name}", 'r', encoding='utf-8') as f:
        sample_sentences = csv.reader(f, delimiter='\n')
        list_of_sentences = []
        for s in sample_sentences:
            list_of_sentences.append(s)
    return list_of_sentences

def load_scaffolded_prompts(file_name: str) -> list:
    with open(f"{file_name}", 'r', encoding='utf-8') as f:
        scaffolded_prompts = csv.reader(f, delimiter='\n')
        list_of_scaffolded_prompts = []
        for s in scaffolded_prompts:
            list_of_scaffolded_prompts.append(s)
    return list_of_scaffolded_prompts



# process each image individually and add them as row to the CSV in here

# in unity game, create a timer that sends a screengrab every second
# when this screencap gets to the server, process each image individually and add them as row to the CSV in here
def save_prompts(list_of_prompts: list): 
    df = pd.Series(list_of_prompts)
    df2 = pd.read_csv('prompts.csv').iloc[:,0]
    concat_df = pd.concat([df2, df], ignore_index=True).drop_duplicates(inplace=True)
    concat_df.to_csv('prompts.csv', index=False)
    
    

save_prompts(list_of_prompts=["kajsndkj", "for real though i'm nervous this doesn't work", "recall"])

