import os
import csv
import random
import pandas as pd
import numpy as np

from src import config


_empty_prompt = None
_prompt_csv_filepath = None

def generate_prompt_from_choice(choice: str, prompt_type: str) -> str:
    if choice.endswith('.csv'):
        prompt_csv_filepath = os.path.join(config.get_data_directory(), "prompts", "subtitle_prompts.csv")
        subtitles_csv_filepath = os.path.join(config.get_data_directory(), "subtitles", f"{choice}")
        print(f'subtitle csv filepath: {subtitles_csv_filepath}')
        prompt = generate_prompt_from_list_of_subtitles(prompt_csv_filepath, subtitles_csv_filepath, prompt_type)
        print(f'You just asked the LLM the following: {prompt}')
        return prompt

    else:         
        prompt_csv_filepath = os.path.join(config.get_data_directory(), "prompts", "term_prompts.csv")
        prompt = generate_prompt_from_term_and_scaffolded_prompts(choice, prompt_csv_filepath, prompt_type)
        print(f'You just asked the LLM the following: {prompt}')
        return prompt


#TODO add kwarg to either pass in 'random' or specific prompt index and return only ONE prompt
def generate_prompt_from_term_and_scaffolded_prompts(term: str, prompts_csv_filename: str, prompt_type: str='Any Type') -> list[str]:
    '''
    prompt_type: first column unique values in scaffolded_prompts.csv
        Any, Definition, Example, Idiom, Lesson, Culture, or Mistake

    '''
    empty_prompts = pd.read_csv(prompts_csv_filename)
    
    if prompt_type != 'Any':
        empty_prompts = empty_prompts[empty_prompts['Type'] == prompt_type]
    
    selected_index = select_index_from_score_probability(empty_prompts) 
    empty_prompt = empty_prompts.iloc[selected_index, 1]
    set_most_recent_prompt(prompts_csv_filename, empty_prompt)
    formatted_prompt = empty_prompt.format(term) # 0 index is type, 1 is prompt
    return formatted_prompt

def select_index_from_score_probability(empty_prompts):
    '''
    pass in empty_prompts pd.DataFrame, probabilistically select one based on score and return its index. 
    Model is: probabilities = ( (Scores * variance(scores)) + ((-1 * min(Scores * variance(scores))) + 1) ) / sum(above scaled Scores)
    '''
    scores = np.array(empty_prompts.loc[:,'Score']).astype(float) # this works returning a pd.series
    variance = np.var(scores)
    scores *= variance
    min = np.min(scores)
    shift = (-1 * min) + 1
    scores += shift
    sum_scores = np.sum(scores)
    scores /= sum_scores
    selected_index = random.choices(np.arange(scores.size), weights=scores, k=1)  
    return selected_index[0]

def load_chinese_samples_csv(file_name: str) -> list[str]:
    with open(f"{file_name}", 'r', encoding='utf-8') as f:
        sample_sentences = csv.reader(f, delimiter='\n')
        list_of_sentences = []
        for s in sample_sentences:
            list_of_sentences.append(s)
    return list_of_sentences

def get_prompt_types(isTerm: bool) -> list[str]:
    if isTerm:
        prompt_filepath = os.path.join(config.get_data_directory(), "prompts", "term_prompts.csv")
    else:
        prompt_filepath = os.path.join(config.get_data_directory(), "prompts", "subtitle_prompts.csv")
    prompt_df = pd.read_csv(prompt_filepath)
    prompt_types = prompt_df.iloc[:, 0].unique().tolist()
    return prompt_types

def save_prompts(list_of_prompts: list) -> None: # FUTURE feature: to save historical prompts? may be useless
    # df = pd.Series(list_of_prompts)
    # read_filepath = os.path.join(config.get_data_directory(), "prompts.csv")
    # df2 = pd.read_csv(f'{read_filepath}').iloc[:,0]
    # concat_df: pd.DataFrame = pd.DataFrame(pd.concat([df2, df], ignore_index=True).drop_duplicates(inplace=True))
    # concat_df.to_csv(f'{config.get_data_directory()}/prompts.csv', index=False)
    return 

def generate_prompt_from_list_of_subtitles(prompt_csv_filepath: str, subtitles_csv_filepath: str, prompt_type: str = 'Any Type') -> str:
    '''
    prompt_type: Summary, Lesson, Quiz, Any. Will likely add more. 
    returns a formatted text string that is the prompt to send to the LLM
    '''
    prompt_df = pd.read_csv(prompt_csv_filepath)
    if prompt_type == 'Any Type':
        filtered_df = prompt_df
    else:
        filtered_df = prompt_df[prompt_df['Type'] == prompt_type]
    
    selected_index = select_index_from_score_probability(filtered_df)
    empty_prompt = filtered_df.iloc[selected_index, 1] 

    set_most_recent_prompt(prompt_csv_filepath, empty_prompt) # set global var in app - YES this is a godawful way to do this
    subtitle_df = pd.read_csv(subtitles_csv_filepath, sep='/n', engine='python')
    subtitle_str = '\n'.join(subtitle_df.iloc[:,0].astype(str).tolist()) # adds all rows in subtitle file to list and casts appropriately
    # format beginning and end of script here
    prompt_beginning = "The following is a list of line-break-separated subtitles from a video, possibly a movie. Please do not guess what specific video this comes from. There may be multiple characters in the scene talking in these subtitles. You can ignore errant punctuation marks or individual characters without context. "
    prompt_ending = " Please use HTML-formatted <p> paragraphs in your response.  Subtitles: '{}'"
    formatted_prompt = prompt_beginning + empty_prompt + prompt_ending.format(f'\n{subtitle_str}')
    return formatted_prompt

def set_most_recent_prompt(prompt_csv_filepath, empty_prompt):
    global _prompt_csv_filepath
    _prompt_csv_filepath = prompt_csv_filepath
    global _empty_prompt
    _empty_prompt = empty_prompt

def get_most_most_recent_prompt():
    return _prompt_csv_filepath, _empty_prompt

if __name__ == '__main__':
    select_index_from_score_probability(pd.read_csv('./data/prompts/subtitle_prompts.csv'))