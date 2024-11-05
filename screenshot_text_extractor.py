import random
import pytesseract
from PIL import Image
import matplotlib.pyplot as plt
import cv2 as cv
import numpy as np
import os
import sys

# need to wrap this into a class to store global params, such whether the language requires spaces between characters 

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

''' 
img = cv.imread(r'E:/ProjectLexeme/uploads/Screenshot.png')
if len(img.shape) == 3:
        img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

noise_removal_dict = {None : [[]],
                      cv.GaussianBlur : [[img], 
                                         [(3,3), (5,5), (7,7), (9,9), (11,11)],
                                         [0]], 
                      cv.medianBlur: [[img], 
                                      [3,5,7,9]],} 
thresholding_dict = {None : [[]],
                     cv.threshold: [[img], # returns tuple (___, thresh)
                                    [100,120,140], 
                                    [255], 
                                    [cv.THRESH_BINARY, cv.THRESH_BINARY_INV, cv.THRESH_TRUNC, cv.THRESH_TOZERO, # thresh function
                                     cv.THRESH_TOZERO_INV, cv.THRESH_BINARY + cv.THRESH_OTSU]],}
edge_detection_dict = {None : [[]],
                        cv.Canny: [[img],
                                  [50,100,130], # low thresh
                                  [150,180,210]], # high thresh
                        cv.Sobel: [[img],
                                   [cv.CV_64F], 
                                   [1, 2], # dx
                                   [0, 1, 2], # dy
                                   [3, 5]] # ksize
                                   } 

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


# define img up here to implicitly pass it in to these functions
img, noise_algorithm, noise_params = get_random_preprocessing(img, noise_removal_dict)
thresh_results = get_random_preprocessing(img, thresholding_dict)
try: (_, img), thresh_algorithm, thresh_params = thresh_results
except: img, thresh_algorithm, thresh_params = thresh_results
img, edge_algorithm, edge_params = get_random_preprocessing(img, edge_detection_dict)
print(edge_params)

# compare with previous choices
img2 = cv.imread(r'E:/ProjectLexeme/uploads/Screenshot.png')
if len(img2.shape) == 3:
        img2 = cv.cvtColor(img2, cv.COLOR_BGR2GRAY)

### set each 'img' arg in each set of params as new img2
noise_params[0] = img2
thresh_params[0] = img2
edge_params[0] = img2
###
if noise_algorithm is not None:
    img2 = noise_algorithm(*noise_params)
if thresh_algorithm is not None:
    _, img2 = thresh_algorithm(*thresh_params)
if edge_algorithm is not None:
    img2 = edge_algorithm(*edge_params)
# cv.imshow("rand", img)

img, noise_algorithm, noise_params = get_random_preprocessing(img, noise_removal_dict)
thresh_results = get_random_preprocessing(img, thresholding_dict)
try: (_, img), thresh_algorithm, thresh_params = thresh_results
except: img, thresh_algorithm, thresh_params = thresh_results
img, edge_algorithm, edge_params = get_random_preprocessing(img, edge_detection_dict)

concatenated_image = np.hstack((img, img2))

# Show the concatenated image in one window
cv.imshow('Comparison', concatenated_image)

cv.waitKey(0)
cv.destroyAllWindows()
'''
# language = "chi_sim"
# tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Adjust as needed
# pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
# read_text_from_image(filepath=f"E:/ProjectLexeme/uploads/Screenshot.png", language=language, preprocessing=True, 
#                      display_text_boxes=True, minimum_confidence=60, print_confidence_levels=True, config=r'') #--oem 3 --psm 6
