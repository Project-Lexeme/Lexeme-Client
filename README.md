Project Lexeme:

Roadmap as of 12/4
	
 	1. December goals:
		- release feature set to include tutorial, configuration editing, and some Quality of Life upgrades for UX
		- find short-term solution for hosting
			- if acquired, limited local release to target audience
				- if limited local release, develop feedback mechanism 
		- present to local leadership and secure permission to open-source the project.
		- virtual show-and-tell with AFCLC, DLI 

	2. January goals:
		- present to ODNI TEG (in talks with Mr. Purkey and Hamrick) to generate buzz (scheduled)
		- broaden beta tester pool
		- release first publically-available v1.0 of app with accompanying access token distribution
		- look into audio capture instead of just relying on subtitles

	3. Spring 2025 goals:
		- mature audio capture capabilities if pursued
		- get link on AFCLC website under resources page
		- if there exists other repository of approved language tools, get there (e.g. if DLI has such a list)
		- attend relevant conferences, present at working groups, etc. if feasible. If not continue to use partners to advocate for project.
	
	4. Summer 2025 goals:
		- v1.5 release - feature set pending
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

 	6. build that relevant .spec or all - good luck figuring out what directory to run it from to get relative paths correct
 	
  	7. cry
