var sliderInstance;

function getLessonFromSubtitles() {
    fetch('/get-subtitle-files')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Populate subtitle dropdown
            const subtitleDropdown = document.getElementById('subtitle-dropdown');
            subtitleDropdown.innerHTML = ''; // Clear previous options
            data.choices.forEach(choice => {
                const option = document.createElement('option');
                option.value = choice;
                option.textContent = choice;
                subtitleDropdown.appendChild(option);
            });

            // Populate prompt type dropdown
            const promptTypeDropdown = document.getElementById('prompt-type-dropdown');
            promptTypeDropdown.innerHTML = ''; // Clear previous options
            data.prompt_types.forEach(type => {
                const option = document.createElement('option');
                option.value = type;
                option.textContent = type;
                promptTypeDropdown.appendChild(option);
            });

            // Hide lesson prompt options and show subtitle selection
            document.getElementById('lesson-prompt-options').style.display = 'none';
            document.getElementById('subtitle-selection').style.display = 'grid';
        })
        .catch(error => {
            console.error('Error fetching subtitle files:', error);
            document.getElementById('response').textContent = 'Error fetching subtitle files.';
        });
}

function viewGeneratedSubtitles() {
    fetch('/open-subtitles-folder', {
        method: 'POST'
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to open subtitles folder');
            } else {
                document.getElementById('response').textContent = 'Viewing Generated Subtitles';
            }
        })
        .catch(error => console.error('Error:', error));
}

function viewPromptsForLLM() {
    fetch('/open-prompt-directory', {
        method: 'POST'
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to open prompt directory');
            } else {
                document.getElementById('response').textContent = 'Opening Prompt Directory';
            }
        })
        .catch(error => console.error('Error:', error));
}

function generate() {
    const subtitleDropdown = document.getElementById('subtitle-dropdown');
    const promptTypeDropdown = document.getElementById('prompt-type-dropdown');

    const selectedSubtitle = subtitleDropdown.value;
    const selectedPromptType = promptTypeDropdown.value;

    fetch('/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            subtitle: selectedSubtitle,
            prompt_type: selectedPromptType
        })
    })
        .then(response => response.json())
        .then(data => {
            document.getElementById('response').textContent = 'Lesson generated successfully!';
            window.location.href = `/lesson?subtitle=${encodeURIComponent(selectedSubtitle)}&prompt_type=${encodeURIComponent(selectedPromptType)}`;
            // Additional handling of lesson data can be added here
        })
        .catch(error => {
            console.error('Error generating lesson:', error);
            document.getElementById('response').textContent = 'Error generating lesson.';
        });
}

function showSettingsOptions() {
    document.querySelector('.container').style.display = 'none';
    const settingsOptions = document.getElementById('change-settings-options');
    settingsOptions.style.display = 'grid';
}

function modifyConfigurationOptions() {
    document.getElementById('change-settings-options').style.display = 'none';
    showAppConfiguration();
    const configurationOptions = document.getElementById('modify-configuration-options');
    configurationOptions.style.display = 'grid';
}

function showRecordOptions() {
    document.querySelector('.container').style.display = 'none';
    const recordOptions = document.getElementById('record-content-options');
    recordOptions.style.display = 'grid';
}

function showLessonOptions() {
    document.querySelector('.container').style.display = 'none';
    const lessonOptions = document.getElementById('lesson-prompt-options');
    lessonOptions.style.display = 'grid';
}
function showUploadOptions() {
    document.querySelector('.container').style.display = 'none';
    const settingsOptions = document.getElementById('upload-content-options');
    settingsOptions.style.display = 'grid';
}

function goBack() {
    document.getElementById('lesson-prompt-options').style.display = 'none';
    document.getElementById('record-content-options').style.display = 'none';
    document.getElementById('change-settings-options').style.display = 'none';
    document.getElementById('upload-content-options').style.display = 'none';
    document.getElementById('modify-configuration-options').style.display = 'none';
    document.getElementById('response').textContent = " ";
    document.querySelector('.container').style.display = 'grid';
}

function goBackToLessonOptions() {
    document.getElementById('subtitle-selection').style.display = 'none';
    document.getElementById('lesson-prompt-options').style.display = 'grid';
    document.getElementById('response').textContent = " ";
}

function goBackToChangeSettingsOptions() {
    revertConfigurationValuesToReadOnly();
    const h2element = document.getElementById('configuration-back-button').querySelector('h2');
    if (h2element) {
        h2element.textContent = "GO BACK"
    }
    const changeConfigurationValuesButton = document.getElementById('change-settings-button');
    changeConfigurationValuesButton.style.display = 'block';
    document.getElementById('modify-configuration-options').style.display = 'none';
    hideAppConfiguration();
    document.getElementById('submit-settings-button').style.display = 'none';
    document.getElementById('change-settings-options').style.display = 'grid';
    document.getElementById('response').textContent = " ";
    
}

