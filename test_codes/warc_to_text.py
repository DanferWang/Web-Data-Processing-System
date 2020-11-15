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

def clean_text(soup):
    for frame in soup(['style', 'script', 'head', 'meta', 'title', '[document]', 'code', 'blockquote', 'cite']):
        frame.extract()
    text = " ".join(re.findall(r'\w+', soup.get_text()))
    sub_str = re.sub(u"([^\s.,';\u0030-\u0039\u0041-\u005a\u0061-\u007a])", "",text)
    return sub_str.strip()

def html_text(payload):
    if payload.rec_type == 'response':
        key = payload.rec_headers.get_header(KEYNAME)
        content = payload.content_stream().read()
        soup = BeautifulSoup(content, "lxml")
        text = clean_text(soup)
        if "XML RPC server accepts POST requests only" not in text:
            if text:
                key_text[key] = text
    return key_text

with gzip.open("./data/sample.warc.gz",'rb') as warcRaw:
    for record in ArchiveIterator(warcRaw):
        html_text(record)
        if record.rec_headers.get_header(KEYNAME) == "clueweb12-0000tw-00-00092":
            break

with open(out_json,'w') as out:
    json.dump(key_text, out)
