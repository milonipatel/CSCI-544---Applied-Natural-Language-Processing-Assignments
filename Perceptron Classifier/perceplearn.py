import sys
import string
import math
import os
import glob 
import re
from decimal import *
from collections import OrderedDict

vocabulary = set()

y_td = dict()
y_pn = dict()

temp_pn=dict()
temp_td=dict()

features_v = dict()
features_a = dict()

id_set=set()

regex = re.compile('[%s]' % re.escape(string.punctuation))

#stopwords = ["i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "so", "than", "too", "very", "will", "just", "should", "now","\n","chicago","re","ian"]
stopwords = ["i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "so", "than", "too", "very", "can", "will", "just", "should", "now","\n","chicago","re","ian","espn","blu","blt"]



def isValid(word):
    word.strip()
    word=regex.sub('', word)
    if word.isalpha():
        return True
    return False


def read_file(filepath,flag):
	global vocabulary
	weight_td = dict()
	weight_pn = dict()
	count = dict()

	
	finput =open(filepath,'r')
	lines =finput.readlines()

   
	
	for line in lines:
        
		line=line.strip("\n")
		line=line.replace("'","")
		line=line.replace("-","")
        
		line=regex.sub('',line)
			
		line=line.lower()
		line=line.split(" ")

		for i in range(0,len(line)):
			if line[i] != '' and line[i] not in stopwords and isValid(line[i]):
				vocabulary.add(line[i])
				if line[i] in count.keys():
					count[line[i]] += 1
				else:
					count[line[i]] = 1

		if flag=='vanilla':
			features_v[filepath] = count

		if flag=='averaged':
			features_a[filepath] = count
			
				
	if flag=='averaged':
		for word in vocabulary:
			weight_td[word] = float(0)
			weight_pn[word] = float(0)
			temp_td[word] = float(0)
			temp_pn[word] = float(0)
			
	if flag=='vanilla':
		for word in vocabulary:
			weight_td[word] = float(0)
			weight_pn[word] = float(0)
	
    
	return weight_td, weight_pn		




def vanilla_model(weight_td,weight_pn):
 
    bias_td = 0
    bias_pn = 0

    for i in range(0,100):

        for docid in features_v:
            feature = features_v[docid]

            a_td = 0
            a_pn = 0

            for val, freq in feature.items():
            	if val in weight_td:
            		a_td = a_td + (weight_td[val] * freq)
            
            	if val in weight_pn:
            		a_pn = a_pn + (weight_pn[val] * freq)
            	
            a_td = a_td + bias_td
            a_pn = a_pn + bias_pn

            if (y_td[docid] * a_td) <= 0:
                for val, freq in feature.items():
                    weight_td[val] = weight_td[val] + (freq * y_td[docid])

                bias_td = bias_td + y_td[docid]

            if (y_pn[docid] * a_pn) <= 0:
                for val, freq in feature.items():
                    weight_pn[val] = weight_pn[val] + (freq * y_pn[docid])

                bias_pn = bias_pn + y_pn[docid]

    return bias_td, bias_pn, weight_td, weight_pn



def average_model(weight_td, weight_pn):

    m = 1
    bias_td = 0
    bias_pn = 0
    mbias_td = 0
    mbias_pn = 0


    for i in range(0,100):

        for docid in sorted(features_a):
            feature = features_a[docid]

            a_td = 0
            a_pn = 0

            for val, freq in feature.items():
            	if val in weight_td:
            		a_td = a_td + (weight_td[val] * freq)
                
                if val in weight_pn:
                	a_pn = a_pn + (weight_pn[val] * freq)

            a_td = a_td + bias_td
            a_pn = a_pn + bias_pn

            if (y_td[docid] * a_td) <= 0:
                for val, freq in feature.items():
                    weight_td[val] += (freq * y_td[docid])
                    temp_td[val] += (m * freq * y_td[docid])

                bias_td = bias_td + y_td[docid]
                mbias_td = mbias_td + (y_td[docid] * m)

            if (y_pn[docid] * a_pn) <= 0:
            	
                for val, freq in feature.items():
                    weight_pn[val] += (freq * y_pn[docid])
                    temp_pn[val] += (m * freq * y_pn[docid])

                bias_pn = bias_pn + y_pn[docid]
                mbias_pn = mbias_pn + (y_pn[docid] * m)

            m = m + 1

    for w in weight_td:
        weight_td[w] = weight_td[w] - float(temp_td[w]) / m

    for w in weight_pn:
        weight_pn[w] = weight_pn[w] - float(temp_pn[w]) / m

    bias_td = bias_td - float(mbias_td) / m
    bias_pn = bias_pn - float(mbias_pn) / m

    return bias_td, bias_pn, weight_td, weight_pn
    


def learn():

	all_files = glob.glob(os.path.join(sys.argv[1], '*/*/*/*.txt'))

	weight_td_v = dict()
	weight_pn_v = dict()
	weight_td_a = dict()
	weight_pn_a = dict()


	for f in all_files:
		
		label_a, label_b, fold, fname = f.split('/')[-4:]
		
		id_set.add(f)
		
		label_b=label_b.split('_')

		if label_a=='positive_polarity' and label_b[0]=='deceptive':
	
			y_td[f] = -1
			y_pn[f] = 1

			weight_td11, weight_pn11=read_file(f,'vanilla')
			weight_td12, weight_pn12=read_file(f,'averaged')

			weight_td_v.update(weight_td11)
			weight_pn_v.update(weight_pn11)
			weight_td_a.update(weight_td12)
			weight_pn_a.update(weight_pn12)

		
		if label_a=='positive_polarity' and label_b[0]=='truthful':

			
			y_td[f] = 1
			y_pn[f] = 1


			weight_td11, weight_pn11=read_file(f,'vanilla')
			weight_td12, weight_pn12=read_file(f,'averaged')

			weight_td_v.update(weight_td11)
			weight_pn_v.update(weight_pn11)
			weight_td_a.update(weight_td12)
			weight_pn_a.update(weight_pn12)

		
		if label_a=='negative_polarity' and label_b[0]=='deceptive':
			
			
			y_td[f] = -1
			y_pn[f] = -1

			weight_f11, weight_p11=read_file(f,'vanilla')
			weight_f12, weight_p12=read_file(f,'averaged')

			weight_td_v.update(weight_f11)
			weight_pn_v.update(weight_p11)
			weight_td_a.update(weight_f12)
			weight_pn_a.update(weight_p12)


		if label_a=='negative_polarity' and label_b[0]=='truthful':
			y_td[f] = 1
			y_pn[f] = -1


			weight_td11, weight_pn11=read_file(f,'vanilla')
			weight_td12, weight_pn12=read_file(f,'averaged')

			weight_td_v.update(weight_td11)
			weight_pn_v.update(weight_pn11)
			weight_td_a.update(weight_td12)
			weight_pn_a.update(weight_pn12)


	bias_td, bias_pn, weight_td, weight_pn = vanilla_model(weight_td_v,weight_pn_v)
	fv = open('vanillamodel.txt', 'w+')
	fv.write("bias_td_vanilla "+"%s\n" % bias_td)
	fv.write("bias_pn_vanilla "+"%s\n" % bias_pn)

	for word in vocabulary:

		fv.write( "weight_td :: " + word + " ::" +  " %f \n" % (weight_td[word]))
		fv.write( "weight_pn :: " + word + " ::" +  " %f \n" % (weight_pn[word]))
		
	fv.close()
	
	bias_td1, bias_pn1, weight_td1, weight_pn1 = average_model(weight_td_a, weight_pn_a)

	fa = open('averagedmodel.txt', 'w+')
	fa.write("bias_td_averaged "+"%s\n" % bias_td1)
	fa.write("bias_pn_averaged "+"%s\n" % bias_pn1)

	for word in vocabulary:
		fa.write( "weight_td :: " + word + " ::" +  " %f \n" % (weight_td1[word]))
		fa.write( "weight_pn :: " + word + " ::" +  " %f \n" % (weight_pn1[word]))
	fa.close()	
	


	
def main():
    learn()

if __name__ == '__main__':
    main()