function showAppConfiguration() {
    const appConfig = document.getElementById('app-configuration');
    appConfig.style.display = 'block';  // Show the App Configuration section
}

function hideAppConfiguration() {
    const appConfig = document.getElementById('app-configuration');
    appConfig.style.display = 'none';  // Hide the App Configuration section
}

function changeConfigurationValues(){
    const submitSettingsButton = document.getElementById('submit-settings-button');
    submitSettingsButton.style.display = 'block'; 
    const configurationBackButton = document.getElementById('configuration-back-button');
    const h2element = configurationBackButton.querySelector('h2');
    if (h2element) {
        h2element.textContent = "UNDO CHANGES"
    }
    const changeConfigurationValuesButton = document.getElementById('change-settings-button');
    changeConfigurationValuesButton.style.display = 'none';
    convertConfigurationValuesToEditable();
}

function convertConfigurationValuesToEditable() {
    const configItems = document.querySelectorAll('#app-configuration ul li');
    
    configItems.forEach(item => {
        const strong = item.querySelector('strong');
        const valueSpan = item.querySelector('span');
        const fieldName = strong.textContent.trim().replace(':', '');
        
        // Change "Base URL" to a free text input field
        if (fieldName === "Base URL" || fieldName === "API Key") {
            const inputField = document.createElement('input');
            inputField.type = 'text';
            inputField.value = valueSpan.textContent.trim();  // Retain the current value
            valueSpan.textContent = '';  // Clear the span
            item.appendChild(inputField);
        } else {
            // Change other fields to dropdowns (select elements)
            const selectField = document.createElement('select');
            const options = ['Option 1', 'Option 2', 'Option 3']; // Example options
            options.forEach(optionText => {
                const option = document.createElement('option');
                option.textContent = optionText;
                selectField.appendChild(option);
            });
            
            valueSpan.textContent = ''; // Clear the span
            selectField.value = valueSpan.textContent.trim();  // Set the current value
            item.appendChild(selectField);
        }
    });
}

function revertConfigurationValuesToReadOnly() {
    const configItems = document.querySelectorAll('#app-configuration ul li');
    
    configItems.forEach(item => {
        const strong = item.querySelector('strong');
        const inputField = item.querySelector('input');
        const selectField = item.querySelector('select');
        
        // If there is an input field (Base URL)
        if (inputField) {
            const value = inputField.value;
            const valueSpan = document.createElement('span');
            valueSpan.textContent = value;
            item.appendChild(valueSpan);
            inputField.remove();  // Remove the input field
        } 
        // If there is a select field (other fields like Model, Language)
        else if (selectField) {
            const selectedOption = selectField.options[selectField.selectedIndex];
            if (selectedOption) {
                const value = selectedOption.text;
                const valueSpan = document.createElement('span');
                valueSpan.textContent = value;
                item.appendChild(valueSpan);
                selectField.remove();  // Remove the select field
            }
        }
    });
}


function submitSettings(){
    const submitSettingsButton = document.getElementById('submit-settings-button');
    submitSettingsButton.style.display = 'none';
    const configurationBackButton = document.getElementById('configuration-back-button');
    configurationBackButton.style.display = 'block';
    const h2element = configurationBackButton.querySelector('h2');
    if (h2element) {
        h2element.textContent = "GO BACK"
    }
    document.getElementById('response').textContent = 'Changes Submitted!';
    revertConfigurationValuesToReadOnly();
    const changeConfigurationValuesButton = document.getElementById('change-settings-button');
    changeConfigurationValuesButton.style.display = 'block';
}

function getLessonFromVocabulary() {
    window.location.href = '/get-learner-profile';
}

function updateFileLabel() {
    var fileInput = document.getElementById('fileInput');
    var fileLabel = document.getElementById('fileLabel');
    
    // Check if a file has been selected
    if (fileInput.files.length > 0) {
        var fileName = fileInput.files[0].name; // Get the file name
        fileLabel.textContent = fileName; // Update the label text
    } else {
        fileLabel.textContent = 'Choose File'; // Default label text if no file selected
    }
}

