import pandas as pd
import numpy as np
from collections import Counter

DATASET_ENCODING = "ISO-8859-1"
dataset_path = "F:\VU\Web_Data_Processing_Systems\clean_kindle_reviews.csv"
print("Open file:", dataset_path)
df = pd.read_csv(dataset_path, encoding =DATASET_ENCODING ,lineterminator='\n')
df = df.drop(columns=["Unnamed: 0"])

decode_map = {1: "NEGATIVE", 2: "NEGATIVE", 3: "NEUTRAL", 4: "POSITIVE", 5: "POSITIVE" }
def decode_sentiment(label):
    return decode_map[int(label)]
df.overall = df.overall.apply(lambda x: decode_sentiment(x))

target_cnt = Counter(df.overall)
print(target_cnt)

def lower_sample_data(df, percent=1):
    data1 = df[df['overall'] == "POSITIVE"]
    data0 = df[df['overall'] == "NEUTRAL"]
    data_1 = df[df['overall'] == "NEGATIVE"]
    index1 = np.random.randint(len(data1), size=percent * (len(df) - len(data1) - len(data0)))
    lower_data1 = data1.iloc[list(index1)]
    df = pd.concat([lower_data1, data0, data_1])
    data1 = df[df['overall'] == "POSITIVE"]
    data0 = df[df['overall'] == "NEUTRAL"]
    data_1 = df[df['overall'] == "NEGATIVE"]
    index2 = np.random.randint(len(data0), size=percent * (len(df) - len(data1) - len(data0)))
    lower_data2 = data0.iloc[list(index2)]
    df = pd.concat([data1, lower_data2, data_1])
    return df

df = lower_sample_data(df)
target_cnt = Counter(df.overall)
print(target_cnt)

df.to_csv("F:\VU\Web_Data_Processing_Systems/balanced_kindle_reviews.csv", index=False)