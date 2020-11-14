import gzip
import lxml
import json
import re
from warcio.archiveiterator import ArchiveIterator
from bs4 import BeautifulSoup
from urllib.parse import urlparse

KEYNAME = "WARC-TREC-ID"

key_text = {}
out_json = "parsed_json_93.json"

def clean_text(text):
    sub_str = re.sub(u"([^\s.,';\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a\uAC00-\uD7AF\u3040-\u31FF])","",text)
    return sub_str.strip()

def html_text(payload):
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

with gzip.open("./data/sample.warc.gz",'rb') as warcRaw:
    for record in ArchiveIterator(warcRaw):
        html_text(record)
        if record.rec_headers.get_header(KEYNAME) == "clueweb12-0000tw-00-00092":
            break

with open(out_json,'w') as out:
    json.dump(key_text, out)
