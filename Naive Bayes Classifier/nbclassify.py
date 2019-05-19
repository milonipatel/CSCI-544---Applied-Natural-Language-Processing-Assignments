import sys
import string
from decimal import *
import glob
import os
import collections
import math
import re


stopwords = ["i","me","my","myself","we","our","ours","ourselves","you","your","yours","yourself","yourselves","he","him","his","himself","she","her","hers","herself","it","its","itself","they","them","their","theirs","themselves","what","which","who","whom","this","that","these","those","am","is","are","was","were","be","been","being","have","has","had","having","do","does","did","doing","a","an","the","and","but","if","or","because","as","until","while","of","at","by","for","with","about","against","between","into","through","during","before","after","above","below","to","from","up","down","in","out","on","off","over","under","again","further","then","once","here","there","when","where","why","how","all","any","both","each","few","more","most","other","some","such","no","nor","not","only","own","same","so","than","too","very","s","t","can","will","just","don","should","now","within","think","any","why","things","its","youll","oh","ive","id","wouldnt","saw","say","saying","says","chicago","hotel","bathroom","view","stay","room","location","\n"]

regex = re.compile('[%s]' % re.escape(string.punctuation))

def isValid(word):
    word.strip()
    word=regex.sub('', word)
    if word.isalpha():
        return True
    return False
    
        
        
                        
def read_data():
    positivedecep_dict = dict()
    negativedecep_dict = dict()
    positivetrue_dict = dict()
    negativetrue_dict = dict()

    finput = open('nbmodel.txt','r')
    lines = finput.readlines()
    for index,line in enumerate(lines):
        line = line.strip("\n")
        if index == 0:
            prior_pd = float(line)

        if index == 1:
            prior_nd = float(line)

        if index == 2:
            prior_pt = float(line)

        if index == 3:
            prior_nt = float(line)

        
        line = line.split(" :: ")
        
        if line[0] == 'deceptive_positive':
            #print line[0]
            positivedecep_dict[line[1]] = Decimal(line[2])
        if line[0] == 'deceptive_negative':
            #print line[0]
            negativedecep_dict[line[1]] = Decimal(line[2])
        if line[0] == 'truthful_positive':
            #print line[0]
            positivetrue_dict[line[1]] = Decimal(line[2])
        if line[0] == 'truthful_negative':
            #print line[0]
            negativetrue_dict[line[1]] = Decimal(line[2])

    finput.close()
    return prior_pt, prior_nt, prior_pd, prior_nd, positivedecep_dict, negativedecep_dict, positivetrue_dict, negativetrue_dict


def classify():
    prior_pt, prior_nt, prior_pd, prior_nd, positivedecep_dict, negativedecep_dict, positivetrue_dict, negativetrue_dict = read_data()
   
    
    all_files = glob.glob(os.path.join(sys.argv[1], '*/*/*/*.txt'))
    fout = open("nboutput.txt",'w+')
    #print all_files

    for f in all_files:
        finput =open(f,'r')
        lines =finput.readlines()
        #print f+"\n"
        for line in lines:
            output = ""
            pd_val=math.log(prior_pd)
            nd_val=math.log(prior_nd)
            pt_val=math.log(prior_pt)
            nt_val = math.log(prior_nt)


            
            line = line.replace("'", "")
            line = line.replace("-", "")

            line=regex.sub('',line)
                #line = line.replace(p, '')
            line = line.lower()
            
            line = line.split(" ")

            for i in range(0,len(line)):
                if line[i] not in stopwords and isValid(line[i]):
                    if line[i] in positivedecep_dict:
                        
                        pd_val += float(positivedecep_dict[line[i]])
                    if line[i] in negativedecep_dict:
                        
                        nd_val += float(negativedecep_dict[line[i]])
                    if line[i] in positivetrue_dict:
                        
                        pt_val += float(positivetrue_dict[line[i]])
                    if line[i] in negativetrue_dict:
                        
                        nt_val += float(negativetrue_dict[line[i]])

            
    
    
            if nd_val>nt_val and nd_val>pt_val and nd_val>pd_val:
                output += "deceptive negative "

            if nt_val>nd_val and nt_val>pt_val and nt_val>pd_val:
                output += "truthful negative "

            if pt_val>nd_val and pt_val>nt_val and pt_val>pd_val:
                output+="truthful positive "

            if pd_val>nd_val and pd_val>pt_val and pd_val>nt_val:
                output+="deceptive positive "


            output += f

        fout.write(output + "\n")



def main():
    classify()


if __name__ == '__main__':
    main()