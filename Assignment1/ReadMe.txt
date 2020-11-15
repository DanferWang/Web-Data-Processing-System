Install the following Libraries:
lxml
warcio
bs4 
gzip
lxml
json
re
math
os
sys
warnings
elasticsearch
multiprocessing
neuroner

Run the Shell script stater_code.sh:
sh test_sample.sh
It will directly run the proedure of linking and scoring on the sample. Then it will create file with the result of record_id, entity_name, and linking_page. Next, the evaluation criteria can be printed.

Installation guide neuroner library:
https://github.com/Franck-Dernoncourt/NeuroNER
1. pip3 install tensorflow
2. pip3 install pyneuroner[gpu]
3. python -m spacy download en
4. unzip http://neuroner.com/data/word_vectors/glove.6B.100d.zip in ./data/word_vectors use
wget -P data/word_vectors http://neuroner.com/data/word_vectors/glove.6B.100d.zip unzip data/word_vectors/glove.6B.100d.zip -d data/word_vectors/ or do it manually

A short report regarding the program can be found in the document Web data processing, first assignment, group 13 
