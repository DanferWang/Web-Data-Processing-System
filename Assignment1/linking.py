import requests
import json
from elasticsearch import Elasticsearch
from sklearn.feature_extraction.text import TfidfVectorizer

def similarity(text, descriptions):
    sim = {}
    #try:
    for des in descriptions:
        vec = TfidfVectorizer(min_df=1, stop_words="english")
        freq = vec.fit_transform([text.lower(), des[1].lower()])
        similarity_mat = freq * freq.T
        sim[des[0]] = similarity_mat[0,1]
    link = max(sim, key=lambda x:(x[0]))
    return link
    #except:
        #exc = "invalid text HTML"
        #return exc

def search(query):
    e = Elasticsearch()
    p = { "query" : { "query_string" : { "query" : query }}}
    response = e.search(index="wikidata_en", body=json.dumps(p))
    id_labels = {}
    if response:
        for hit in response['hits']['hits']:
            if 'schema_description' in hit['_source']:
                label = hit['_source']['schema_description']
                id = hit['_id']
                id_labels.setdefault(id, set()).add(label)
            else:
                continue
    return id_labels

if __name__ == '__main__':
    import sys
    try:
        _, QUERY = sys.argv
    except Exception as e:
        QUERY = 'Vrije Universiteit Amsterdam'
    with open("data/entities_json.json",'r') as load_f:
        load_dictN = json.load(load_f)
    with open("data/parsed_json_1.1.json",'r') as file:
        rec_text = json.load(file)
    #print(rec_text)
    #mylist=[]
    for i in load_dictN.keys():
        for k in load_dictN.get(i):
            QUERY=k
            #print(k)
            mylist=[]
            for entity in search(QUERY).keys():
                mylist.append([entity, str(search(QUERY)[entity])])
            #print(mylist)
            if mylist:
                html_text = " ".join(rec_text[i])
                print(i + " " + k + " " + similarity(html_text, mylist))

