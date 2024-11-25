from startup import get_language_and_proficiency, install_and_load_nlp_lang
from setup_pytesseract import set_tesseract_cmd, setup_tessdata

class LanguageData:
    def __init__(self) -> None:
        (self.language, [self.ocr_lang_code, self.nlp_lang_code, self.proficiency]) = get_language_and_proficiency()
        self.nlp_model = install_and_load_nlp_lang(self.nlp_lang_code)
        print("SpaCy installed, imported, and loaded")
        print("Setting up PyTesseract now... Checking for installation")
        set_tesseract_cmd()
        setup_tessdata(self.ocr_lang_code)
        print("PyTesseract set up!")

    # TODO: Add startup stuff that relates to LanguageData here

    # set_nlp(startup.install_and_load_nlp_lang(nlp_lang))
    # setup_pytesseract.setup_tessdata(lang_code)
    # _nlp = None
# _cfg = None
# _language = None # TODO: use Language class to make the handling of language info cleaner

## Set up the screen recorder
    # language, codes_and_proficiency =  startup.get_language_and_proficiency()
    # lang_code, nlp_lang, proficiency = codes_and_proficiency
    # set_recorder(ScreenRecorder(language=lang_code, nlp=_nlp, preprocessors=3, use_comparative_preprocessing=True, minimum_confidence=70, config=r'--psm 6', time_between_screencaps=.6))
    # print("ScreenRecorder is set up")
    # set_nlp(startup.install_and_load_nlp_lang(nlp_lang))
    # setup_pytesseract.setup_tessdata(lang_code)
