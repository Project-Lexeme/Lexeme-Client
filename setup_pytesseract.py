import os
import sys
import pytesseract
import requests

# TODO: wrap all this in a new script
if getattr(sys, 'frozen', False):
    # If running as a bundled executable
    tesseract_cmd = os.path.join(sys._MEIPASS, 'tesseract')
else:
    # If running in a normal Windows Python environment
    tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Adjust as needed


def setup_tessdata(language):
    # Define the tessdata path
    if getattr(sys, 'frozen', False):
        tessdata_path = os.path.join(sys._MEIPASS, 'tessdata')
    else:
        tessdata_path = os.path.join(os.path.dirname(__file__), 'tessdata')

    # Create the tessdata directory if it doesn't exist
    os.makedirs(tessdata_path, exist_ok=True)

    # Check if the language file exists
    lang_file = os.path.join(tessdata_path, f"{language}.traineddata")
    if not os.path.isfile(lang_file):
        print(f"{language}.traineddata not found. Downloading...")
        download_language_data(language, tessdata_path)

    os.environ['TESSDATA_PREFIX'] = tessdata_path

    return tessdata_path

def download_language_data(language, tessdata_path): # TODO call this in main
    url = f"https://github.com/tesseract-ocr/tessdata/raw/main/{language}.traineddata"
    response = requests.get(url)
    
    if response.status_code == 200:
        with open(os.path.join(tessdata_path, f"{language}.traineddata"), 'wb') as f:
            f.write(response.content)
        print(f"{language}.traineddata downloaded successfully.")
    else:
        print(f"Failed to download {language}.traineddata. Status code: {response.status_code}")
        sys.exit(1)

pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
