import re
import spacy
import csv
import random
import pandas as pd
import config

def generate_prompt_from_choice(choice: str) -> str: # TODO: find way to get type of lesson as a subchoice from flask
    if choice.endswith('.csv'):
         # TODO: find means to getting prompt_type param in here
        prompt_csv_filepath = f'{config.get_data_directory()}/prompts/subtitle_prompts.csv'
        subtitles_csv_filepath = f'{config.get_data_directory()}/subtitles/{choice}'
        prompt = generate_prompt_from_list_of_subtitles(prompt_csv_filepath, subtitles_csv_filepath)
        return prompt

    else:         
        # TODO: find means to getting prompt_type param in here
        prompt_csv_filepath = f'{config.get_data_directory()}/prompts/term_prompts.csv'
        prompt = generate_prompt_from_term_and_scaffolded_prompts(choice, prompt_csv_filepath)
        print(prompt)
        return prompt

def find_parts_of_speech_in_sentence(sentence: str, part_of_speech: list, nlp: spacy.Language) -> list[str]:
    filtered_sentence: str = filter_different_scripts(sentence, nlp)
    print(filtered_sentence)
    parts_of_speech: list[str] = []
    doc = nlp(filtered_sentence)
    for token in doc:
        if token.pos_ in part_of_speech:
            #TODO: get rid of nouns that just don't make damn sense
            parts_of_speech.append(token.text)
    return parts_of_speech

def filter_different_scripts(sentence: str, nlp: spacy.Language) -> str:
    '''
    filter sentence to remove all characters not in a target script
    '''
    lang = nlp.meta['lang'] # returns two-letter spacy lang code e.g. en for English, fr for French
    pattern_dict = {'en':'A-Za-zÀ-ÿ ', 'zh':'一-龯 ', 'ko':'가-힣 ', 'ru':'\u0400-\u04FF ', 'ja':'ァ-ヴぁ-ゔー '} # regex patterns that capture each target script INCLUDE A SPACE
    if lang in pattern_dict:
        pattern = pattern_dict[lang]
    else:
        pattern = pattern_dict['en'] # this is a catch-all for Latin-based languages
    filtered_sentence = re.findall(fr'[{pattern}]', sentence)
    return ''.join(filtered_sentence)

#TODO add kwarg to either pass in 'random' or specific prompt index and return only ONE prompt
def generate_prompt_from_term_and_scaffolded_prompts(term: str, prompts_csv_filename: str, prompt_type: str='Any') -> list[str]:
    '''
    prompt_type: first column unique values in scaffolded_prompts.csv
        Any, Definition, Example, Idiom, Lesson, Culture, or Mistake

    '''
    scaffolded_prompts = pd.read_csv(prompts_csv_filename)
    
    if prompt_type != 'Any':
        scaffolded_prompts = scaffolded_prompts[scaffolded_prompts['Type'] == prompt_type]
    
    random_index = random.randint(0, len(scaffolded_prompts) - 1)
    formatted_prompt = scaffolded_prompts.iloc[random_index, 1].format(term) # 0 index is type, 1 is prompt
    return formatted_prompt

def load_chinese_samples_csv(file_name: str) -> list[str]:
    with open(f"{file_name}", 'r', encoding='utf-8') as f:
        sample_sentences = csv.reader(f, delimiter='\n')
        list_of_sentences = []
        for s in sample_sentences:
            list_of_sentences.append(s)
    return list_of_sentences

def get_prompt_types(prompt_csv_filename: str) -> list[str]:
    prompt_filepath = f'{config.get_data_directory()}/prompts/{prompt_csv_filename}'
    prompt_df = pd.read_csv(prompt_filepath)
    prompt_types = prompt_df.iloc[:, 0].unique()
    return prompt_types

def save_prompts(list_of_prompts: list) -> None: 
    df = pd.Series(list_of_prompts)
    df2 = pd.read_csv(f'{config.get_data_directory()}/prompts.csv').iloc[:,0]
    concat_df: pd.DataFrame = pd.DataFrame(pd.concat([df2, df], ignore_index=True).drop_duplicates(inplace=True))
    concat_df.to_csv(f'{config.get_data_directory()}/prompts.csv', index=False)

def find_greatest_vector_in_sentence(sentence:str, target_parts_of_speech:list[str], nlp: spacy.Language) -> None: # TODO: reconsider/implement this
    target_vectors = []
    # doc = nlp(sentence)
    # for target in target_parts_of_speech:
    #     target_vectors.append() ## need to first find where each target_part of speech belongs int eh whole sentence to refer to it by index.

def generate_prompt_from_list_of_subtitles(prompt_csv_filepath: str, subtitles_csv_filepath: str, prompt_type: str = 'Summary') -> str:
    '''
    prompt_type: Summary, Lesson, Quiz, Any
    
    returns a formatted text string that is the prompt to send to the LLM
    '''
    prompt_df = pd.read_csv(prompt_csv_filepath)
    if prompt_type == 'Any':
        filtered_df = prompt_df
    else:
        filtered_df = prompt_df[prompt_df['Type'] == prompt_type]

    max_index = len(filtered_df)
    empty_prompt = filtered_df.loc[random.randrange(0,max_index),'Prompt'] # randomly pulls based on filtered_df
    
    subtitle_df = pd.read_csv(subtitles_csv_filepath, sep='/n', engine='python')
    subtitle_str = '\n'.join(subtitle_df.iloc[:,0].astype(str).tolist()) # adds all rows in subtitle file to list and casts appropriately

    formatted_prompt = empty_prompt.format(f'\n{subtitle_str}')
    return formatted_prompt

    
def generate_prompt_from_sentence_and_part_of_speech(sentence: str, part_of_speech, nlp: spacy.Language, target_term='random', prompt='random') -> str: 
    '''
    returns a formatted string prompt with target part of speech

    args:
        sentence - string in target language
        
        part_of_speech -    ADJ: adjective, ADP: adposition, ADV: adverb, AUX: auxiliary, CCONJ: coordinating conjunction, DET: determiner
                            INTJ: interjection, NOUN: noun, NUM: numeral, PART: particle, PRON: pronoun, PROPN: proper noun, PUNCT: punctuation
                            SCONJ: subordinating conjunction, SYM: symbol, VERB: verb, X: other
        
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
    
    if target_term=="random":
        max_length = len(target_parts_of_speech)-1
        target_part_of_speech = target_parts_of_speech[random.randint(0, max_length)] # returns a random target part of speech

    elif target_term=='first':
        target_part_of_speech = target_parts_of_speech[0]

    elif target_term=='last':
        target_part_of_speech = target_parts_of_speech[-1]

    # elif target_term=='vector':
    #     target_part_of_speech = find_greatest_vector_in_sentence(sentence, target_parts_of_speech, nlp)

    # prompts: list[str]= format_prompt_from_term_and_scaffolded_prompts(target_part_of_speech, "beginner_scaffolded_prompts.csv")

    # if prompt=="random":
    #     max_length = len(prompts)-1
    #     formatted_prompt = prompts[random.randint(0, max_length)] # returns a random target part of speech

    # elif type(prompt)==int:
    #     formatted_prompt = prompts[prompt]
    
    return #formatted_prompt


if __name__ == '__main__':
    generate_prompt_from_term_and_scaffolded_prompts('HEHEHE', f'data/prompts/term_prompts.csv')