import os
import sys
import pytesseract
import requests
import config
import tempfile
import subprocess

def set_tesseract_cmd():
    if not check_tesseract_installation():
        install_tesseract()

    if os.environ['PROCESSOR_ARCHITECTURE'] == 'AMD64':
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe" # 64-bit
    elif os.environ['PROCESSOR_ARCHITECTURE'] == 'x86':
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe" # 32-bit
    else: # TODO: handle other OS's here 
        return 'Unknown'
    
    return

def check_tesseract_installation():
    # Define the default path for Tesseract installation
    tesseract_path_64 = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    tesseract_path_32 = r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
    
    # Check if Tesseract is installed in the default paths
    if os.path.exists(tesseract_path_64) or os.path.exists(tesseract_path_32):
        print("Tesseract is already installed.")
        return True
    else:
        print("Tesseract is not installed.")
        return False

def install_tesseract():
    # Get the path to the temporary directory where the installer .exe is located
    temp_dir = tempfile.gettempdir()
    
    # Define the path to the installer .exe
    installer_path = os.path.join(temp_dir, "tesseract_installer.exe")  # Make sure this matches your installer name

    # Check if the installer exists
    if os.path.exists(installer_path):
        print(f"Launching installer from {installer_path}...")
        
        # Run the installer and wait for it to finish
        subprocess.run(installer_path, check=True)  # check=True will ensure the script waits until the installer finishes
        print("Tesseract installation completed.")
    else:
        print(f"Installer not found in {temp_dir}. Make sure the installer is present.")
        sys.exit(1)  # Exit if the installer is missing


def setup_tessdata(language):
    # Define the tessdata path
    if getattr(sys, 'frozen', False):
        tessdata_path = os.path.join(config.get_data_directory(), 'tessdata')
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


