import gzip
import lxml
import json
import re
import math
import os, sys
import warnings
import nltk
from warcio.archiveiterator import ArchiveIterator
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
from multiprocessing import Pool, cpu_count

warnings.filterwarnings('ignore')

nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')
nltk.download('punkt')


# Problem 1: The webpage is typically encoded in HTML format.
# We use beautiful soup to extract from html, and refine the raw text.

# Only textual content shown in html is considered to process. Remove HTML head, CSS style, JavaScript, and some.
def clean_text(soup):
    for frame in soup(['style', 'script', 'head', 'meta', 'title', '[document]', 'code', 'blockquote', 'cite']):
        frame.extract()
    text = " ".join(re.findall(r'\w+', soup.get_text()))
    # only extract English, numbers, and some punctuation
    sub_str = re.sub(u"([^\s.,';\u0030-\u0039\u0041-\u005a\u0061-\u007a])", "", text)
    return sub_str.strip()


# the id_list is the output text
def html_text(payload):
    if payload.rec_type == 'response':
        key = payload.rec_headers.get_header(KEYNAME)
        content = payload.content_stream().read()
        soup = BeautifulSoup(content, "lxml")
        text = clean_text(soup)
        if "XML RPC server accepts POST requests only" not in text:
            id_text = [key, text]
            return id_text
        else:
            pass

# Problem 2: Let's assume that we found a way to retrieve the text from a webpage.
# How can we recognize the entities in the text?
# 


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


# sample document
def entity_detect(text):
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
                entity_name = ' '.join(c[0] for c in tagged_tree.leaves())  # get NE name
                entity_type = tagged_tree.label()  # get NE category
                named_entities.append(entity_name)

    return named_entities

    # Problem 3: We now have to disambiguate the entities in the text. For instance, let's assugme that we identified
    # the entity "Michael Jordan". Which entity in Wikidata is the one that is referred to in the text?


# compare the similarity of html text and description, return the link of the best fit
def compute_cosine(text_a, text_b):
    # look for words and their frequency
    words_a = re.split(' |/', text_a)
    words_b = re.split(' |/', text_b)
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
                id = hit['_id']
                if 'schema_name' in hit['_source']:
                    label = hit['_source']['schema_name']
                id_labels.setdefault(id, set()).add(str(label))
    except:
        id_labels = {}
        label = "W"
        id_labels.setdefault('NULL in ES', set()).add(str(label))
    return id_labels


def ent_link(page_id, entities):
    for ent in entities:
        QUERY = ent
        label_description = []
        for entity in search(QUERY).keys():
            label_description.append([entity, str(search(QUERY)[entity])])
        if label_description:
            print(page_id + "\t" + ent.strip() + "\t" + similarity(ent, label_description))


def ner_link(page_text):
    entities = entity_detect(page_text[1])
    ent_link(page_text[0], entities)


if __name__ == '__main__':
    try:
        _, INPUT = sys.argv
    except Exception as e:
        print('Usage: python starter-code.py INPUT')
        sys.exit(0)

    # get the key_text
    KEYNAME = "WARC-TREC-ID"
    recID_text = []

    with gzip.open(INPUT, 'rb') as warcRaw:
        for record in ArchiveIterator(warcRaw):
            item = html_text(record)
            if item:
                recID_text.append(item)
            if record.rec_headers.get_header(KEYNAME) == "clueweb12-0000tw-00-00092":
                break

    with Pool(cpu_count()) as p:
        p.map(ner_link, recID_text)