function selectSubtitleUpload() {
    // Get the file input element
    var fileInput = document.getElementById('fileInput');
    var file = fileInput.files[0];

     // Get the responseMessage div to display errors or success messages
    var responseMessageDiv = document.getElementById('response');

    // If no file is selected, update the response div with an error message
    if (!file) {
        responseMessageDiv.textContent = "Please attach a file.";
        responseMessageDiv.style.color = "red"; // Set error message color
        return;
    }

    

    // Create FormData to send the file to the Flask server
    var formData = new FormData();
    formData.append("file", file);

    // Use fetch to send the file to Flask
    fetch('/upload-subtitles', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('File upload failed');
        }
        return response.json(); // Parse JSON response
    })
    .then(data => {

        console.log(data);
        // Handle the response (e.g., update the slider if needed)
        if (data.slider_values && data.slider_values.min !== undefined && data.slider_values.max !== undefined) {
            // Show the slider container
            document.getElementById('sliderContainer').style.display = 'block';

            // Initialize the slider with min and max from the response
            sliderInstance = $('#slider').ionRangeSlider({
                type: 'double', // This makes it a range slider (two handles)
                min: data.slider_values.min,
                max: data.slider_values.max,
                from: data.slider_values.min,  // Set the initial start of the range
                to: data.slider_values.max,    // Set the initial end of the range
                step: 1,
                postfix: ' minutes',
                grid: true

        });
        
        document.getElementById('submitButton').style.display = 'block';
        
        } else {
            // Log a warning if slider_values is not as expected
            console.error('Invalid slider values in response:', data);
            alert('Error: Invalid slider values');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('There was an error uploading the file.');
    });
}

function submitSubtitleUpload() {
    if (!sliderInstance) {
        console.error('Slider instance is not initialized.');
        var fromValue = 0;
        var toValue = 0;
    }
    else {
        var sliderValues = sliderInstance.data('ionRangeSlider').result;
        var fromValue = sliderValues.from;
        var toValue = sliderValues.to;
    }
    
    // Get the file input and create a FormData object
    var fileInput = document.getElementById('fileInput');
    var file = fileInput.files[0];
    var formData = new FormData();

    // Append file and slider values to FormData
    if (file) {
        formData.append("subtitle_file", file);
    }
    formData.append("slider_from", fromValue);
    formData.append("slider_to", toValue);
        
    fetch('/submit-subtitle-upload', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('File upload failed');
        }
        return response.json(); // Parse JSON response
    })
    .then(data => {
        document.getElementById('response').textContent = data.message;   
    })
    .catch(error => {
        console.error('Error:', error);
        alert('There was an error uploading the file.');
    });

}   

function takeScreenshot() {
    fetch('/take-screenshot', {
        method: 'POST'
    })
        .then(response => response.json())
        .then(data => {
            document.getElementById('response').textContent = data.message;
        })
        .catch(error => {
            document.getElementById('response').textContent = 'Failed to take screenshot.';
        });
}

let isRecording = false;

function toggleScreenRecording() {
    const recordTile = document.querySelector('#record-content-options .tile[onclick="toggleScreenRecording()"]');
    const onStopRecordingSubmitLessonButton = document.getElementById('on-stop-recording-submit-lesson-button');  


    isRecording = !isRecording;
    recordTile.setAttribute('data-recording', isRecording);

    if (isRecording) {
        recordTile.querySelector('h2').textContent = 'STOP RECORDING SCREEN ';
        fetch('/begin-recording', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
            .then(response => response.json())
            .then(data => {
                document.getElementById('response').textContent = 'Screen recording started.';
            })
            .catch(error => {
                document.getElementById('response').textContent = 'Failed to start recording.';
            });
    } else {
        recordTile.querySelector('h2').textContent = 'BEGIN RECORDING SCREEN ';
        fetch('/stop-recording', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
            .then(response => response.json())
            .then(data => {
                document.getElementById('response').textContent = 'Screen recording stopped.';

                const subtitleFileName = 'placeholder.csv'; // this needs to come from the web page, and tkinter interface needs to be removed entirely
                onStopRecordingSubmitLessonButton.style.display = 'block';

                submitButton.setAttribute('data-subtitle', subtitleFileName);
            })
            .catch(error => {
                document.getElementById('response').textContent = 'Failed to stop recording.';
            });
    }
}
function onStopRecordingSubmitLesson() {
    const onStopRecordingSubmitLessonButton = document.getElementById('on-stop-recording-submit-lesson-button');
    const subtitleFile = submitButton.getAttribute('data-subtitle');
    window.location.href = '/lesson?subtitle=${encodeURIComponent(subtitleFile)}&prompt_type=Summary';
}

function adjustBoundingBox() {
    fetch('/adjust-bounding-box', {
        method: 'POST'
    })
        .then(response => response.json())
        .then(data => {
            document.getElementById('response').textContent = data.message;
        })
        .catch(error => {
            document.getElementById('response').textContent = 'Failed to adjust bounding box.';
        });
}