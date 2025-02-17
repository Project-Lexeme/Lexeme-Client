from pathlib import Path
import pandas as pd
import os

from src import config
from src import dictionary

def check_for_learner_profile(ocr_lang_code: str):
    """Checks for learner profile with OCR lang code prefix

    Args:
        ocr_lang_code (str): Tesseract OCR-friendly lang code, 
    """
    csv_file = Path(f'{config.get_data_directory()}/{ocr_lang_code}_learner_profile.csv')
    if not csv_file.is_file():  # Check if the file exists
        # If it doesn't exist, create it
        csv_file.touch()
        with csv_file.open('w') as f:
            f.write('Term,Number of touches,Number correct,Number incorrect\n') 

def log_terms(terms: list[str], on: str, nlp_lang_code: str, ocr_lang_code: str) -> None:
    '''
    on - the column name to increment. So far, 'Number of touches', 'Number correct', 'Number incorrect'
    '''
    check_for_learner_profile(ocr_lang_code)  # Assuming this checks if profile exists

    # Read existing learner profile (if it exists)
    learner_profile_path = os.path.join(config.get_data_directory(), f"{ocr_lang_code}_learner_profile.csv")
    if os.path.exists(learner_profile_path):
        touched_terms = pd.read_csv(learner_profile_path)

    # Fetch term dictionary contents (this will be used for merging additional information)
    term_dictionary_contents = dictionary.get_term_dictionary_contents(terms, ocr_lang_code)

    # Clean up terms by stripping spaces and ensuring they are in a common case (lowercase, for example)
    terms = [term.strip().lower() for term in terms]
    term_dictionary_contents['term'] = term_dictionary_contents['term'].str.strip().str.lower()

    # Prepare the DataFrame with the terms and the default value for 'on'
    to_concat = pd.DataFrame({'Term': terms, on: [1] * len(terms)})

    # If dictionary contents exist, merge them with the terms DataFrame
    if len(term_dictionary_contents) > 0:
        # Merge with a left join (all terms included, even if no match in dictionary)
        to_concat = to_concat.merge(term_dictionary_contents, left_on='Term', right_on='term', how='right').drop(columns=['term'])
    else:
        # If no dictionary contents, just ensure terms are added with 'NaN' for missing columns
        to_concat['definition'] = None  # Assuming you have a column like 'definition' in your dictionary

    # Append the new terms and their data to the learner profile DataFrame
    touched_terms = pd.concat([touched_terms, to_concat], axis=0).reset_index(drop=True).fillna(0)

    # Handle duplicates by summing the 'on' column for duplicate terms and retaining other columns
    # Here, we keep the first value for each column (definition, other columns, etc.)
    grouped_terms = touched_terms.groupby('Term', as_index=False).agg({on: 'sum', 'definition': 'sum'})
    
    # Also handle any additional columns (e.g., 'other1', 'other2', etc.) by keeping the first value
    for column in touched_terms.columns:
        if column not in ['Term', on, 'definition']:
            grouped_terms[column] = touched_terms.groupby('Term')[column].first().values

    # Save the updated learner profile to CSV
    grouped_terms.to_csv(learner_profile_path, index=False)


def get_terms(ocr_lang_code: str, sort_by='weakest', qty=0, all=False):
    """Returns learner profile contents for selected language

    Args:
        ocr_lang_code (str): Tesseract OCR-friendly code to math how learner_profiles are named, e.g. "chi_sim"
        sort_by (str, optional): Yet to be implemented. Defaults to 'weakest'.
        qty (int, optional): Number of terms to return. Defaults to 0, which signififies ALL.
        all (bool, optional): whether all fields associated with a term (e.g. definition) are returned or just the term. Defaults to False.

    Returns:
        List[List[str]]: returns a list of terms or a list of lists of terms and their contents
    """

    terms_df = pd.read_csv(os.path.join(config.get_data_directory(),f"{ocr_lang_code}_learner_profile.csv"))
    terms_df.fillna('', inplace=True)
    
    if all == True:
        terms = [terms_df.columns.tolist()] + terms_df.values.tolist()

    else:
        terms = terms_df['Term'].to_list()

    # if sort_by == 'weakest': ## TODO: add in actual support for sorting here
    #     terms = terms_df['Term'].to_list()
    if qty == 0:
        return terms
    else:
        return terms[:qty-1]

def log_subtitle(subtitle: str, filepath: str, drop_duplicates=True):
    # TODO: add support for appending subtitles from a specific recording into a specific csv (please create new csv for each time this happens)
    # TODO: handle logic for eliminating duplicate subtitles

    with open(filepath, 'a', encoding='utf-8') as f: # this creates the file if it doesn't already exist
        pass
    
    subtitle = subtitle.replace(r'[〉」『|={_-#【“|\[\\】\]/《「〈」…<~^]','') # cleans a number of errant characters
    if len(subtitle) > 1:
        if drop_duplicates:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = str(f.read()).split('\n') ## splits string by newline into list
                data.remove('') # removes empty line that appears at end of the list
                if len(data) > 0:
                    if data[-1] == subtitle:
                        return
                
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(f'{subtitle}\n')
    return

def get_subtitles_csv(filename: str) -> list:
    # TODO: think about how to do this in a smart systematic way for the user
    filepath = os.path.join(config.get_data_directory(),'subtitles', filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        data = str(f.read()).split('\n')
        data.remove('')
    return data

def log_prompt_feedback(prompts_filepath, empty_prompt:str, feedback: int): # try/except so that passing in empty_prompt doesn't cause any funny business
    '''
    takes in prompt csv filename, empty_prompt, and feedback as {-1, 1} and increments/decrements prompt score
    '''
    try:
        prompt_df = pd.read_csv(prompts_filepath)
        prompt_df.loc[prompt_df['Prompt']==empty_prompt, 'Score'] += feedback 
        prompt_df.to_csv(prompts_filepath, index=False)
    except:
        print(f'Error adding prompt score')
    return


if __name__ == "__main__":
    #log_term('天','Number of touches', 'chi_sim')
    print(log_subtitle(' yeah。', 'MediaPlayer2911121.csv'))
