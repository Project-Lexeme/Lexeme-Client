import spacy
from spacy.pipeline.dep_parser import DEFAULT_PARSER_MODEL
import io
import csv
import random

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

