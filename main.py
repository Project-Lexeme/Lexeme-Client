from flask import Flask, request, jsonify, send_from_directory, render_template
import os
import screenshot_text_extractor, prompt_generator, startup, setup_pytesseract, config
from screen_recorder import ScreenRecorder 
import LLMserver
import logger
import webbrowser
from pathlib import Path
import app

'''
TODO: check out Koboldcpp for a means to deploy LLM server 
TODO: review TODOs and fix things
TODO: look closer at how choices get passed back and forth
TODO: rework the subtitle.csv naming convention and work in a folder 
TODO: refactor, clean - DO IT. don't be lazy. Big rocks are prompt_generator
TODO: work on screen recorder OCR performance
TODO: add support for multiple monitors - Desktopmagic library for python - wil be a headache.
TODO: TEST packaging the thing up and launching from a clean environment. At home, maybe
TODO: add support for config file with LLM API info, potentially have user-input required with opening windows if no config file is found?

'''

'''
Prompts could include the use of previously touched terms as reinforcement - e.g. Give me a summary of x. Please use as many touched terms as possible.
Pictures
prompts that broaden context around a target term by teaching related terms
specify context of terms or choose multiple contexts to define terms
think about poisoning 

'''

'''
python -m PyInstaller main.spec main.py
'''

if __name__ == '__main__':
    app.start_app()

    