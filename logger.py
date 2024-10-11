import pandas as pd


def log(term: str, on: str):
    '''
    on - the column name to increment. So far, 'Number of touches', 'Number correct', 'Number incorrect'
    '''

    touched_terms = pd.read_csv('learner_profile.csv') # term, no_touches
    indexer = touched_terms.loc[touched_terms['Term'] == term]

    if len(indexer) == 0: # if term is not in list of terms
        to_concat = pd.DataFrame({'Term': [term], on: [1]}) # this is going to add 1 to whichever column you passed as 'on'
        touched_terms = pd.concat([touched_terms,to_concat],ignore_index=True)
        

    elif len(indexer) == 1: # if term appears in list of terms once, as intened
        touched_terms.loc[touched_terms['Term'] == term, on] += 1

    else: # duplicate entries exist, combine them    
        summed = sum(touched_terms.loc[touched_terms['Term'] == term, on])
        touched_terms.drop_duplicates('Term', inplace=True)
        touched_terms.loc[touched_terms['Term'] == term, on] = summed
    
    touched_terms.to_csv('learner_profile.csv', index=False)

def get_terms(sort_by='weakest'):
    terms_df = pd.read_csv('learner_profile.csv')
    if sort_by == 'weakest': ## TODO: add in actual support for sorting here
        terms = terms_df['Term'].to_list()
    return terms

#log('老师', on='Number of touches)
#log('你好', on='Number incorrect')
