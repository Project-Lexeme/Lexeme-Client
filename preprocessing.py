import random
import cv2 as cv
import numpy as np


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

# everything in triple quotes is the earliest version of the thread of comparing two screenshot preprocessings and taking the best to be the parent of the next generation

def convert_to_grayscale(img):
    if len(img.shape) == 3:  # Check if the image is colored (3 channels)
        img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    return img
