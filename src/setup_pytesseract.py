import os
import sys
import pytesseract
import requests
from src import config
import subprocess
import platform

def set_tesseract_cmd():
    if not check_tesseract_installation():
        run_installer()

    if platform.system() == 'Windows':
        if os.environ['PROCESSOR_ARCHITECTURE'] == 'AMD64':
            pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe" # 64-bit
        elif os.environ['PROCESSOR_ARCHITECTURE'] == 'x86':
            pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe" # 32-bit
    elif platform.system() == 'Linux':  
        pytesseract.pytesseract.tesseract_cmd = r"/bin/tesseract"
    
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

def find_installer():
    # Check if the program is bundled (PyInstaller one-file executable)
    if hasattr(sys, '_MEIPASS'):
        # _MEIPASS is where PyInstaller unpacks files in a one-file executable
        temp_dir = sys._MEIPASS
        installer_folder = os.path.join(temp_dir, 'tesseract_installer')  # The folder where the installer is placed

        # Check if the folder exists
        if os.path.exists(installer_folder) and os.path.isdir(installer_folder):
            # Get all files in the installer folder
            installer_files = [f for f in os.listdir(installer_folder) if f.endswith('.exe')]
            if installer_files:
                # Take the first .exe file found (there should only be one)
                installer_path = os.path.join(installer_folder, installer_files[0])
                return installer_path
            else:
                print(f"No .exe file found in {installer_folder}.")
        else:
            print(f"The folder {installer_folder} does not exist in the temp directory.")
    else:
        print("This is not a bundled executable. Cannot find installer.")
    
    return None
def run_installer():
    installer_path = find_installer()
    if installer_path:
        print(f"Found installer at: {installer_path}")
        try:
            # Run the installer
            subprocess.run([installer_path], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to run the installer: {e}")
        except Exception as e:
            print(f"Error running the installer: {e}")
    else:
        print("Installer not found or could not be run.")


def setup_tessdata(ocr_lang_code: str):
    """Checks for ocr_lang_code.traineddata in ./tessdata, installs if not found. 
    Sets os.environ variable to this file's location

    Args:
        ocr_lang_code (str): language code used by OCR (currently Tesseract) e.g. "chi_sim" or "rus"

    Returns:
        str: absolute path to traineddata
    """
    print("Checking for language data for your language...")
    
    if getattr(sys, 'frozen', False):
        tessdata_path = os.path.join(config.get_data_directory(), 'tessdata')
    else:
        current_file_path = os.path.dirname(__file__)
        parent_dir = os.path.dirname(current_file_path)
        tessdata_path = os.path.join(parent_dir, 'tessdata')

    # Create the tessdata directory if it doesn't exist
    os.makedirs(tessdata_path, exist_ok=True)

    # Check if the language file exists
    lang_file = os.path.join(tessdata_path, f"{ocr_lang_code}.traineddata")
    if not os.path.isfile(lang_file):
        print(f"{ocr_lang_code}.traineddata not found. Downloading...")
        download_language_data(ocr_lang_code, tessdata_path)

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


