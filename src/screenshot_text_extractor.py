import pytesseract
from PIL import Image
import cv2 as cv
import numpy as np
import sys
import time
import concurrent.futures

from src import preprocessing

previous_parent_algorithms = [None, None, None]
previous_parent_params = [[[]],[[]],[[]]]
if not getattr(sys, 'frozen', False):
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

'''
# TODO: need to modify comparative preprocessing to check for how many preprocessors are going to be used and better randomize using this info
    e.g. if there are 3 preprocessors total, one should be parent algo/parent params, one should be parent algo/random params, one should be random algo/random params
'''

def check_img_tesseract_compatibility(img): # converts img if preprocessing turned it into not-tesseract friendly dtype/color
    if img.dtype != np.uint8:
        img = np.uint8(img)
    img = cv.cvtColor(img, cv.COLOR_BGR2RGB) # type: ignore
    img = Image.fromarray(img) # Convert the NumPy array (image) to a PIL Image object
    if img.mode == 'F':
        img = img.convert('RGB')
    return img

def comparative_read_text_from_image(filepath: str, language: str, number_of_preprocessors=3, multithreading=True, display_comparison=False, **kwargs): 
    '''
    language: tesseract lang
    '''
    
    minimum_confidence = kwargs.get('minimum_confidence')
    print_confidence_levels = kwargs.get('print_confidence_levels')
    display_text_boxes = kwargs.get('display_text_boxes')
    tesseract_config = kwargs.get("config")

    global previous_parent_params
    global previous_parent_algorithms

    img = cv.imread(filepath)
    preprocessed_images = preprocessing.comparative_preprocessing(img, previous_parent_algorithms, previous_parent_params, number_of_preprocessors, display_comparison)
    
    param_conf_sums = []
    param_datas = []
    if multithreading==True:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Map the 'read_text_from_img' function to each preprocessed image in parallel
            future_to_image = {
                executor.submit(read_text_from_img, preprocessed_images[i], tesseract_config, language, print_confidence_levels): i 
                for i in range(len(preprocessed_images))
            }

            # Collect results from futures
            for future in concurrent.futures.as_completed(future_to_image):
                i = future_to_image[future]
                try:
                    param_data = future.result()
                    param_conf_sum = sum([conf for conf in param_data['conf'] if conf > 50])
                    param_conf_sums.append(param_conf_sum)
                    param_datas.append(param_data)
                except Exception as e:
                    print(f"Error processing image {i}: {e}")

    else:
        for i, _ in enumerate(preprocessed_images):
            param_data = read_text_from_img(preprocessed_images[i], tesseract_config,language,print_confidence_levels)
            param_conf_sum = sum([conf for conf in param_data['conf'] if conf > 50])
            param_conf_sums.append(param_conf_sum)
            param_datas.append(param_data)
    max_index = get_best_output_index(param_datas, minimum_confidence)

    _, previous_parent_algorithms, previous_parent_params = preprocessed_images[max_index]
    selected_data = param_datas[int(max_index)]
    
    if language not in ['chi_sim','chi_tra','kor','jpn']: # checks for languages that don't add spaces between characters
        text = ''.join([f'{t} ' for t in selected_data['text']]) # add spaces between characters
    else:
        text = ''.join(selected_data['text']) # no spaces
    
    if minimum_confidence != None:
        text = filter_low_confidence(selected_data, minimum_confidence, language)

    if display_text_boxes == True: 
        display_text_box_image(selected_data, img)

    print(f'Text: {text}')
    
    return text

def read_text_from_img(preprocessed_image, tesseract_config, ocr_lang_code, print_confidence_levels):
    """Takes in a preprocessed image and everything Tesseract needs to do OCR

    Args:
        preprocessed_image (PIL.Image): either PIL Image or np.array - doesn't have to be but is currently only used as a preprocessed image
        tesseract_config (str): r-string tesseract config e.g. r'--psm 6 --oem 1' - see tesseract documentation https://muthu.co/all-tesseract-ocr-options/
        ocr_lang_code (str): tesseract language codes, e.g. "chi_sim" or "rus"
        print_confidence_levels (bool): Whether or not to print each token's associated confidence - for debugging/performance testing

    Returns:
        dict: pytesseract.image_to_data dict output with a number of keys per token - see TSV section of https://tesseract-ocr.github.io/tessdoc/Command-Line-Usage.html
    """
    img = preprocessed_image[0]
    img = check_img_tesseract_compatibility(img)    

    if tesseract_config:
        param_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT, lang=ocr_lang_code, config=tesseract_config)
    else:
        param_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT, lang=ocr_lang_code)

    if print_confidence_levels:
        for i, w in enumerate(param_data['conf']):
            print(f"p: {param_data['text'][i]} with confidence {param_data['conf'][i]}")
    return param_data

def get_best_output_index(data_list, minimum_confidence):
    best_index = 0
    best_avg_confidence = -1

    for idx, data in enumerate(data_list):
        # Extract the confidence and text values
        conf_values = data['conf']
        
        # Count valid tokens (where confidence is not '-1')
        valid_tokens_count = sum(1 for conf in conf_values if conf > minimum_confidence)
        #print(f'index {idx} has {valid_tokens_count} valid tokens')
        
        if valid_tokens_count >= 3: # Only consider dictionaries with at least 5 valid tokens
            confidences = [int(conf) for conf in conf_values if conf != '-1']  # Only include valid confidences
            avg_confidence = sum(confidences) / len(confidences) # Calculate the average confidence for all tokens (including low-confidence ones)
            #print(f'index {idx} has avg confidence of {avg_confidence}')            
            
            if avg_confidence > best_avg_confidence: # Update best index if current output has a higher average confidence
                best_index = idx 
                best_avg_confidence = avg_confidence
    #print(best_index)
    return best_index

def filter_low_confidence(data: dict, min_confidence: int, language) -> list:
    # filters text below a given min_confidence (0-100, 80 being a decent threshold)
    # TODO: instead of returning list of filtered text, just create new data dict and return that so the join doesn't have to happen twice. 
    filtered_data = []

    for i, c in enumerate(data['conf']):
        if data['conf'][i] > min_confidence:
            filtered_data.append(data['text'][i])
    
    if language not in ['chi_sim','chi_tra','kor','jpn']: # checks for languages that don't add spaces between characters
        filtered_text = ''.join([f'{t} ' for t in filtered_data]) # add spaces between characters 
    else:
        filtered_text = ''.join(filtered_data) # no spaces
    
 
    return filtered_text

def display_text_box_image(data: dict, img: np.array) -> None:
    # displays text boxes all neat-like
    n_boxes = len(data['level'])

    for i in range(n_boxes):
        (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
        cv.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cv.imshow('img', img)
    cv.waitKey(0)
    return


if __name__ == '__main__':
    language = "chi_sim"
    tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Adjust as needed
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    config = r'--psm 6'
    #os.environ['TESSDATA_PREFIX'] = r'./tessdata'  # in case of debugging weirdness
    #os.environ['TESSDATA'] = r'./tessdata'

    start_time = time.time()
    for _ in range(10):
        comparative_read_text_from_image(filepath=f"./uploads/Screenshot.png", language=language, minimum_confidence=.7 ,number_of_preprocessors=3, display_comparison=False, config=config)
    end_time = time.time()
    print(f'Time elapsed: {end_time-start_time:.4f}')