import sys
import math
from decimal import *
import codecs

tagList = set()
tagCount = dict()
wordSet = set()
wordTags = list()
dictCount = dict()
transitionModel = dict()
wordCount = dict()
emissionModel = dict()


def readData():
    global wordTags
    finput = codecs.open(sys.argv[1], 'r', encoding="utf-8")
    lines = finput.readlines()
    for line in lines:
        data = line.strip('\n').split(" ")
        wordTags.append(data)
    finput.close()
    return wordTags
 


def transition_probability():
    global transitionModel
    global tagList
    global wordSet
    
    global dictCount
    global tagCount
    trainingData = readData()
    for value in trainingData:

        previous = "q0"
        for data in value:

            word = data[:-data[::-1].find("/") - 1]
            data = data.split("/")
            tag=data[-1]
            wordSet.add(word.lower())
            tagList.add(tag)

            if tagCount.has_key(tag):
                tagCount[tag] += 1
            else:
                tagCount[tag] = 1
            _prevTag=previous + "*WordTag*" + tag  
            if dictCount.has_key(_prevTag):

                dictCount[_prevTag] += 1
                previous = tag
            else:
                dictCount[_prevTag] = 1
                previous = tag
                
    print(len(wordSet))
    print(len(tagList))
    for key in dictCount:
        x = 0
        val = key.split("*WordTag*")
        val=val[0]
        for key1 in dictCount:
            _key0=key1.split("*WordTag*")
            _key0=_key0[0]
            if _key0 == val:
                x = x + dictCount[key1]
        transitionModel[key] = float(float(dictCount[key])/(x))
    for tag in tagList:
        _start="q0" + "*WordTag*" + tag
        if _start not in  transitionModel:
            transitionModel[_start] = float(float(1) / float(len(wordSet) + tagCount[tag]))
    for _firstTag in tagList:
        for _secondTag in tagList:
            transition=_firstTag +"*WordTag*" + _secondTag
            if transition not in transitionModel:
                transitionModel[transition] = float(float(1)/float(len(wordSet) + tagCount[_firstTag]))

 

def emission_probability():
   
    global tagCount
    trainingData = readData()
    global wordCount
    for value in trainingData:
        for data in value:

            word = data[:-data[::-1].find("/") - 1]
            tag = data.split("/")[-1]

            word=word.lower()
            _wordTag=word + "/" + tag
            if wordCount.has_key(_wordTag):
                wordCount[_wordTag] +=1
            else:
                wordCount[_wordTag] = 1
   
    global emissionModel
    for key in wordCount:
        emissionModel[key] = float(float(wordCount[key])/tagCount[key.split("/")[-1]])


def main():
   
    transition_probability()
    #print tagList
    emission_probability()

    foutput = codecs.open("hmmmodel.txt", 'w', encoding="utf-8")
    foutput.write(u'********Transiton Probability********\n')
    for key in transitionModel.keys():
        foutput.write('%s|%s\n' % (key,transitionModel[key]))


    foutput.write(u'********Emission Probability********\n')
    for key in emissionModel.keys():
        foutput.write('%s|%s\n' % (key,emissionModel[key]))


if __name__ == '__main__':
    main()