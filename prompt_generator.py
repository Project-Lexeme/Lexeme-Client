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


def find_parts_of_speech_in_sentence(sentence: str, part_of_speech: str) -> list:
    nlp = spacy.load("zh_core_web_sm")
    nouns = []
    doc = nlp(sentence)
    for token in doc:
        #print(f"Token: {token.text}, POS: {token.pos_}, Dependency: {token.dep_}, Head: {token.head.text}") # Lemma: {token.lemma_} <- not used in Chinese
        if token.pos_ == part_of_speech:
            #TODO: get rid of nouns that just don't make damn sense
            nouns.append(token.text)
    return nouns

#TODO add kwarg to either pass in 'random' or specific prompt index and return only ONE prompt
def format_prompts_from_term_and_scaffolded_prompt(term: str, scaffolded_prompts_csv_filename: str) -> list:
    scaffolded_prompts = load_scaffolded_prompts(scaffolded_prompts_csv_filename)
    list_of_prompts = []
    for p in scaffolded_prompts: 
        f_str = p[0].format(term)
        list_of_prompts.append(f_str)
    return list_of_prompts

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

def save_prompts(list_of_prompts: list): 
    df = pd.Series(list_of_prompts)
    df2 = pd.read_csv('prompts.csv').iloc[:,0]
    concat_df = pd.concat([df2, df], ignore_index=True).drop_duplicates(inplace=True)
    concat_df.to_csv('prompts.csv', index=False)
    
    
def generate_prompt_from_sentence_and_part_of_speech(sentence: str, part_of_speech='NOUN'): # defaults to noun, not sure if ideal behavior
    assert len(find_parts_of_speech_in_sentence(sentence, part_of_speech)) > 0, "did not find any target parts of speech"
    noun = find_parts_of_speech_in_sentence(sentence, part_of_speech)[0]
    prompt = format_prompts_from_term_and_scaffolded_prompt(noun, "beginner_scaffolded_prompts.csv")[0] 
    return prompt

