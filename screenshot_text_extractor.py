import random
import pytesseract
from PIL import Image
import matplotlib.pyplot as plt
import cv2 as cv
import numpy as np
import os
import sys

previous_parent_algorithms = [None, None, None]
previous_parent_params = [[[]],[[]],[[]]]
if not getattr(sys, 'frozen', False):
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

'''
# TODO: comparative_read_text_from_image() needs to be thought about considerably
        it seems like the computational overhead for tesseract to extract text is sufficiently low that we can really expand how this thing 
        compares different preprocessed image scores
'''

def check_img_tesseract_compatibility(img): # converts img if preprocessing turned it into not-tesseract friendly dtype/color
    if img.dtype != np.uint8:
        img = np.uint8(img)
    img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    img = Image.fromarray(img) # Convert the NumPy array (image) to a PIL Image object
    if img.mode == 'F':
        img = img.convert('RGB')
    return img
def comparative_read_text_from_image(filepath: str, language: str, display_comparison=False, **kwargs): 
    minimum_confidence = kwargs.get('minimum_confidence')
    print_confidence_levels = kwargs.get('print_confidence_levels')
    display_text_boxes = kwargs.get('display_text_boxes')
    config = kwargs.get("config")

    img = cv.imread(filepath)
    global previous_parent_params
    global previous_parent_algorithms

    parent_param_img, random_param_img, random_algorithms, random_params = comparative_preprocessing(img, previous_parent_algorithms, previous_parent_params, display_comparison)
    
    # below checks for some edge cases in preprocessing where the preprocessing changes the underlying img mode and it errors pytesseract.image_to_data
    random_param_img = check_img_tesseract_compatibility(random_param_img)    
    parent_param_img = check_img_tesseract_compatibility(parent_param_img)


    if config:
        parent_param_data = pytesseract.image_to_data(parent_param_img, output_type=pytesseract.Output.DICT, lang=language, config=config)
        random_param_data = pytesseract.image_to_data(random_param_img, output_type=pytesseract.Output.DICT, lang=language, config=config)

    else:
        parent_param_data = pytesseract.image_to_data(parent_param_img, output_type=pytesseract.Output.DICT, lang=language)
        random_param_data = pytesseract.image_to_data(random_param_img, output_type=pytesseract.Output.DICT, lang=language)

    if print_confidence_levels:
        for i, w in enumerate(parent_param_data['conf']):
            print(f"p: {parent_param_data['text'][i]} with confidence {parent_param_data['conf'][i]}")
        for i, w in enumerate(random_param_data['conf']):
            print(f"r: {random_param_data['text'][i]} with confidence {random_param_data['conf'][i]}")
    parent_param_conf_sum = sum([conf for conf in parent_param_data['conf'] if conf > 50])
    random_param_conf_sum = sum([conf for conf in random_param_data['conf'] if conf > 50])
    #random_param_conf_sum = sum(random_param_data['conf'][random_param_data['conf'] > 50])
    if random_param_conf_sum > parent_param_conf_sum:
        previous_parent_algorithms = random_algorithms
        previous_parent_params = random_params
        selected_data = random_param_data
        print(f"parent param conf sum: {parent_param_conf_sum}, random param conf sum: {random_param_conf_sum}, changed previous parent params to new random params")
    else:
        selected_data = parent_param_data
        print(f"parent param conf sum: {parent_param_conf_sum}, random param conf sum: {random_param_conf_sum}, kept previous parent params")
    # print(f"r: {''.join(random_param_data['text'])}")
    # print(f"p: {''.join(parent_param_data['text'])}")

    if language not in ['chi_sim','chi_tra','kor','jpn']: # checks for languages that don't add spaces between characters
        text = ''.join([f'{t} ' for t in selected_data['text']]) # add spaces between characters
    else:
        text = ''.join(selected_data['text']) # no spaces
    
    if minimum_confidence != None:
        text = filter_low_confidence(selected_data, minimum_confidence, language)

    if display_text_boxes == True: 
        display_text_box_image(selected_data, img)

    print(text)
    return text


def read_text_from_image(filepath: str, language: str, preprocessing=False, **kwargs) -> str: 
    # returns string of the text detected in the image

    minimum_confidence = kwargs.get('minimum_confidence')
    print_confidence_levels = kwargs.get('print_confidence_levels')
    display_text_boxes = kwargs.get('display_text_boxes')
    config = kwargs.get("config")
    

    #image = Image.open(filepath)
    image = cv.imread(filepath)
        
    if preprocessing == True:
        image = preprocess_image(image)

    if config:
        d = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT, lang=language, config=config)

    else:
        d = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT, lang=language)

    if print_confidence_levels:
        for i, w in enumerate(d['conf']):
            print(f"{d['text'][i]} with confidence {d['conf'][i]}")

    if language not in ['chi_sim','chi_tra','kor','jpn']: # checks for languages that don't add spaces between characters
        text = ''.join([f'{t} ' for t in d['text']]) # add spaces between characters
    else:
        text = ''.join(d['text']) # no spaces
    
    if minimum_confidence != None:
        text = filter_low_confidence(d, minimum_confidence, language)

    if display_text_boxes == True: 
        display_text_box_image(d, image)

    print(text)
    return text

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

