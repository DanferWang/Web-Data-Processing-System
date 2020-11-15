Install the Libraries:
pip3 install lxml
pip3 install nltk
pip3 install warcio
pip3 install bs4

These four file should be downloaded at the first time in the stater_code_v2.5.py:
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')
nltk.download('punkt')

Run the Shell script stater_code.sh:
sh test_sample.sh
It will directly run the proedure of linking and scoring on the sample. Then it will create file with the result of record_id, entity_name, and linking_page. Next, the evaluation criteria can be printed.