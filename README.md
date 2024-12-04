Project Lexeme:

Roadmap as of 12/4
	1. December goals:
		- release feature set to include tutorial, configuration editing, and some Quality of Life upgrades for UX
		- find short-term funds for hosting, either on AWS (~$400/month) or using a supercomputer somewhere.
			- if acquired, limited local release to target audience
				- if limited local release, develop feedback mechanism 
		- present to local leadership and secure permission to open-source the project.

	2. January goals:
		- present to ODNI TEG (in talks with Mr. Purkey and Hamrick at ODNI) to generate buzz
		- broaden beta tester pool
		- release first publically-available version of app with accompanying access token distribution
		- look into audio capture instead of just relying on subtitles

	3. Spring 2025 goals:
		- mature audio capture
		- get link on AFCLC website under resources page
		- attend relevant conferences if feasible, if not continue to use partners to advocate for project
	
	4. Summer 2025 goals:
		- 

	5. Indefinite future goals:
		- pursue ATO as fully open-source software
		- long term advocate of the project, share where possible
		- benevolent dictator for life of open-source project 
		- willing to help contractors build on top of it
	

To add support for a new language:
	1. in Venv, use python interactive interpreter to download target spacy language
	2. in venv/Lib/site-packages/target-language-directory, copy contents of versioned subdirectory into the parent target language directory
	3. open up {language}.spec in spec/
	4. add 'venv/Lib/site-packages/{target language spacy module name}', 'spacy/data/{target language spacy module name}'
	5. add relevant dictionary - if it doesn't exist, find one online and parse it into correct format (e.g. de-en-enwiktionary.txt -> deu_dictionary.csv)
	6. cry