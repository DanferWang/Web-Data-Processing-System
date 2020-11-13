import gzip
import lxml
import json
import re
import os, sys
from warcio.archiveiterator import ArchiveIterator
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from neuroner import neuromodel
from elasticsearch import Elasticsearch
from sklearn.feature_extraction.text import TfidfVectorizer


# Problem 1: The webpage is typically encoded in HTML format.
# We should get rid of the HTML tags and retrieve the text. How can we do it?


def clean_text(text):
    sub_str = re.sub(u"([^\s.,';\u0030-\u0039\u0041-\u005a\u0061-\u007a])", "", text)
    return sub_str.strip()


# the key_text is the output of record_id and text in dict
def html_text(payload):
    if payload.rec_type == 'response':
        key = payload.rec_headers.get_header(KEYNAME)
        # print(key)
        content = payload.content_stream().read()
        # print(content)
        soup = BeautifulSoup(content, "lxml")
        text_list = [clean_text(text) for text in soup.stripped_strings]
        text_set = set(text_list)
        text_list = list(text_set)
        text_list = list(filter(None, text_list))
        key_text[key] = text_list
        # print(json.dumps(key_text,indent=2))
        return key_text

    # Problem 2: Let's assume that we found a way to retrieve the text from a webpage. How can we recognize the
    # entities in the text?


class HiddenPrints:
    # Prevent printing
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout


dataset = 'i2b2_2014_deid'
# 'conll2003'
# 'example_unannotated_texts'
# 'i2b2_2014_deid'

model = 'i2b2_2014_glove_spacy_bioes'
# 'conll_2003_en'
# 'i2b2_2014_glove_spacy_bioes'
# 'i2b2_2014_glove_stanford_bioes'
# 'mimic_glove_spacy_bioes'
# 'mimic_glove_stanford_bioes'

# detect entities
def entity_detect(sentence):
    # print("Building model")
    with HiddenPrints():
        neuromodel.fetch_data(dataset)
        neuromodel.fetch_model(model)
        nn = neuromodel.NeuroNER(train_model=False, use_pretrained_model=True)

    entities = nn.predict(sentence)
    return entities

    # Problem 3: We now have to disambiguate the entities in the text. For instance, let's assugme that we identified
    # the entity "Michael Jordan". Which entity in Wikidata is the one that is referred to in the text?


# compare the similarity of html text and description, return the link of the best fit
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


# searching in Elasticsearch and return url: discription in dict
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

    # To tackle this problem, you have access to two tools that can be useful. The first is a SPARQL engine (Trident)
    # with a local copy of Wikidata. The file "test_sparql.py" shows how you can execute SPARQL queries to retrieve
    # valuable knowledge. Please be aware that a SPARQL engine is not the best tool in case you want to lookup for
    # some strings. For this task, you can use elasticsearch, which is also installed in the docker image.
    # The file start_elasticsearch_server.sh will start the elasticsearch server while the file
    # test_elasticsearch_server.py shows how you can query the engine.

    # A simple implementation would be to first query elasticsearch to retrieve all the entities with a label
    # that is similar to the text found in the web page. Then, you can access the SPARQL engine to retrieve valuable
    # knowledge that can help you to disambiguate the entity. For instance, if you know that the webpage refers to persons
    # then you can query the knowledge base to filter out all the entities that are not persons...

    # Obviously, more sophisticated implementations that the one suggested above are more than welcome :-)

    # For now, we are cheating. We are going to returthe labels that we stored in sample-labels-cheat.txt
    # Instead of doing that, you should process the text to identify the entities. Your implementation should return
    # the discovered disambiguated entities with the same format so that I can check the performance of your program.

    # cheats = dict((line.split('\t', 2) for line in open('data/sample-labels-cheat.txt').read().splitlines()))
    # for label, wikidata_id in cheats.items():
    #     if key and (label in payload):
    #         yield key, label, wikidata_id


if __name__ == '__main__':
    try:
        _, INPUT = sys.argv
    except Exception as e:
        print('Usage: python starter-code.py INPUT')
        sys.exit(0)

    # get the key_text
    KEYNAME = "WARC-Record-ID"
    key_text = {}
    with gzip.open(INPUT, 'rt', errors='ignore') as warcRaw:
        for record in ArchiveIterator(warcRaw):
            html_text(record)

    # detect entities and save in recID_entities
    recID_entities = {}
    for rec_id in key_text.keys():
        text = ' '
        strxNew = text.join(key_text.get(rec_id))
        recID_entities[rec_id] = entity_detect(strxNew)

    # linking
    for rec_id in recID_entities.keys():
        sp = rec_id.split(":")[2].replace(">", "")
        for ent in recID_entities.get(rec_id):
            QUERY = ent
            label_description = []
            for entity in search(QUERY).keys():
                label_description.append([entity, str(search(QUERY)[entity])])
            if label_description:
                html_text = " ".join(key_text[rec_id])
                print(sp + " " + ent + " " + similarity(html_text, label_description))
