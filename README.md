The releasable package plan:

Wrap up projectlexeme_server into an executable

If local hosting: 

 	-package up something like Koboldcpp to deploy GGUF LLM to local host
	
 	-package up GGUF file with appropriate model
	
 	-create .bat to set up Koboldcpp with model loaded

regardless:

 	-write .bat file to 
	
  		-pass correct server address to app.py and/or launch server
		
  		-launch app.py
		
  		-launch web browser to app homepage


To add support for a new language:
	1. in Venv, use python interactive interpreter to download target spacy language
	2. in venv/Lib/site-packages/target-language-directory, copy contents of versioned subdirectory into the parent target language directory
	3. open up main.spec in root project folder
	4. add 'venv/Lib/site-packages/{target language spacy module name}', 'spacy/data/{target language spacy module name}'
	5. cry