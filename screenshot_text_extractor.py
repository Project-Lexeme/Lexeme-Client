import pytesseract
from PIL import Image
import matplotlib.pyplot as plt
import cv2 as cv
import numpy as np

pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe" # 

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

    text = ''.join(d['text'])

    
    if minimum_confidence != None:
        text = filter_low_confidence(d, minimum_confidence)

    if display_text_boxes == True: 
        display_text_box_image(d, image)

    print(text)
    return text

def filter_low_confidence(data: dict, min_confidence: int) -> list:
    # filters text below a given min_confidence (0-100, 80 being a decent threshold)
    filtered_data = []

    for i, c in enumerate(data['conf']):
        if data['conf'][i] > min_confidence:
            filtered_data.append(data['text'][i])

    filtered_text = ''.join(filtered_data)
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

def preprocess_image(img: np.array) -> np.array:

    height, width = img.shape[:2]

    # Calculate the coordinates for the bottom fourth
    start_row = height // 2   # Start from 1/2 of the height
    end_row = height               # End at the bottom of the image
    start_col = 0                 # Start from the leftmost column
    end_col = width                # End at the rightmost column

    # Crop the image
    cropped_image = img[start_row:end_row, start_col:end_col]
    cropped_image = cv.cvtColor(cropped_image, cv.COLOR_BGR2GRAY)
    return cropped_image
    #cropped_image = cv.cvtColor(cropped_image, cv.IMREAD_GRAYSCALE)

    # _, thresh = cv.threshold(cropped_image, 100, 255, cv.THRESH_BINARY)


    # ### inverts color
    # preprocessed_image =thresh#cv.convertScaleAbs(thresh)
    
    #cv.convertScaleAbs(laplacian)
    
    #return preprocessed_image



#language = "chi_sim"

#read_text_from_image(filepath=f"E:/ProjectLexeme_Server/uploads/Screenshot.png", language=language, preprocessing=True, display_text_boxes=False, minimum_confidence=60, print_confidence_levels=False)
