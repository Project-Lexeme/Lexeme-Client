import spacy
import io
import csv
import random
import pandas as pd
from logger import get_subtitles_csv

def generate_prompt_from_choice(choice: str): # TODO: refine this bad boy to have some more nuance
    if choice.endswith('.csv'):
        data = get_subtitles_csv(choice)
        prompt = f"""The following is a list of line-break-separated subtitles from a movie. Please do not guess what specific movie this comes from. 
        There may be multiple characters in the scene talking in these subtitles. 
        You can ignore errant punctuation marks or individual characters without context.
        What information can you get from this exchange? Please share a paragraph in only simplified Chinese about this situation.
        If there are any useful idioms in the text, could you share a single sentence describing what they mean? 
        '{data}'
        """
        print(data)
        return prompt

    else:         
        # TODO: vary this prompt using the prompt generator functions
        prompt = f"""Could you define what the term {choice} means.  
        Please give me 1 example sentence in simplified Chinese, 
        then give me a multiple choice question in simplified Chinese (without pinyin or English) 
        asking to define {choice} with the answers (again, without pinyin or English) being all single sentence definitions of other terms. 
        Please use realistic distractors but make the correct answer unambiguous. Please state which the correct answer is.
        can you format the Questions with the term {choice}
        giving me the correct answer below given the term {choice} the script under the answer column, and the correct answer has to be within the A to D answer pool
        Finally, end the response by asking, "Did you get it right?" but with a slight variation. 
        Can you also use an HTML paragraph formatting, one line after the next, line break after each paragraph?
        can you use the format "答案是：[insert answer here]"
        can you also add supplementary information to help the language user learn the language in a simplified manner, and give a hint to the user so they can get the correct answer.
        """
        return prompt

def find_parts_of_speech_in_sentence(sentence: str, part_of_speech: str, nlp: spacy.Language) -> list:
    parts_of_speech = []
    doc = nlp(sentence)
    for token in doc:
        #print(f"Token: {token.text}, POS: {token.pos_}, Dependency: {token.dep_}, Head: {token.head.text}") # Lemma: {token.lemma_} <- not used in Chinese
        if token.pos_ == part_of_speech:
            #TODO: get rid of nouns that just don't make damn sense
            parts_of_speech.append(token.text)
    return parts_of_speech

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

def find_greatest_vector_in_sentence(sentence:str, target_parts_of_speech:list[str], nlp: spacy.Language):
    target_vectors = []
    doc = nlp(sentence)
    for target in target_parts_of_speech:
        target_vectors.append() ## need to first find where each target_part of speech belongs int eh whole sentence to refer to it by index.

def generate_prompt_from_list_of_subtitles(csv_filepath: str, prompt: str) -> str:
    '''
    # TODO: think about whether these prompts should also come from a csv so that we can have variety

    filepath - location of csv with recent subtitles
    returns a formatted text string
    '''
    # TODO: take in a csv location and return a formatted text string
    
    return ''

    
def generate_prompt_from_sentence_and_part_of_speech(sentence: str, part_of_speech, nlp: spacy.Language, target_term='random', prompt='random'): 
    '''
    returns a formatted string prompt with target part of speech

    args:
        sentence - string in target language
        
        part_of_speech -    ADJ: adjective
                            ADP: adposition
                            ADV: adverb
                            AUX: auxiliary
                            CCONJ: coordinating conjunction
                            DET: determiner
                            INTJ: interjection
                            NOUN: noun
                            NUM: numeral
                            PART: particle
                            PRON: pronoun
                            PROPN: proper noun
                            PUNCT: punctuation
                            SCONJ: subordinating conjunction
                            SYM: symbol
                            VERB: verb
                            X: other
        
        nlp - spacy.Language, specifically the one you're using in the program - this is passed in as arg so that it can be loaded in server script and not reloaded everytime a prompt is generated
        
        target_term -       'random' returns random
                            'first'
                            'last'
                            'vector' is PLANNED to compare whole sentence versus individual token vector to find the most impactful target_term in the sentence
        
        prompt -            'random' returns random
                            int-type returns corresponding index location of scaffolded prompts
    '''


    assert len(find_parts_of_speech_in_sentence(sentence, part_of_speech, nlp)) > 0, "did not find any target parts of speech"
    target_parts_of_speech = find_parts_of_speech_in_sentence(sentence, part_of_speech, nlp)
    
    print(f'Here are the {part_of_speech}s: {target_parts_of_speech}')
    
    if target_term=="random":
        max_length = len(target_parts_of_speech)-1
        target_part_of_speech = target_parts_of_speech[random.randint(0, max_length)] # returns a random target part of speech

    elif target_term=='first':
        target_part_of_speech = target_parts_of_speech[0]

    elif target_term=='last':
        target_part_of_speech = target_parts_of_speech[-1]

    # elif target_term=='vector':
    #     target_part_of_speech = find_greatest_vector_in_sentence(sentence, target_parts_of_speech, nlp)

    prompts = format_prompts_from_term_and_scaffolded_prompt(target_part_of_speech, "beginner_scaffolded_prompts.csv")

    if prompt=="random":
        max_length = len(prompts)-1
        formatted_prompt = prompts[random.randint(0, max_length)] # returns a random target part of speech

    elif type(prompt)==int:
        formatted_prompt = prompts[prompt]
    
    return formatted_prompt

#sentence = '啊，我猜他可能一只手往塞着披萨，另一只手看管。、要的是了，正在招人有找到了人SupAheod'
#print(generate_prompt_from_sentence_and_part_of_speech(sentence, 'VERB', spacy.load("zh_core_web_sm")))
