import random
import pytesseract
from PIL import Image
import cv2 as cv
import numpy as np
import sys
import os 

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

def comparative_read_text_from_image(filepath: str, language: str, number_of_preprocessors=3, display_comparison=False, **kwargs): 
    minimum_confidence = kwargs.get('minimum_confidence')
    print_confidence_levels = kwargs.get('print_confidence_levels')
    display_text_boxes = kwargs.get('display_text_boxes')
    tesseract_config = kwargs.get("config")

    global previous_parent_params
    global previous_parent_algorithms

    img = cv.imread(filepath)
    preprocessed_images = comparative_preprocessing(img, previous_parent_algorithms, previous_parent_params, number_of_preprocessors, display_comparison)
    
    # below checks for some edge cases in preprocessing where the preprocessing changes the underlying img mode and it errors pytesseract.image_to_data
    param_conf_sums = []
    param_datas = []
    for i, _ in enumerate(preprocessed_images):
        img = preprocessed_images[i][0]
        img = check_img_tesseract_compatibility(img)    
    
        if tesseract_config:
            param_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT, lang=language, config=tesseract_config)
        else:
            param_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT, lang=language)

        if print_confidence_levels:
            for i, w in enumerate(param_data['conf']):
                print(f"p: {param_data['text'][i]} with confidence {param_data['conf'][i]}")

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

    print(text)
    return text

def get_best_output_index(data_list, minimum_confidence):
    best_index = 0
    best_avg_confidence = -1

    for idx, data in enumerate(data_list):
        # Extract the confidence and text values
        conf_values = data['conf']
        
        # Count valid tokens (where confidence is not '-1')
        valid_tokens_count = sum(1 for conf in conf_values if conf > minimum_confidence)
        #print(f'index {idx} has {valid_tokens_count} valid tokens')
        # Only consider dictionaries with at least 5 valid tokens
        if valid_tokens_count >= 3:
            # Calculate the average confidence for all tokens (including low-confidence ones)
            confidences = [int(conf) for conf in conf_values if conf != '-1']  # Only include valid confidences
            avg_confidence = sum(confidences) / len(confidences)
            #print(f'index {idx} has avg confidence of {avg_confidence}')
            
            # Update best index if current output has a higher average confidence
            if avg_confidence > best_avg_confidence:
                best_index = idx
                best_avg_confidence = avg_confidence
    #print(best_index)
    return best_index


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

def convert_to_grayscale(img):
    if len(img.shape) == 3:  # Check if the image is colored (3 channels)
        img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    return img

def comparative_preprocessing(img, previous_algorithms, previous_params, number_of_preprocessors, show_comparison=False):
    img = convert_to_grayscale(img)
    
    # set each 'img' arg in each set of params as new img
    preprocessors = []
    previous_params[0][0] = img
    previous_params[1][0] = img
    previous_params[2][0] = img

    img = apply_algorithms(img, previous_algorithms,previous_params)
    parent_preprocessor_tuple = (img, previous_algorithms, previous_params)
    preprocessors.insert(0,parent_preprocessor_tuple) # first index is parent set
    
    if number_of_preprocessors < 2:
        return preprocessors
    elif number_of_preprocessors == 2:
        preprocessors.append(assign_random_preprocessing(img))
        return preprocessors 
    else:
        # case for parent algorithms, random params
        preprocessors.append(assign_random_preprocessing(img, previous_algorithms))
        # case for random algorithms, random params
        for _ in range(number_of_preprocessors - 2): # n - 2 because the first preprocessor is parent, second is parent algo / random params
            random_preprocessor_tuple = assign_random_preprocessing(img)
            preprocessors.append(random_preprocessor_tuple)
    
    if show_comparison == True:
        show_preprocessing_comparison(preprocessors)

    return preprocessors # list of tuples (img, algo, params)

def assign_random_preprocessing(img, previous_algorithms=None):
    random_param_img = convert_to_grayscale(img)                                     
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
    if previous_algorithms is not None:
        random_algorithms = previous_algorithms
        noise_params = get_rand_params(noise_removal_dict[random_algorithms[0]])
        thresh_params = get_rand_params(thresholding_dict[random_algorithms[1]])
        edge_params = get_rand_params(edge_detection_dict[random_algorithms[2]])
    else:
        # define img up here to implicitly pass it in to these functions
        random_param_img, noise_algorithm, noise_params = get_random_preprocessing(random_param_img, noise_removal_dict)
        thresh_results = get_random_preprocessing(random_param_img, thresholding_dict)
        try: (_, random_param_img), thresh_algorithm, thresh_params = thresh_results # done via try/except because thresh algo returning 'None' gives error when assigned to (_, random_param_img)
        except: random_param_img, thresh_algorithm, thresh_params = thresh_results
        random_param_img, edge_algorithm, edge_params = get_random_preprocessing(random_param_img, edge_detection_dict)

        random_algorithms = [noise_algorithm,thresh_algorithm, edge_algorithm]
    random_params = [noise_params, thresh_params, edge_params] # this is returned
    random_preprocessor_tuple = (random_param_img, random_algorithms, random_params)
    return random_preprocessor_tuple

# def show_preprocessing_comparison(preprocessors) -> None:
#     imgs = [p[0] for p in preprocessors]
#     concatenated_image = np.vstack(imgs)
#     # Show the concatenated image in one window
#     cv.imshow('Comparison', concatenated_image)
#     cv.waitKey(0)
#     cv.destroyAllWindows()

def show_preprocessing_comparison(preprocessors) -> None:
    # Create an empty list to hold the labeled images
    labeled_images = []
    
    # Loop through each preprocessed image and its corresponding algorithms and parameters
    for img, algorithms, params in preprocessors:
        labeled_img = img.copy()  # Copy the image to modify it
        
        # Construct a label for the preprocessing algorithms and parameters
        label = ""
        for algo in algorithms:
            algo_name = algo.__name__ if algo else "None"
            label += f"{algo_name}\n"  # Add each algorithm and its params to the label
        
        # Add the label to the image (you may adjust the position and font as needed)
        font = cv.FONT_HERSHEY_SIMPLEX
        color = (255, 255, 255)  # White text
        thickness = 1
        position = (10, 30)  # Starting position for text (top-left corner)
        cv.putText(labeled_img, label, position, font, 0.5, color, thickness, lineType=cv.LINE_AA)
        
        # Append the labeled image to the list
        labeled_images.append(labeled_img)
    
    # Concatenate all the labeled images vertically
    concatenated_image = np.vstack(labeled_images)
    
    # Show the concatenated image in one window
    cv.imshow('Comparison', concatenated_image)
    cv.waitKey(0)
    cv.destroyAllWindows()

def apply_algorithms(img, algorithms, params):
    for algorithm, param_set in zip(algorithms, params):
        if algorithm is not None:
            img = algorithm(*param_set)
    return img

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
        elif len(param_type) == 1:
            params.append(param_type[0])
        else:
            params.append([])
    return params    


if __name__ == '__main__':
    language = "chi_sim"
    tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Adjust as needed
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        # Set TESSDATA_PREFIX to the parent directory of your tessdata folder
    os.environ['TESSDATA_PREFIX'] = r'./tessdata'  # Update this with the correct path

    # You may also want to explicitly specify the path to the tessdata folder, in case it isn't auto-detected
    os.environ['TESSDATA'] = r'./tessdata'
    comparative_read_text_from_image(filepath=f"./uploads/Screenshot.png", language=language, minimum_confidence=.7 ,number_of_preprocessors=3, display_comparison=True)