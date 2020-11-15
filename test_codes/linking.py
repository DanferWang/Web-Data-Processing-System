import os, sys
import json
from elasticsearch import Elasticsearch
from sklearn.feature_extraction.text import TfidfVectorizer

def similarity(text, descriptions):
    sim = {}
    try:
        for des in descriptions:
            vec = TfidfVectorizer(min_df=1, stop_words="english")
            freq = vec.fit_transform([text.lower(), des[1].lower()])
            similarity_mat = freq * freq.T
            sim[des[0]] = similarity_mat[0, 1]
        link = max(sim, key=lambda x: (x[0]))
        return link
    except:
        exc = "invalid text HTML"
        return exc


def search(query):
    e = Elasticsearch()
    p = {"query": {"query_string": {"query": query}}}
    try:
        response = e.search(index="wikidata_en", body=json.dumps(p), request_timeout=60)
        id_labels = {}
        if response:
            for hit in response['hits']['hits']:
                label = "W"
                description = "L"
                id = hit['_id']
                if 'schema_name' in hit['_source']:
                    label = hit['_source']['schema_name']
                if 'schema_description' in hit['_source']:
                    description = hit['_source']['schema_description']
                id_labels.setdefault(id, set()).add(str(label) + " " + str(description))
    except:
        id_labels = {}
        label = "W"
        description = "L"
        id_labels.setdefault('NULL in ES', set()).add(str(label) + " " + str(description))
    return id_labels


if __name__ == '__main__':
    with open("parsed_json_93.json", 'r') as load_f:
        rec_text = json.load(load_f)
    with open("en93.json",'r') as load_en:
        recID_entities = json.load(load_en)
    for i in recID_entities.keys():
        #sp = i.split(":")[2].replace(">", "")
        for k in recID_entities.get(i):
            QUERY = k
            mylist = []
            for entity in search(QUERY).keys():
                mylist.append([entity, str(search(QUERY)[entity])])
            if mylist:
                html_text = rec_text[i]
                print(i + "\t" + k + "\t" + similarity(QUERY, mylist))

