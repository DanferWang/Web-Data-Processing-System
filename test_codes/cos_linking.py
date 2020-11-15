import os, sys
import json
import re
import math
from elasticsearch import Elasticsearch
from sklearn.feature_extraction.text import TfidfVectorizer

def compute_cosine(text_a, text_b):
    # look for words and their frequency
    words_a = re.split(' |/',text_a)
    words_b = re.split(' |/',text_b)
    words1 = list(set(words_a))
    words2 = list(set(words_b))
    words1_dict = {}
    words2_dict = {}
    for word in words1:
        word = re.sub('[^a-zA-Z]', '', word)
        word = word.lower()
        if word in words1_dict and word != '':
            num = words1_dict[word]
            words1_dict[word] = num + 1
        elif word != '':
            words1_dict[word] = 1
        else:
            continue
    for word in words2:
        word = re.sub('[^a-zA-Z]', '', word)
        word = word.lower()
        if word in words2_dict and word != '':
            num = words2_dict[word]
            words2_dict[word] = num + 1
        elif word != '':
            words2_dict[word] = 1
        else:
            continue

    # return True
    dic1 = sorted(words1_dict.items(), key=lambda asd: asd[1], reverse=True)
    dic2 = sorted(words2_dict.items(), key=lambda asd: asd[1], reverse=True)

    # word vec
    words_key = []
    for i in range(len(dic1)):
        words_key.append(dic1[i][0])
    for i in range(len(dic2)):
        if dic2[i][0] in words_key:
            pass
        else:
            words_key.append(dic2[i][0])
    vect1 = []
    vect2 = []
    for word in words_key:
        if word in words1_dict:
            vect1.append(words1_dict[word])
        else:
            vect1.append(0)
        if word in words2_dict:
            vect2.append(words2_dict[word])
        else:
            vect2.append(0)

    # calculate cosine sim
    sum = 0
    sq1 = 0
    sq2 = 0
    for i in range(len(vect1)):
        sum += vect1[i] * vect2[i]
        sq1 += pow(vect1[i], 2)
        sq2 += pow(vect2[i], 2)
    try:
        result = round(float(sum) / (math.sqrt(sq1) * math.sqrt(sq2)), 2)
    except ZeroDivisionError:
        result = 0.0
    return result

def similarity(text, descriptions):
    sim = {}
    try:
        for des in descriptions:
            sim[des[0]] = compute_cosine(text.lower(), des[1].lower())
        link = max(sim, key=sim.get)
        return link
    except:
        exc = "invalid text HTML"
        return exc


def search(query):
    e = Elasticsearch()
    p = {"query": {"query_string": {"query": query}}}
    try:
        response = e.search(index="wikidata_en", body=json.dumps(p), request_timeout=60, size=30)
        id_labels = {}
        if response:
            for hit in response['hits']['hits']:
                label = "W"
#                description = "L"
                id = hit['_id']
                if 'schema_name' in hit['_source']:
                    label = hit['_source']['schema_name']
#                if 'schema_description' in hit['_source']:
#                    description = hit['_source']['schema_description']
                id_labels.setdefault(id, set()).add(str(label))
    except:
        id_labels = {}
        label = "W"
#        description = "L"
        id_labels.setdefault('NULL in ES', set()).add(str(label))
    return id_labels


if __name__ == '__main__':
#    with open("parsed_json_93.json", 'r') as load_f:
#        rec_text = json.load(load_f)
    with open("en93nltk.json",'r') as load_en:
        recID_entities = json.load(load_en)
    for i in recID_entities.keys():
        #sp = i.split(":")[2].replace(">", "")
        for k in recID_entities.get(i):
            QUERY = k
            mylist = []
            for entity in search(QUERY).keys():
                mylist.append([entity, str(search(QUERY)[entity])])
            if mylist:
#                html_text = rec_text[i]
                print(i + "\t" + k.strip() + "\t" + similarity(QUERY, mylist))

