import json
from sklearn.feature_extraction.text import TfidfVectorizer

out_json = "parsed_json_1.1.json"
with open(out_json,'r') as file:
    rec_text = json.load(file)
des = [["123", "nice"],["456", "hello I am boy"],["789", "my"]]


def similarity(text, descriptions):
    sim = {}
    try:
        for des in descriptions:
            vec = TfidfVectorizer(min_df=1, stop_words="english")
            freq = vec.fit_transform([text.lower(), des[1].lower()])
            similarity_mat = freq * freq.T
            sim[des[0]] = similarity_mat[0,1]
        link = max(sim, key=lambda x:(x[0]))
        return link
    except:
        exc = "invalid text HTML"
        return exc

for rec_id, text_list in rec_text.items():
    html_text = " ".join(text_list)
    print(similarity(html_text, des))
    
    
