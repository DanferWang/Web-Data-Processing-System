import os, sys
import json
from neuroner import neuromodel
from elasticsearch import Elasticsearch
from sklearn.feature_extraction.text import TfidfVectorizer


class HiddenPrints:
    # Prevent printing
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout


dataset = 'conll2003'
# 'conll2003'
# 'example_unannotated_texts'
# 'i2b2_2014_deid'

model = 'conll_2003_en'

# 'conll_2003_en'
# 'i2b2_2014_glove_spacy_bioes'
# 'i2b2_2014_glove_stanford_bioes'
# 'mimic_glove_spacy_bioes'
# 'mimic_glove_stanford_bioes'
print("Building model")
with HiddenPrints():
    neuromodel.fetch_data(dataset)
    neuromodel.fetch_model(model)
    nn = neuromodel.NeuroNER(train_model=False, use_pretrained_model=True)


def entity_detect(sentence):
    print("predicting")
    entities = nn.predict(sentence)
    return entities


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
    response = e.search(index="wikidata_en", body=json.dumps(p))
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
    return id_labels


if __name__ == '__main__':
    import sys

    try:
        _, QUERY = sys.argv
    except Exception as e:
        QUERY = 'Vrije Universiteit Amsterdam'
    with open("parsed_json_93.json", 'r') as load_f:
        rec_text = json.load(load_f)

    recID_entities = {}
    for i in rec_text.keys():
        strx = ' '
        strxNew = strx.join(rec_text.get(i))
        recID_entities[i] = entity_detect(strxNew)

    for i in recID_entities.keys():
        sp = i.split(":")[2].replace(">", "")
        for k in recID_entities.get(i):
            QUERY = k
            # print(k)
            mylist = []
            for entity in search(QUERY).keys():
                mylist.append([entity, str(search(QUERY)[entity])])
            # print(mylist)
            if mylist:
                html_text = " ".join(rec_text[i])
                print(sp + " " + k + " " + similarity(html_text, mylist))

