import os
import pandas as pd

from src import config

def get_term_dictionary_contents(terms: str, language: str) -> pd.DataFrame: #TODO: make sure it only returns one (correct) item
    dictionary_csv_filepath = os.path.join(config.get_data_directory(), "dictionaries", f"{language}_dictionary.csv") #f'{config.get_data_directory()}\\dictionaries\\{language}_dictionary.csv'
    df = pd.read_csv(dictionary_csv_filepath)
    term_contents = df[df.iloc[:,0].isin(terms)]
    return term_contents

if __name__ == "__main__":
    filepath = f'{config.get_data_directory()}/dictionaries/indonesian_dictionary.txt'
    