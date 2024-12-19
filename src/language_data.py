from src.startup import get_language_and_proficiency, install_and_load_nlp_lang_from_spacy, load_nlp_lang_from_bootstrapped_models
from src.setup_pytesseract import set_tesseract_cmd, setup_tessdata
from src.logger import check_for_learner_profile

class LanguageData:
    def __init__(self) -> None:
        (self.language, [self.ocr_lang_code, self.nlp_lang_code, self.proficiency]) = get_language_and_proficiency()
        self.is_language_bootstrapped = self.check_language_source()
        check_for_learner_profile(self.ocr_lang_code)
        self.nlp_model = self.load_nlp_lang()
        print("SpaCy installed, imported, and loaded")
        print("Setting up PyTesseract now... Checking for installation")
        set_tesseract_cmd()
        setup_tessdata(self.ocr_lang_code)
        print("PyTesseract set up!")

    def check_language_source(self) -> bool:
        if self.language in ['Arabic','Indonesian','Tagalog','Persian - Farsi', 'Persian - Dari']:
            return True
        else:
            return False
        
    def load_nlp_lang(self):
        if self.is_language_bootstrapped:
            return load_nlp_lang_from_bootstrapped_models(self.nlp_lang_code)
        else:
            return install_and_load_nlp_lang_from_spacy(self.nlp_lang_code)
        
