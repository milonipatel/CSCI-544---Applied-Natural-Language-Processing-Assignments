import sys

import codecs

tags = set()
wordSet = set()
transitionProbability = dict()
emissionProbability = dict()
tagList = list()
tagsCount =dict()

def readModel():

    global transitionProbability
    global emissionProbability
    global tagList
    global tagsCount
    global tags
    
    finput = codecs.open("hmmmodel.txt",'r', encoding="utf-8")
    lines = finput.readlines()
    temp = "transition"
    for index,line in enumerate(lines):
        line = line.strip('\n')
        if index >= 1:
            if line != "********Emission Probability********":
                if temp == "emission":
                    putdata("emission",line)
                else:
                    putdata("transition",line)
            else:
                temp="emission"
                continue
                 
    finput.close() 




def putdata(flag,line):
    _tagi = line[:-line[::-1].find("|")-1]

    if flag=="transition":

        transitionProbability[_tagi] = line.split("|")[-1]
        _word=_tagi.split("*WordTag*")
        _word=_word[0]
        if (_word not in tagList) and (_word != "q0"):
            key_split=_tagi.split("*WordTag*")
            key_split=key_split[0]
            tagList.append(key_split)

    if flag=="emission":
        emissionProbability[_tagi] = line.split("|")[-1]
        _tagk = line[:-line[::-1].find("|") - 1]
        word = _tagi[:-_tagi[::-1].find("/")-1]
        word=word.lower()
        wordSet.add(word)
        if _tagk.split("/")[-1] not in tagsCount:
            tagsCount[_tagk.split("/")[-1]] =1
        else:    
            tagsCount[_tagk.split("/")[-1]] += 1
        tags.add(_tagk.split("/")[-1])    





def viterbiAlgo(line):
    latestProbability = dict()
    global tagList
    global transitionProbability
    global emissionProbability
    global tagsCount
    global wordSet
    global tags


    words = line.rstrip("\n").split(" ")
    
    for tag in tagList:
        transitionpro = float(0)
        emissionpro = float(0)
        startTag="q0*WordTag*"+tag
        if transitionProbability.has_key(startTag):
            transitionpro = float(transitionProbability[startTag])
        words[0]=words[0].lower()
        if words[0] in wordSet:
            _tag=words[0]+"/"+tag
            if emissionProbability.has_key(_tag):
                emissionpro = float(emissionProbability[_tag])
                latestProbability[tag] = transitionpro * emissionpro
        else:
            denom=tagsCount[tag] +len(wordSet)
            emissionpro = float(float(1) /denom)
            latestProbability[tag] = transitionpro

    if len(words) > 1:
        for i in range(1, len(words)):
            prevProbability = latestProbability
            latestProbability = dict()
            locals()['dict{}'.format(i)] = {}
            prevTag = ""
            for tag in tagList:
                words[i]=words[i].lower()

                if words[i] in wordSet:
                    _tagged=words[i]+"/"+tag
                    if emissionProbability.has_key(_tagged):
                        emissionpro = float(emissionProbability[_tagged])
                        maxProbVal=float(0)
                        maxProbVal, precedingState = max((float(prevProbability[prevTag]) * float(transitionProbability[prevTag + "*WordTag*" + tag]) * emissionpro, prevTag) for prevTag in prevProbability)
                        latestProbability[tag] = maxProbVal
                        transition=precedingState + "*" + tag
                        locals()['dict{}'.format(i)][transition] = maxProbVal
                        prevTag = precedingState
                else:
                    denom=tagsCount[tag] +len(wordSet)
                    emissionpro = float(float(1) /denom)
                    maxProbVal=float(0)

                    maxProbVal, precedingState = max((float(prevProbability[prevTag]) * float(transitionProbability[prevTag + "*WordTag*" + tag]) *emissionpro, prevTag) for prevTag in prevProbability)

                    latestProbability[tag] = maxProbVal
                    transition=precedingState + "*" + tag
                    locals()['dict{}'.format(i)][transition] = maxProbVal
                    prevTag = precedingState

            if i == len(words)-1:
                endTag = max(latestProbability,key=latestProbability.get)
                maxVal = ""
                maxVal = maxVal + endTag + " " + prevTag
                for j in range(len(words)-1,0,-1):
                    for key in locals()['dict{}'.format(j)]:
                        data = key.split("*")
                        if data[-1] == prevTag:
                            prevTag = data[0]
                            maxVal = maxVal + " " +prevTag
                            
                            break
                result = maxVal.split()
                result.reverse()
                return " ".join(result)
    else:
        maxVal = max(latestProbability,key=latestProbability.get)
        return maxVal
 



def main():
    readModel()

    finput = codecs.open(sys.argv[1], 'r', encoding="utf-8")
    foutput = codecs.open("hmmoutput.txt",'w',encoding="utf-8")
    for line in finput.readlines():
        pathViterbi = viterbiAlgo(line)
 
        word = line.strip("\n").split(" ")
        tag = pathViterbi.split(" ")
        for i in range(0,len(word)):
            foutput.write(word[i] + "/" + tag[i])
            if i !=len(word)-1:
                foutput.write(" ")
            else:
                foutput.write(u'\n')
                



if __name__ == '__main__':
    main()