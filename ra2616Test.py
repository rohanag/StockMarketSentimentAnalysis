from __future__ import division
from math import log
import sys
import json
import re
import porter
stemmer = porter.PorterStemmer()

def tokenizer(words):
    words = words.replace('\'','').replace(',','').replace('.','')
    temp = re.split("\s|(?<!\d)[^\w']+|[^\w']+(?!\d)", words.lower())
    return [stemmer.stem(i) for i in temp]

modelFile = 'model.json'

def getSentiment(test):
    n = 1
    test = [test]
    #test = ['so bad, so sad, its a sad sad situation and its getting more and more absurd; ; ']
    #test = ['so good, so happy, its a sad and bad situation and its getting more and more wonderful; ; ']

    with open(modelFile, 'r') as fp: 
        prob,sorted_features = json.load(fp)

    num_features = len(prob)
    y_pred = [0 for i in range(n)]
    x = [ [0 for i in range(num_features)] for j in range(n) ]
    for i,data in enumerate(test):
        datarow =  data[1:-1]
        #print datarow.encode('utf-8')
        tokenized = tokenizer(datarow)
        #print tokenized
        for token in tokenized:
            if token in sorted_features:
                x[i][sorted_features.index(token)] = 1
        for j in range(len(tokenized)-1):
            token = ' '.join((tokenized[j], tokenized[j+1]))
            if token in sorted_features:
                x[i][sorted_features.index(token)] = 1
                
    for i in range(n):
        poslikhood = 0
        neglikhood = 0
        for j in range(num_features):
            if x[i][j] == 1:
                poslikhood += log(prob[j][1])
                neglikhood += log(prob[j][0])
            if x[i][j] == 0:
                poslikhood += log( 1 - prob[j][1] )
                neglikhood += log( 1 - prob[j][0] )
                
            if poslikhood > neglikhood:
                y_pred[i] = 1
            else:
                y_pred[i] = 0
        #print 'good 1 or bad 0, ', y_pred[i]
        return y_pred[i]
