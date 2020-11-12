# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 17:06:06 2020

@author: ianbe
"""
import requests
import json
from elasticsearch import Elasticsearch
import time
import os, sys
from neuroner import neuromodel

class HiddenPrints:
    #Prevent printing
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout


dataset = 'i2b2_2014_deid'
#'conll2003'
#'example_unannotated_texts'
#'i2b2_2014_deid'

model = 'i2b2_2014_glove_spacy_bioes'
#'conll_2003_en'
#'i2b2_2014_glove_spacy_bioes'
#'i2b2_2014_glove_stanford_bioes'
#'mimic_glove_spacy_bioes'
#'mimic_glove_stanford_bioes'

#Test_sentence = "The Beatles were an English rock band formed in Liverpool in 1960. The group, whose best-known line-up comprised John Lennon, Paul McCartney, George Harrison and Ringo Starr, are regarded as the most influential band of all time. They were integral to the development of 1960s counterculture and popular music's recognition as an art form. Rooted in skiffle, beat and 1950s rock and roll, their sound incorporated elements of classical music and traditional pop in innovative ways; the band later explored music styles ranging from ballads and Indian music to psychedelia and hard rock. As pioneers in recording, songwriting and artistic presentation, the Beatles revolutionised many aspects of the music industry and were often publicised as leaders of the era's youth and sociocultural movements."
Test_sentence = "FIFA was founded in 1904 to oversee international competition among the national associations of Belgium, Denmark, France, Germany, the Netherlands, Spain, Sweden, and Switzerland. Headquartered in Zürich, its membership now comprises 211 national associations. Member countries must each also be members of one of the six regional confederations into which the world is divided: Africa, Asia, Europe, North & Central America and the Caribbean, Oceania, and South America."

print("Building model")

with HiddenPrints():
    neuromodel.fetch_data(dataset)
    neuromodel.fetch_model(model)
    nn = neuromodel.NeuroNER(train_model=False, use_pretrained_model=True)

print("predicting")

entities = nn.predict(Test_sentence)

#entities = [{'id': 'T1', 'type': 'ORG', 'start': 0, 'end': 4, 'text': 'FIFA'}, {'id': 'T2', 'type': 'LOC', 'start': 97, 'end': 104, 'text': 'Belgium'}, {'id': 'T3', 'type': 'LOC', 'start': 106, 'end': 113, 'text': 'Denmark'}, {'id': 'T4', 'type': 'LOC', 'start': 115, 'end': 121, 'text': 'France'}, {'id': 'T5', 'type': 'LOC', 'start': 123, 'end': 130, 'text': 'Germany'}, {'id': 'T6', 'type': 'LOC', 'start': 136, 'end': 147, 'text': 'Netherlands'}, {'id': 'T7', 'type': 'LOC', 'start': 149, 'end': 154, 'text': 'Spain'}, {'id': 'T8', 'type': 'LOC', 'start': 156, 'end': 162, 'text': 'Sweden'}, {'id': 'T9', 'type': 'LOC', 'start': 168, 'end': 179, 'text': 'Switzerland'}, {'id': 'T10', 'type': 'LOC', 'start': 198, 'end': 204, 'text': 'Zürich'}, {'id': 'T11', 'type': 'LOC', 'start': 380, 'end': 386, 'text': 'Africa'}, {'id': 'T12', 'type': 'LOC', 'start': 388, 'end': 392, 'text': 'Asia'}, {'id': 'T13', 'type': 'LOC', 'start': 394, 'end': 400, 'text': 'Europe'}, {'id': 'T14', 'type': 'ORG', 'start': 402, 'end': 425, 'text': 'North & Central America'}, {'id': 'T15', 'type': 'LOC', 'start': 434, 'end': 443, 'text': 'Caribbean'}, {'id': 'T16', 'type': 'LOC', 'start': 445, 'end': 452, 'text': 'Oceania'}, {'id': 'T17', 'type': 'LOC', 'start': 458, 'end': 471, 'text': 'South America'}]

def search(query):
    e = Elasticsearch()
    p = { "query" : { "query_string" : { "query" : query }}}
    print(p)
    response = e.search(index="wikidata_en", body=json.dumps(p), size=20)
    id_labels = {}
    if response:
        for hit in response['hits']['hits']:
            id = hit['_id']
            if 'schema_name' in hit['_source'].keys():
                label = hit['_source']['schema_name']
                id_labels.setdefault(id, set()).add(label)
            if 'schema_description' in hit['_source'].keys():
                description = hit['_source']['schema_description']
                id_labels.setdefault(id, set()).add(description)
    return id_labels

if __name__ == '__main__':
    for ent in entities:
        QUERY = ent['text']
        for entity, labels in search(QUERY).items():
            print(entity, labels)
