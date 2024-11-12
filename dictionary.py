import pandas as pd
import config
import re



def standardize_wiktionary_dictionary(filepath: str) -> None:
    
    return

def standardize_u8_dictionary(filepath: str) -> None:
    '''
    trad /s sim /s [pinyin] /definition/
    B型超聲 B型超声 [B xing2 chao1 sheng1] /type-B ultrasound/
    B格 B格 [bi1 ge2] /variant of 逼格[bi1 ge2]/

    TODO: implement preference to not grab surnames instead of definition. surnames have capitalized pinyin e.g. 'Neng1' instead of 'neng1' in the dictionary
    '''
    
    entries = []
    re_string = r'(\S*) (\S*) \[(.*)\] \/(.*)\/'
    with open(filepath,'r', encoding='utf-8') as f:
        for line in f:
            if re.match(re_string, line):
                trad, sim, pinyin, definition = re.match(re_string, line).groups() # type: ignore
                print(sim)
                entries.append([trad, sim, pinyin, definition])
        
    chi_sim_save_filepath = f'{config.get_data_directory()}\\dictionaries\\chi_sim_dictionary.csv'
    chi_tra_save_filepath = f'{config.get_data_directory()}\\dictionaries\\chi_tra_dictionary.csv'
    df = pd.DataFrame(entries)
    
    df.columns = ['trad','term','pinyin','definition']
    df = df[['term','definition','pinyin', 'trad']]
    df.to_csv(chi_sim_save_filepath, index=False)
    df = df[['trad','definition','pinyin', 'term']]
    df.columns = ['term','definition','pinyin','sim']
    
    df.to_csv(chi_tra_save_filepath, index=False)
    # with open(save_filepath, 'w', newline='', encoding='utf-8') as f:
    #     wr = csv.writer(f, quoting=csv.QUOTE_ALL)
    #     wr.writerow(entries)
    return

def get_term_dictionary_contents(term: str, language: str) -> pd.DataFrame: #TODO: make sure it only returns one item
    dictionary_csv_filepath = f'{config.get_data_directory()}\\dictionaries\\{language}_dictionary.csv'
    df = pd.read_csv(dictionary_csv_filepath)
    term_contents = df[df.iloc[:,0] == term]
    return term_contents

if __name__ == "__main__":
    get_term_dictionary_contents('中文', 'chi_sim')
    #chinese_dict_filepath = f'{config.get_data_directory()}\\dictionaries\\cedict_ts.u8'
    #standardize_u8_dictionary(chinese_dict_filepath)
