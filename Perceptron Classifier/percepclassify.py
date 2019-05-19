import sys
from decimal import *
import string
import collections
import os
import glob 
import re


stopwords = ["i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they","them", "their", "theirs", "themselves", "what", "which", "who", "whom", "this", "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "why", "how", "all", "any", "both", "each", "few", "more", "other", "such", "only", "own", "same", "so", "than", "too", "very", "will", "just", "should", "now", 'for', 'had', 'and', 'to', 'a', 'was', 'in', 'of', 'is', 'it', 'at', 'with', 'they', 'on', 'our', 'be', 'as', 'there', 'an', 'or', 'this', 'that',"\n","chicago","off","before","further","then","during","once","here","ll","ve","espn","blu","blt"]

bias_td=float(0)
bias_pn=float(0)


regex = re.compile('[%s]' % re.escape(string.punctuation))


def isValid(word):
    word.strip()
    word=regex.sub('', word)
    if word.isalpha():
        return True
    return False


def model():
    weight_td = dict()
    weight_pn = dict()
    fmodel = open(sys.argv[1], 'r')
    fread = fmodel.read()
    lines = fread.splitlines()
    m=lines[0].split(' ')
    n=lines[1].split(' ')
    bias_td = float(m[1])
    bias_pn = float(n[1])

    for line in lines[3:]:
        line = line.split(" :: ")
  
        if line[0] == "weight_td":
            weight_td[line[1]] = float(line[2])
        if line[0] == "weight_pn":
            weight_pn[line[1]] = float(line[2])

    return weight_td, weight_pn


def classify_vanilla():
    weight_td, weight_pn = model()
    
    all_files = glob.glob(os.path.join(sys.argv[2], '*/*/*/*.txt'))
    f_vanilla = open("percepoutput.txt", 'w+')
    for f in all_files:
        finput =open(f,'r')
        lines =finput.readlines()
        tempd = dict()
        
        for line in lines:
            line = line.replace("'", '')
            line = line.replace('-', '')
            line = line.strip("\n")
            line=regex.sub(' ',line)

            line = line.split(" ")
            
            docid = f
            list_temp = list()
           
            for i in range(0,len(line)):
                line[i]=line[i].lower()
                if line[i] != '' and line[i] not in stopwords and isValid(line[i]):
                    list_temp.append(line[i])
                    tempd[docid] = list_temp
        for doc, val in sorted(tempd.items()):
            cnt = dict()
            for word in val:
                if word in cnt.keys():
                    cnt[word] += 1
                else:
                    cnt[word] = 1
            td = 0
            pn = 0
            for word, freq in cnt.items():
                if word in weight_td:
                    td += weight_td[word] * freq
                if word in weight_pn:
                    pn += weight_pn[word] * freq
            td += bias_td
            pn += bias_pn
            if td > 0:
                t1 = 'truthful'
            else:
                t1 = 'deceptive'
            if pn > 0:
                t2 = 'positive'
            else:
                t2 = 'negative'
            f_vanilla.write(t1 + " " + t2 + " "+doc + "\n")    
                


def classify_average():
    weight_td, weight_pn = model()
  
    all_files = glob.glob(os.path.join(sys.argv[2], '*/*/*/*.txt'))
    f_average = open("percepoutput.txt", 'w+')


    for f in all_files:
        finput =open(f,'r')
        lines =finput.readlines()
        tempd = dict()

        for line in lines:

            line = line.replace("'", '')
            line = line.replace('-', '')
            line = line.strip("\n")
            line=regex.sub(' ',line)

            line = line.split(" ")
            
            docid = f    
            list_temp = list()
            for i in range(0,len(line)):
                line[i]=line[i].lower()
                if line[i] != '' and line[i] not in stopwords and isValid(line[i]):
                    list_temp.append(line[i])
                    tempd[docid] = list_temp

        for doc, val in sorted(tempd.items()):
            cnt = dict()
            for word in val:
                if word in cnt.keys():
                    cnt[word] += 1
                else:
                    cnt[word] = 1
            td = 0
            pn = 0
            for word, freq in cnt.items():
                if word in weight_td:
                    td += weight_td[word] * freq
                if word in weight_pn:
                    pn += weight_pn[word] * freq
            td += bias_td
            pn += bias_pn
            if td > 0:
                t1 = 'truthful'
            else:
                t1 = 'deceptive'
            if pn > 0:
                t2 = 'positive'
            else:
                t2 = 'negative'

            f_average.write(t1 + " " + t2 + " " + doc + " " + "\n")    


def main():
    if sys.argv[1] == 'vanillamodel.txt':
        classify_vanilla()

    if sys.argv[1] == 'averagedmodel.txt':
        classify_average()


if __name__ == '__main__':
    main()