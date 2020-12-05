# -*- coding: utf-8 -*-
"""
Created on Sat Dec  5 13:27:45 2020

@author: ianbe
"""

import numpy as np
from collections import Counter
import pandas as pd
import os, sys
import time
import json


class HiddenPrints:
    #Prevent printing
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout

with HiddenPrints():
    from neuroner import neuromodel
    
def decode_sentiment(label):
    return decode_map[int(label)]

dataset = 'i2b2_2014_deid'
#'conll2003'
#'example_unannotated_texts'
#'i2b2_2014_deid'

model = 'i2b2_2014_glove_stanford_bioes'
#'conll_2003_en'
#'i2b2_2014_glove_spacy_bioes'
#'i2b2_2014_glove_stanford_bioes'
#'mimic_glove_spacy_bioes'
#'mimic_glove_stanford_bioes'

print("Building model")

with HiddenPrints():
    neuromodel.fetch_data(dataset)
    neuromodel.fetch_model(model)
    nn = neuromodel.NeuroNER(train_model=False, use_pretrained_model=True)

start_time = time.time()
data = pd.read_csv("kindle_reviews.csv", na_filter=False, index_col=0, nrows=1000)
filtered_data = data.drop(columns=["helpful", "reviewTime", "reviewerID", "reviewerName", "unixReviewTime"])

decode_map = {1: "NEGATIVE", 2: "NEGATIVE", 3: "NEUTRAL", 4: "POSITIVE", 5: "POSITIVE" }

filtered_data['label'] = filtered_data.overall.apply(lambda x: decode_sentiment(x))

books = filtered_data.asin.unique()
books_dict = {}

for book in books:
    books_dict[book] = {}
    df = filtered_data[filtered_data['asin'] == book]
    df = df.reset_index()
    print(book)
    for index, row in df.iterrows():
        books_dict[book][index] = {'review': row.reviewText,'summary': row.summary, 'rating': row.overall,'label': row.label}
        sentences = books_dict[book][index]['review'].replace('? ', '. ')
        sentences = sentences.replace('! ', '. ')
        sentences = sentences.split('. ')
        books_dict[book][index]['sentences'] = {}
        for i, sentence in enumerate(sentences):
            if not sentence:
                print('empty')
            else:
                entities = nn.predict(sentence)
                books_dict[book][index]['sentences'][i] = {'sentence': sentence, 'entities': entities}

json = json.dumps(books_dict)
f = open("books_dict.json","w")
f.write(json)
f.close()
print(books_dict)
print("--- %s seconds ---" % (time.time() - start_time))            