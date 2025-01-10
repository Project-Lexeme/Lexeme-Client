To add support for a new language:
	
 	1. in Venv, use python interactive interpreter to download target spacy language
	
 	2. in venv/Lib/site-packages/target-language-directory, copy contents of versioned subdirectory into the parent target language directory
	
 	3. open up {language}.spec in spec/
	
 	4. add 'venv/Lib/site-packages/{target language spacy module name}', 'spacy/data/{target language spacy module name}'
	
 	5. add relevant dictionary - if it doesn't exist, find one online and parse it into correct format (e.g. de-en-enwiktionary.txt -> deu_dictionary.csv)

 	6. build that relevant .spec or all - good luck figuring out what directory to run it from to get relative paths correct
 	
  	7. cry
