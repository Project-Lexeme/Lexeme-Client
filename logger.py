from pathlib import Path
import pandas as pd
import os
import config
import dictionary


def check_for_learner_profile():
    csv_file = Path(f'{config.get_data_directory()}/learner_profile.csv')
    if not csv_file.is_file():  # Check if the file exists
        # If it doesn't exist, create it
        csv_file.touch()
        with csv_file.open('w') as f:
            f.write('Term,Number of touches,Number correct,Number incorrect\n') 

def log_term(term: str, on: str, language: str) -> None: 
    '''
    on - the column name to increment. So far, 'Number of touches', 'Number correct', 'Number incorrect'
    '''
    check_for_learner_profile()

    touched_terms = pd.read_csv(f'{config.get_data_directory()}/learner_profile.csv') # term, no_touches
    indexer = touched_terms.loc[touched_terms['Term'] == term]
    
    

    if len(indexer) == 0: # if term is not in list of terms
        term_dictionary_contents = dictionary.get_term_dictionary_contents(term, language)
        # # need to also concat definition and other language info
        to_concat = pd.DataFrame({'Term': [term], on: [1]}) # this is going to add 1 to whichever column you passed as 'on'
        to_concat = to_concat.merge(term_dictionary_contents, left_on='Term',right_on='term').drop(columns=['term'])
        # If term_dictionary_contents is not empty, create a DataFrame from it
        if len(term_dictionary_contents) > 0:
            touched_terms = pd.concat([touched_terms,to_concat],axis=0).reset_index(drop=True)  
            
    elif len(indexer) == 1: # if term appears in list of terms once, as intended
        # does not append term dictionary contents
        touched_terms.loc[touched_terms['Term'] == term, on] += 1
            
    else: # duplicate entries exist, combine them    
        summed = sum(touched_terms.loc[touched_terms['Term'] == term, on])
        touched_terms.drop_duplicates('Term', inplace=True)
        touched_terms.loc[touched_terms['Term'] == term, on] = summed
    
    touched_terms.to_csv(f'{config.get_data_directory()}/learner_profile.csv', index=False)

def get_terms(sort_by='weakest', qty=0, all=False):
    '''
    if qty == 0, returns all terms, else returns the number requested
    '''

    terms_df = pd.read_csv(f'{config.get_data_directory()}/learner_profile.csv')
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



#log_term('天','Number of touches', 'chi_sim')
#log('老师', on='Number of touches)
#print(log_subtitle(' yeah。', 'MediaPlayer2911121.csv'))
