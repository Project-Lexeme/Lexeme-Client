import pytesseract
from PIL import Image
import matplotlib.pyplot as plt
import cv2 as cv
import numpy as np

pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe"

def read_text_from_image(filepath: str, language: str, preprocessing=False, **kwargs) -> str: 
    # returns string of the text detected in the image

    minimum_confidence = kwargs.get('minimum_confidence')
    print_confidence_levels = kwargs.get('print_confidence_levels')
    display_text_boxes = kwargs.get('display_text_boxes')

    #image = Image.open(filepath)
    if preprocess_image:
        image = preprocess_image(filepath)
    else:
        image = cv.imread(filepath)
    
    

    d = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT, lang=language)



    if print_confidence_levels:
        for i, w in enumerate(d['conf']):
            print(f"{d['text'][i]} with confidence {d['conf'][i]}")


    text = ''.join(d['text'])
    if minimum_confidence != None:
        text = filter_low_confidence(d, minimum_confidence)

    print(text) 

    if display_text_boxes == True: 
        display_text_box_image(d, filepath)

       
    return text

def filter_low_confidence(data: dict, min_confidence: int) -> list:
    # filters text below a given min_confidence (0-100, 80 being a decent threshold)
    filtered_data = []

    for i, c in enumerate(data['conf']):
        if data['conf'][i] > min_confidence:
            filtered_data.append(data['text'][i])

    filtered_text = ''.join(filtered_data)
    return filtered_text

def display_text_box_image(data: dict, filepath: str) -> None:
    # displays text boxes all neat-like
    img = cv.imread(filepath)
    n_boxes = len(data['level'])
    for i in range(n_boxes):
        (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
        cv.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cv.imshow('img', img)
    cv.waitKey(0)
    return

def preprocess_image(filepath: np.array) -> np.array:

    img = cv.imread(filepath, cv.IMREAD_GRAYSCALE)
    #
    return img



language = "chi_sim"
#preprocess_image("E:/ProjectLexeme_Server/uploads/Screenshot.png")
read_text_from_image(filepath="E:/ProjectLexeme_Server/uploads/Screenshot.png", language=language, preprocessing=True, display_text_boxes=True, minimum_confidence=80, print_confidence_levels=False)