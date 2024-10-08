import requests
from PIL import Image


## currently broken

def upload_screenshot(url):
    # Get the screenshot as bytes
    with Image.open("E:/ProjectLexeme_Server/uploads/Screenshot.png") as screenshot:
        screenshot_bytes = screenshot.tobytes()
    # Prepare the files dictionary
    files = {'image': ('Screenshot.png', screenshot_bytes, 'image/png')}
    
    # Send the POST request
    response = requests.post(url, files=files)
    
    # Print the response from the server
    print(response.json())

if __name__ == '__main__':
    upload_screenshot('http://127.0.0.1:5000/upload')