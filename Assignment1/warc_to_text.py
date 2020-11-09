import gzip
import lxml
import json
import re
from warcio.archiveiterator import ArchiveIterator
from bs4 import BeautifulSoup
from urllib.parse import urlparse

KEYNAME = "WARC-Record-ID"

key_text = {}
out_json = "parsed_json_1.1.json"

def clean_text(text):
    sub_str = re.sub(u"([^\s.,';\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a\uAC00-\uD7AF\u3040-\u31FF])","",text)
    return sub_str.strip()

def find_labels(payload):
    if payload.rec_type == 'response':
        key = payload.rec_headers.get_header(KEYNAME)
        #print(key)
        content = payload.content_stream().read()
        #print(content)
        soup = BeautifulSoup(content, "lxml")
        text_list = [clean_text(text) for text in soup.stripped_strings]
        text_set = set(text_list)
        text_list = list(text_set)
        text_list = list(filter(None,text_list))
        key_text[key] = text_list
        #print(json.dumps(key_text,indent=2))
        return key_text

with gzip.open("./data/warcs/CC-MAIN-20200927121105-20200927151105-00583.warc.gz",'rb') as warcRaw:
    for record in ArchiveIterator(warcRaw):
        find_labels(record)

with open(out_json,'w') as out:
    json.dump(key_text, out)
