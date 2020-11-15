import math
import re

def compute_cosine(text_a, text_b):
    # look for words and their frequency
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
        print(sim)
        link = max(sim, key=sim.get)
        return link
    except:
        exc = "invalid text HTML"
        return exc

text1 = "Vrije University Amsterdam AID/HIV"
text2 = "Vrije University Amsterdam Hospital I love it when an author can bring you into their made up world and make"
text3 = "Vrije University"
text4 = "I love it when an author can bring you into their made up world and make you feel like a friend, confidant, or family. Having a special child of my own I could relate to the teacher and her madcap class. I've also spent time in similar classrooms and enjoyed the uniqueness of each and every child. Her story drew me into their world and had me laughing so hard my family thought I had lost my mind, so I shared the passage so they could laugh with me. Read this book if you enjoy a book with strong women, you won't regret it."

en_dict = [["123",text2],["456",text3],["789",text4]]
print(similarity(text1,en_dict))

out = re.split(' |/',text1)
print(out)