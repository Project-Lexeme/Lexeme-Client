import spacy
import re

def find_parts_of_speech_in_sentence(sentence: str, part_of_speech: list, nlp: spacy.Language, filter=True) -> list[str]:
    """parses a sentence for a target parts of speech and returns any such tokens, also checking for compound nouns in supported languages

    Args:
        sentence (str): subtitle/individual line of text 
        part_of_speech (list): list of target spacy parts of speech, e.g. 'NOUN','ADJ' 
        nlp (spacy.Language): spacy.Language object

    Returns:
        list[str]: all instances of the target part of speech in the sentence
    """
    if filter:
        filtered_sentence: str = filter_different_scripts(sentence, nlp)
    else:
        filtered_sentence = sentence
    parts_of_speech_in_sentence: list[str] = []
    doc = nlp(filtered_sentence)

    # check for compound nouns - not implemented in all spacy languages, (e.g. no support in chinese)
    try:
        for chunk in doc.noun_chunks:
            if chunk.root.pos_ in part_of_speech:
                parts_of_speech_in_sentence.append(chunk.text)
    except:
        pass
    
    print_token_attributes(doc)
    # then parse all tokens regardless of whether they were combined to form compound nouns
    for token in doc:

        if token.pos_ in part_of_speech:
            parts_of_speech_in_sentence.append(token.text)

    return parts_of_speech_in_sentence

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

def print_token_attributes(doc):
    print(doc)
    for token in doc:
        print(f"Attributes for Token: {token}")
        print(f"Tag: {token.tag_}")
        print(f"POS: {token.pos_}")
        print("-" * 50)

if __name__ == "__main__":
    print(find_parts_of_speech_in_sentence("عبارات کلیدی که به این تم اشاره دارند عبارتند از: «بی نهایت نوستالژیک»، «دوست داشتم»،", ["NOUN", "VERB"], spacy.load("../models/fa_dep_web_sm")))
