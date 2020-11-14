import os, sys
import json
from neuroner import neuromodel
import warnings
 
warnings.filterwarnings('ignore')
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

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
    with HiddenPrints():
        entity = nn.predict(sentence)
        entities = []
        for i in range(len(entity)):
            entities.append(entity[i]['text'])
    return entities

if __name__ == '__main__':
    with open("parsed_json_93.json", 'r') as load_f:
        rec_text = json.load(load_f)
    recID_entities = {}
    for i in rec_text.keys():
        strx = ' '
        strxNew = strx.join(rec_text.get(i))
        recID_entities[i] = entity_detect(strxNew)
    with open("en93.json",'w') as out:
        json.dump(recID_entities,out)

