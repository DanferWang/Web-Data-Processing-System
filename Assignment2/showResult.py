import math
import re
import datetime
import time


def compute_cosine(text_a, text_b):
    # find word
    words1 = text_a.split(' ')
    words2 = text_b.split(' ')
    
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

    dic1 = sorted(words1_dict.items(), key=lambda asd: asd[1], reverse=True)
    dic2 = sorted(words2_dict.items(), key=lambda asd: asd[1], reverse=True)

    # word vector
    words_key = []
    for i in range(len(dic1)):
        words_key.append(dic1[i][0])
    for i in range(len(dic2)):
        if dic2[i][0] in words_key:
            
            pass
        else:  # combine
            words_key.append(dic2[i][0])
    # print(words_key)
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
    

    # compute cosine similarity
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



import pandas as pd
data = pd.read_csv("/content/drive/My Drive/Colab Notebooks/prediction_test3.csv")

# group according bookid
means = data.groupby(data['bookid'])
s=0
y=0
aa=[]
bb=[]
cc=[]

# for every bookid
for i in means:

    # compute similarity of two names
    for j in range(0+y,len(i[1])+y):
        score=0
        for k in range(0+y,len(i[1])+y):
            #print(i[1]['entity'][k])
            if len(i[1]['entity'][k])>len(i[1]['entity'][j]):
                score=compute_cosine(i[1]['entity'][k],i[1]['entity'][j])
                if score>0.65:
                    i[1]['entity'][j]=i[1]['entity'][k]
        
        
        aa.append(i[1]['entity'][j])
        bb.append(i[1]['bookid'][j])
        cc.append(i[1]['score'][j])
    y=len(i[1])+y


dataframe = pd.DataFrame({'bookid':bb,'entity':aa,'score':cc})


dataframe.to_csv("/content/drive/My Drive/Colab Notebooks/temp3.csv",index=False,sep=',')

# compute mean score of every entity
data = pd.read_csv("/content/drive/My Drive/Colab Notebooks/temp3.csv")
means = data.groupby([data['bookid'], data['entity']]).mean()
means.to_csv("/content/drive/My Drive/Colab Notebooks/result3.csv",sep=',')
