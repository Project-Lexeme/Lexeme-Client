import pytesseract
from PIL import Image
import matplotlib.pyplot as plt
import cv2

pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe"

def read_text_from_image(filepath: str, language: str): #open ocr is only for chinese and english

    image = Image.open(filepath)
    text = pytesseract.image_to_string(image, lang=language)  # Use 'chi_sim' for Simplified Chinese

    print(text)

    img = cv2.imread("E:/SpaCy Playground/uploads/Screenshot.png")

    d = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    n_boxes = len(d['level'])
    for i in range(n_boxes):
        (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cv2.imshow('img', img)
    cv2.waitKey(0)

language = "chi_sim"
read_text_from_image(filepath="E:/SpaCy Playground/uploads/Screenshot.png", language=language)