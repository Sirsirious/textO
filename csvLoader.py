import pandas as pd
import csv

df = pd.read_csv('OriginalLemmatizedRel.csv',sep="\n",header=None)
maxlen = 0
for row in df[0].values:
    listOfTerms = [x for x in row.split(',')]
    maxlen = len(listOfTerms) if len(listOfTerms) > maxlen else maxlen
print (maxlen)

with open('fixedLenght.csv', 'w', newline='') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',')
    for row in df[0].values:
        listOfTerms = [x for x in row.split(',')]
        leftLen = len(listOfTerms) - maxlen
        for x in range(0, leftLen):
            row+=", "
        spamwriter.writerow([row])
    
