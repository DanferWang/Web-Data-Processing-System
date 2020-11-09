# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 12:26:39 2020

@author: ianbe

Documentation for neuroner: http://neuroner.com/ and https://github.com/Franck-Dernoncourt/NeuroNER
"""
import os, sys

class HiddenPrints:
    #Prevent printing
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout

from neuroner import neuromodel

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

Test_sentence = "The Beatles were an English rock band formed in Liverpool in 1960. The group, whose best-known line-up comprised John Lennon, Paul McCartney, George Harrison and Ringo Starr, are regarded as the most influential band of all time. They were integral to the development of 1960s counterculture and popular music's recognition as an art form. Rooted in skiffle, beat and 1950s rock and roll, their sound incorporated elements of classical music and traditional pop in innovative ways; the band later explored music styles ranging from ballads and Indian music to psychedelia and hard rock. As pioneers in recording, songwriting and artistic presentation, the Beatles revolutionised many aspects of the music industry and were often publicised as leaders of the era's youth and sociocultural movements."

with HiddenPrints():
    neuromodel.fetch_data(dataset)
    neuromodel.fetch_model(model)
    nn = neuromodel.NeuroNER(train_model=False, use_pretrained_model=True)
    
predict = nn.predict(Test_sentence)