import re
import pandas as pd
import nltk
import json
#These four file should be downloaded at the first time
#nltk.download('averaged_perceptron_tagger')
#nltk.download('maxent_ne_chunker')
#nltk.download('words')
#nltk.download('punkt')


def parse_document(document):
   document = re.sub('\n', ' ', document)
   if isinstance(document, str):
       document = document
   else:
       raise ValueError('Document is not string!')
   document = document.strip()
   sentences = nltk.sent_tokenize(document)
   sentences = [sentence.strip() for sentence in sentences]
   return sentences

# sample document
def entity_detect(text):
    # tokenize sentences
    sentences = parse_document(text)
    tokenized_sentences = [nltk.word_tokenize(sentence) for sentence in sentences]
    # tag sentences and use nltk's Named Entity Chunker
    tagged_sentences = [nltk.pos_tag(sentence) for sentence in tokenized_sentences]
    ne_chunked_sents = [nltk.ne_chunk(tagged) for tagged in tagged_sentences]
    # extract all named entities
    named_entities = []
    for ne_tagged_sentence in ne_chunked_sents:
       for tagged_tree in ne_tagged_sentence:
           # extract only chunks having NE labels
           if hasattr(tagged_tree, 'label'):
               entity_name = ' '.join(c[0] for c in tagged_tree.leaves()) #get NE name
               entity_type = tagged_tree.label() # get NE category
               named_entities.append(entity_name)

    return named_entities

with open("parsed_json_93.json", 'r') as load_f:
    rec_text = json.load(load_f)
    recID_entities = {}
    for i in rec_text.keys():
        strxNew = rec_text.get(i)
        recID_entities[i] = entity_detect(strxNew)
    with open("en93nltk.json",'w') as out:
        json.dump(recID_entities,out)
