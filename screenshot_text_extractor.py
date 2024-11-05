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

    # # Apply adaptive thresholding to enhance text visibility
    # thresh = cv.adaptiveThreshold(
    #     blurred,
    #     255,
    #     cv.ADAPTIVE_THRESH_GAUSSIAN_C,
    #     cv.THRESH_BINARY,
    #     11,
    #     2
    # )

    
    edges = cv.Canny(blurred, threshold1=100, threshold2=200)

    return edges



# language = "chi_sim"
# tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Adjust as needed
# pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
# read_text_from_image(filepath=f"E:/ProjectLexeme/uploads/Screenshot.png", language=language, preprocessing=True, 
#                      display_text_boxes=True, minimum_confidence=60, print_confidence_levels=True, config=r'') #--oem 3 --psm 6
