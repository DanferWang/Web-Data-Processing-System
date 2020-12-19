import pandas as pd
import numpy as np
from collections import Counter

DATASET_ENCODING = "ISO-8859-1"
dataset_path = "F:\VU\The_Social_Web/twitter1600000.csv"
print("Open file:", dataset_path)
df = pd.read_csv(dataset_path, encoding =DATASET_ENCODING ,lineterminator='\n')

decode_map = {0: "NEGATIVE", 2: "NEUTRAL", 4: "POSITIVE"}
def decode_sentiment(label):
    return decode_map[int(label)]
df.target = df.target.apply(lambda x: decode_sentiment(x))

target_cnt = Counter(df.target)
print(target_cnt)

def lower_sample_data(df, percent=1):
    data1 = df[df['target'] == "POSITIVE"]
    data0 = df[df['target'] == "NEUTRAL"]
    data_1 = df[df['target'] == "NEGATIVE"]
    index1 = np.random.randint(len(data1), size=percent * (len(df) - len(data1) - len(data0)))
    lower_data1 = data1.iloc[list(index1)]
    df = pd.concat([lower_data1, data0, data_1])
    data1 = df[df['target'] == "POSITIVE"]
    data0 = df[df['target'] == "NEUTRAL"]
    data_1 = df[df['target'] == "NEGATIVE"]
    index2 = np.random.randint(len(data0), size=percent * (len(df) - len(data1) - len(data0)))
    lower_data2 = data0.iloc[list(index2)]
    df = pd.concat([data1, lower_data2, data_1])
    return df

df = lower_sample_data(df)
target_cnt = Counter(df.target)
print(target_cnt)

# df.to_csv("F:\VU\The_Social_Web/balanced_twitter1600000.csv", index=False)