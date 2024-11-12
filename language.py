class LanguageData:
    def __init__(self, language, nlp_lang, spacy_lang, proficiency) -> None:
        self.language = language
        self.nlp_lang = nlp_lang
        self.spacy_lang = spacy_lang
        self.proficiency = proficiency

    # TODO: Add startup stuff that relates to LanguageData here