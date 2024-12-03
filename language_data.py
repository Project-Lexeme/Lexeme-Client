from startup import get_language_and_proficiency, install_and_load_nlp_lang
from setup_pytesseract import set_tesseract_cmd, setup_tessdata
from logger import check_for_learner_profile

class LanguageData:
    def __init__(self) -> None:
        (self.language, [self.ocr_lang_code, self.nlp_lang_code, self.proficiency]) = get_language_and_proficiency()
        check_for_learner_profile(self.ocr_lang_code)
        self.nlp_model = install_and_load_nlp_lang(self.nlp_lang_code)
        print("SpaCy installed, imported, and loaded")
        print("Setting up PyTesseract now... Checking for installation")
        set_tesseract_cmd()
        setup_tessdata(self.ocr_lang_code)
        print("PyTesseract set up!")
