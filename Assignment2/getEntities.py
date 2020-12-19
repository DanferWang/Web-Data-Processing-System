import re
import pandas as pd
import nltk
#These four file should be downloaded at the first time
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')
nltk.download('punkt')


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


def get_entity(text):
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
               if entity_type =='PERSON': #get PERSON entity
                   named_entities.append(entity_name)
               
    return named_entities



data = pd.read_csv("/content/drive/My Drive/Colab Notebooks/clean_kindle_reviews.csv")

from nltk.tokenize import sent_tokenize
stencesE=[]
allStences=[]
bookid=[]
for i in range(0,982618):
    # only process string text
    if type(data['reviewText'][i])!=str:
        print(i)
        continue
    # replace some words
    temp=data['reviewText'][i].replace('author','Author')
    sentList=sent_tokenize(temp.replace('writer','Author'))
    # get entities in sentences
    for sentence in sentList:
        entities=get_entity(sentence)
        if len(entities)!=0:
            for e in entities:
                stencesE.append(e)
                allStences.append(sentence)
                bookid.append(data['asin'][i])
    # tell how many items are processed
    if i%10000==0:
        print(i)
 
 
 # save file
dataframe = pd.DataFrame({'bookid':bookid,'entity':stencesE,'sentence':allStences})
dataframe.to_csv("/content/drive/My Drive/Colab Notebooks/test5.csv",index=False,sep=',')
