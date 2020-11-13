import os, sys
import json
from neuroner import neuromodel


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


def entity_detect(sentence):
    # print("Building model")
    with HiddenPrints():
        neuromodel.fetch_data(dataset)
        neuromodel.fetch_model(model)
        nn = neuromodel.NeuroNER(train_model=False, use_pretrained_model=True)

    # print("predicting")
    entities = nn.predict(sentence)
    return entities


with open("parsed_json.json", 'r') as load_f:
    load_dict = json.load(load_f)
newJson = {}
for i in load_dict.keys():
    strx = ' '
    strxNew = strx.join(load_dict.get(i))
    newJson[i] = entity_detect(strxNew)
with open("entities_json.json", "w") as f:
    # json.dump(dict_, f)
    json.dump(newJson, f, indent=2, sort_keys=True, ensure_ascii=False)
