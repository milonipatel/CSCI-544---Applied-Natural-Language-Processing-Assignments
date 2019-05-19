import sys
import string
import math
import os
import glob 
import re
from decimal import *

vocabulary = set()

positivedecep_count = dict()
negativedecep_count = dict()
positivetrue_count = dict()
negativetrue_count = dict()
pd_cnt=float(0)
nd_cnt=float(0)
pt_cnt=float(0)
nt_cnt=float(0)
           

prior_positivedecep=float(0.0)
prior_negativedecep=float(0.0)
prior_positivetrue=float(0.0)
prior_negative=float(0.0)
 

positivedecep_set = set()
negativedecep_set = set()
positivetrue_set = set()
negativetrue_set = set()
id_set=set()

regex = re.compile('[%s]' % re.escape(string.punctuation))


def isValid(word):
    word.strip()
    word=regex.sub('', word)
    if word.isalpha():
        return True
    return False
    
    

def read_file(filepath,flag):
	finput =open(filepath,'r')
	lines =finput.readlines()
	for line in lines:
        
		
		line=line.replace("'","")
		line=line.replace("-","")
        
		line=regex.sub('',line)
			

		line=line.lower()
		line=line.split(" ")
        
        
		if flag == 0:
			for i in range(0, len(line)):
				if isValid(line[i]):
					vocabulary.add(line[i])
					global pd_cnt
					
					if line[i] in positivedecep_count.keys():
						positivedecep_count[line[i]] +=1
						pd_cnt+=1
						
					else:
						positivedecep_count[line[i]] =1
						

		if flag ==1:
			for i in range(0,len(line)):
				if isValid(line[i]):
					vocabulary.add(line[i])
					global pt_cnt
					
					if line[i] in positivetrue_count.keys():

						positivetrue_count[line[i]] +=1
						pt_cnt+=1
						
					else:
						positivetrue_count[line[i]] =1
					

		if flag == 2:
			for i in range(0,len(line)):
				if isValid(line[i]):
					vocabulary.add(line[i])
        			global nd_cnt
        			
        			if line[i] in negativedecep_count.keys():
        				negativedecep_count[line[i]] +=1
        				nd_cnt+=1
        				
        			else:
        				negativedecep_count[line[i]] =1
        				

        if flag == 3:
        	for i in range(0,len(line)):
        		if isValid(line[i]):
        			vocabulary.add(line[i])
        			global nt_cnt
        			
        			if line[i] in negativetrue_count.keys():
        				negativetrue_count[line[i]] +=1
        				nt_cnt+=1
        			
        			else:

        				negativetrue_count[line[i]] =1
        				


def learn():

	all_files = glob.glob(os.path.join(sys.argv[1], '*/*/*/*.txt'))
	
	for f in all_files:
		
		label_a, label_b, fold, fname = f.split('/')[-4:]
		
		id_set.add(f)
		
		label_b=label_b.split('_')
		
		if label_a=='positive_polarity' and label_b[0]=='deceptive':
			read_file(f,0)
			positivedecep_set.add(f)

		
		if label_a=='positive_polarity' and label_b[0]=='truthful':
			read_file(f,1)
			positivetrue_set.add(f)

		
		if label_a=='negative_polarity' and label_b[0]=='deceptive':
			read_file(f,2)
			negativedecep_set.add(f)
		if label_a=='negative_polarity' and label_b[0]=='truthful':
			read_file(f,3)
			negativetrue_set.add(f)
		

	

	fout = open('nbmodel.txt', 'w+')

	

	prior_positivedecep= float(len(positivedecep_set))/float(len(id_set))
	prior_negativedecep=float(len(negativedecep_set))/float(len(id_set))
	prior_positivetrue=float(len(positivetrue_set))/float(len(id_set))
	prior_negativetrue=float(len(negativetrue_set))/float(len(id_set))
 
	
	fout.write("%f\n" % prior_positivedecep)
	fout.write("%f\n" % prior_negativedecep)
	fout.write("%f\n" % prior_positivetrue)
	fout.write("%f\n" % prior_negativetrue)

	
	for word in vocabulary:
		if word in positivedecep_count.keys():
			prob=math.log(positivedecep_count[word] + 1) -math.log( Decimal(pd_cnt + len(vocabulary)))

		else:

			prob = math.log(1)-math.log(Decimal(pd_cnt + len(vocabulary)))
			
		fout.write("deceptive_positive :: " + word + " :: %f\n" % prob)

		if word in negativedecep_count.keys():
  
			prob=math.log(negativedecep_count[word] + 1) - math.log(Decimal(nd_cnt + len(vocabulary)))

		else:
                           
			prob = math.log(1)-math.log(Decimal(nd_cnt + len(vocabulary)))
			
		fout.write("deceptive_negative :: " + word + " :: %f\n" % prob)

		if word in positivetrue_count.keys():
			
			prob=math.log(positivetrue_count[word] + 1) - math.log(Decimal(pt_cnt + len(vocabulary)))
		else:
			prob = math.log(1)-math.log(Decimal(pt_cnt + len(vocabulary)))
                                      
			
		fout.write("truthful_positive :: " + word + " :: %f\n" % prob)

		if word in negativetrue_count.keys():
			
			prob=math.log(negativetrue_count[word] + 1)- math.log(Decimal(nt_cnt + len(vocabulary)))
		else:
			prob = math.log(1)-math.log(Decimal(nt_cnt + len(vocabulary)))
                                        
			
		fout.write("truthful_negative :: " + word + " :: %f\n" % prob)


	
def main():
    learn()

if __name__ == '__main__':
    main()