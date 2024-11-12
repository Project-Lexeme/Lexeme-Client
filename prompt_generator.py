import re
import spacy
import csv
import random
import pandas as pd
import config


# TODO TODAY: generate_prompt_from_choice needs to pull from csvs for end users to customize
def generate_prompt_from_choice(choice: str) -> str: # TODO: create thread from user proficiency choice and type of intended lesson to point to the correct {proficiency}_subtitle_prompt_csv
    if choice.endswith('.csv'):
        #data = get_subtitles_csv(choice)
        prompt = generate_prompt_from_list_of_subtitles(f'{config.get_data_directory()}/prompts/intermediate_subtitle_prompts.csv', f'{config.get_data_directory()}/subtitles/{choice}')
        print(prompt)
        return prompt

    else:         
        # TODO: vary this prompt using the prompt generator functions
        prompt = f"""
        The following is a list of vocabulary terms in my target language that I would like to study. {choice}. 
        Could you write me a short description of each one in English with a sample sentence in Chinese? 
        If you know any good cultural tidbits that are relevant to the term, share that too!
        """
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
def format_prompts_from_term_and_scaffolded_prompt(term: str, scaffolded_prompts_csv_filename: str) -> list[str]:
    scaffolded_prompts = load_scaffolded_prompts(scaffolded_prompts_csv_filename)
    list_of_prompts = []
    for p in scaffolded_prompts: 
        f_str = p[0].format(term)
        list_of_prompts.append(f_str)
    return list_of_prompts

def load_chinese_samples_csv(file_name: str) -> list[str]:
    with open(f"{file_name}", 'r', encoding='utf-8') as f:
        sample_sentences = csv.reader(f, delimiter='\n')
        list_of_sentences = []
        for s in sample_sentences:
            list_of_sentences.append(s)
    return list_of_sentences

def load_scaffolded_prompts(file_name: str) -> list[str]:
    with open(f"{file_name}", 'r', encoding='utf-8') as f:
        scaffolded_prompts = csv.reader(f, delimiter='\n')
        list_of_scaffolded_prompts = []
        for s in scaffolded_prompts:
            list_of_scaffolded_prompts.append(s)
    return list_of_scaffolded_prompts

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

def generate_prompt_from_list_of_subtitles(prompt_csv_filepath: str, subtitles_csv_filepath: str, prompt_type: str = 'summary') -> str:
    '''
    supported prompt_type is based on coumn in subtitle_prompts csv. currently just 'summary'
    
    returns a formatted text string that is the prompt to send to the LLM
    '''
    prompt_df = pd.read_csv(prompt_csv_filepath)
    if prompt_type == 'summary':
        filtered_df = prompt_df[prompt_df['Type'] == 'Summary']

    # else if prompt_type == 'grammar_lesson'
        # filtered_df = df[df['Type'] == 'Grammar Lesson']

    max_index = len(filtered_df)
    empty_prompt = filtered_df.loc[random.randrange(0,max_index),'Prompt']
    
    subtitle_df = pd.read_csv(subtitles_csv_filepath, sep='/n', engine='python')
    subtitle_str = '\n'.join(subtitle_df.iloc[:,0].astype(str).tolist())

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

    prompts: list[str]= format_prompts_from_term_and_scaffolded_prompt(target_part_of_speech, "beginner_scaffolded_prompts.csv")

    if prompt=="random":
        max_length = len(prompts)-1
        formatted_prompt = prompts[random.randint(0, max_length)] # returns a random target part of speech

    elif type(prompt)==int:
        formatted_prompt = prompts[prompt]
    
    return formatted_prompt

# sentence = 'Я вижу собаку, 고양이가 나무에 올라가요, 猫在树上, стол 자동차 un chat est sur la table, и это замечательно 你好，最近怎麼樣? Bonjour, comment ça va 어떻게 지내세요、こんにちは、お元気ですか要的是了，正在招人有找到了人SupAheod () 1010万'
# langs = ['zh_core_web_sm', "fr_core_news_sm", "ja_core_news_sm", "ko_core_news_sm", "ru_core_news_sm"]
# for l in langs: 
#     print(find_parts_of_speech_in_sentence(sentence, 'NOUN', spacy.load(l)))