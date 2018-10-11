import pandas as pd
import numpy as np
import re
import csv

with open('twoColumns.csv', 'w', newline='\n') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',')
    spamwriter.writerow(['term1', 'term2', 'value'])
    df = pd.read_csv('OriginalLemmatizedRel.csv', sep=',', header=None, names=range(1294))
    for row in df.iterrows():
        terms = row[1]
        #print(terms[0])
        for term in terms[1:]:
            if(not type(term) is float):
                relationLen = int(term[term.find("[")+1:term.find("]")])
                term = re.sub("\[.*\]","",term)
                spamwriter.writerow([terms[0], term, relationLen])
                #print(terms[0],"->",term, " - ", relationLen)        
            else:
                break;