def preprocess_image(img: np.array) -> np.array: # TODO: work on this

    if len(img.shape) == 3:
        img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    # Apply Gaussian Blur to reduce noise
    blurred = cv.GaussianBlur(img, (3, 3), 0) #(5, 5)
    edges = cv.Canny(blurred, threshold1=100, threshold2=200)

    return edges

# everything in triple quotes is the earliest version of the thread of comparing two screenshot preprocessings and taking the best to be the parent of the next generation

def comparative_preprocessing(img, previous_algorithms, previous_params, show_comparison=False):
    parent_param_img = img # duplicate img upfront
    random_param_img = img 
    if len(random_param_img.shape) == 3:
        random_param_img = cv.cvtColor(random_param_img, cv.COLOR_BGR2GRAY)
                                    
    noise_removal_dict = {None : [[]],
                        cv.GaussianBlur : [[random_param_img], 
                                            [(3,3), (5,5), (7,7), (9,9), (11,11)],
                                            [0]], 
                        cv.medianBlur: [[random_param_img], 
                                        [3,5,7,9]],} 
    thresholding_dict = {None : [[]],
                        cv.threshold: [[random_param_img], # returns tuple (___, thresh)
                                        [100,120,140], 
                                        [255], 
                                        [cv.THRESH_BINARY, cv.THRESH_BINARY_INV, cv.THRESH_TRUNC, cv.THRESH_TOZERO, # thresh function
                                        cv.THRESH_TOZERO_INV, cv.THRESH_BINARY + cv.THRESH_OTSU]],}
    edge_detection_dict = {None : [[]],
                            cv.Canny: [[random_param_img],
                                    [50,100,130], # low thresh
                                    [150,180,210]], # high thresh
                            cv.Sobel: [[random_param_img],
                                    [cv.CV_64F], 
                                    [1, 2], # dx
                                    [0, 1, 2], # dy
                                    [3, 5]]} # ksize
    
    # define img up here to implicitly pass it in to these functions
    random_param_img, noise_algorithm, noise_params = get_random_preprocessing(random_param_img, noise_removal_dict)
    thresh_results = get_random_preprocessing(random_param_img, thresholding_dict)
    try: (_, random_param_img), thresh_algorithm, thresh_params = thresh_results # done via try/except because thresh algo returning 'None' gives error when assigned to (_, random_param_img)
    except: random_param_img, thresh_algorithm, thresh_params = thresh_results
    random_param_img, edge_algorithm, edge_params = get_random_preprocessing(random_param_img, edge_detection_dict)
    
    random_algorithms = [noise_algorithm,thresh_algorithm, edge_algorithm]

    random_params = [noise_params, thresh_params, edge_params] # this is returned
    # compare with previous choices
    
    if len(parent_param_img.shape) == 3:
            parent_param_img = cv.cvtColor(parent_param_img, cv.COLOR_BGR2GRAY)

    # set each 'img' arg in each set of params as new parent_param_img
    previous_params[0][0] = parent_param_img
    previous_params[1][0] = parent_param_img
    previous_params[2][0] = parent_param_img
    
    if previous_algorithms[0] is not None:
        parent_param_img = previous_algorithms[0](*previous_params[0])
    if previous_algorithms[1] is not None:
        _, parent_param_img = previous_algorithms[1](*previous_params[1])
    if previous_algorithms[2] is not None:
        parent_param_img = previous_algorithms[2](*previous_params[2])


    if show_comparison == True:
        concatenated_image = np.hstack((random_param_img, parent_param_img))
        # Show the concatenated image in one window
        cv.imshow('Comparison', concatenated_image)
        cv.waitKey(0)
        cv.destroyAllWindows()

    return parent_param_img, random_param_img, random_algorithms, random_params


def get_random_preprocessing(img, preprocessing_dict):
    preprocessing_list = list(preprocessing_dict.keys())
    preprocessing_algorithm_index = random.randrange(0, len(preprocessing_list)) # need to store index separately for genetic purposes
    preprocessing_algorithm = preprocessing_list[preprocessing_algorithm_index] # algorithm is stored as a 
    if preprocessing_algorithm == None:
        return (img, None, [[]])
    param_options = preprocessing_dict[preprocessing_algorithm] # params associates with given index, so
    params = get_rand_params(param_options)
    return (preprocessing_algorithm(*params), preprocessing_algorithm, params)
    
def get_rand_params(param_options: list):
    params = []
    for param_type in param_options:
        if len(param_type) > 1:
            param_index = random.randrange(0, len(param_type))
            params.append(param_type[param_index]) # introduce randomness
        else:
            params.append(param_type[0])
    return params    



#language = "chi_sim"
# tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Adjust as needed
# pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
#comparative_read_text_from_image(filepath=f"E:/ProjectLexeme/uploads/Screenshot.png", language=language, display_comparison=True)