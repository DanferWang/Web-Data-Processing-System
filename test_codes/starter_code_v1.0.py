import gzip
import lxml
import json
import re
import os, sys
import warnings
from warcio.archiveiterator import ArchiveIterator
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from neuroner import neuromodel
from elasticsearch import Elasticsearch
from sklearn.feature_extraction.text import TfidfVectorizer

warnings.filterwarnings('ignore')
# Problem 1: The webpage is typically encoded in HTML format.
# We should get rid of the HTML tags and retrieve the text. How can we do it?


def clean_text(text):
    sub_str = re.sub(u"([^\s.,';\u0030-\u0039\u0041-\u005a\u0061-\u007a])", "", text)
    return sub_str.strip()


# the key_text is the output of record_id and text in dict
def html_text(key_text, payload):
    if payload.rec_type == 'response':
        key = payload.rec_headers.get_header(KEYNAME)
        content = payload.content_stream().read()
        soup = BeautifulSoup(content, "lxml")
        text_list = [clean_text(text) for text in soup.stripped_strings]
        if "XMLRPC server accepts POST requests only." not in text_list:
            text_set = set(text_list)
            text_list = list(text_set)
            text_list = list(filter(None, text_list))
            if text_list:
                key_text[key] = text_list
    return key_text

def read_warc(warcRaw):
    recID_text = {}
    for record in ArchiveIterator(warcRaw):
        recID_text = html_text(recID_text, record)
    return recID_text

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

with HiddenPrints():
    neuromodel.fetch_data(dataset)
    neuromodel.fetch_model(model)
    nn = neuromodel.NeuroNER(train_model=False, use_pretrained_model=True)

# detect entities
def entity_detect(sentence):
    print("predicting")
    entity = nn.predict(sentence)
    entities = []
    for i in range(len(entity)):
        entities.append(entity[i]['text'])
    return entities

def entitis_dict(key_text):
    recID_entities = {}
    for rec_id in key_text.keys():
        text = ' '
        strxNew = text.join(key_text.get(rec_id))
        recID_entities[rec_id] = entity_detect(strxNew)
    return recID_entities

    # Problem 3: We now have to disambiguate the entities in the text. For instance, let's assugme that we identified
    # the entity "Michael Jordan". Which entity in Wikidata is the one that is referred to in the text?


# compare the similarity of html text and description, return the link of the best fit
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

def ent_link(key_text, recID_entities):
    for rec_id in recID_entities.keys():
        page_id = rec_id.split(":")[2].replace(">", "")
        for ent in recID_entities.get(rec_id):
            QUERY = ent
            label_description = []
            for entity in search(QUERY).keys():
                label_description.append([entity, str(search(QUERY)[entity])])
            if label_description:
                html_text = " ".join(key_text[rec_id])
                print(page_id + "\t" + ent + "\t" + similarity(html_text, label_description))

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
        read_warc(warcRaw)

    # detect entities and save in recID_entities
    recID_entities = entitis_dict(key_text)

    # linking
    ent_link(key_text, recID_entities)
