from dicio import Dicio
import json
dicio = Dicio()
with open('data/SupportingStructures/completedict.json', 'r') as file:
        dicioDict = json.load(file)
def getRoot(word):
    diciosearch = dicio.search(word)
    if diciosearch is not None:
        if(diciosearch.findRoot() == ""):
            return word
        return diciosearch.findRoot()
    else:
        return word
    
def getDictEntry(word, dictionary): 
    dicio = Dicio()
    test = word.split(" ")
    if(len(test) > 1):
        return
    w = dicio.search(word)
    if not(w is None):
        d = dict()
        d[word] = dict()
        d[word]['root']=w.root
        if(d[word]['root'] == ""):
            d[word]['root'] = word
        d[word]['pos']=w.pos
        d[word]['synonyms']= [s.word for s in w.synonyms]
        dictionary.update(d)
    else:
        d = dict()
        d[word] = dict()
        d[word]['root'] = word
        d[word]['pos'] = ['NOUN']
        d[word]['synonyms'] = []
        dictionary.update(d)

def dicioDef(token):
    word = token[0].lower()
    pos = token[1]
    if not (dicioDict is None):
        if word in dicioDict:
            dicioDict[word]['word']=word
            return dicioDict[word]
    dicio = Dicio()
    d = dict()
    if(pos == ""):
        w = dicio.search(word)
    else:
        w = dicio.search(word, pos)
    if not(w is None):
        d['word']=word
        d['root']=w.root
        if(d['root'] == ""):
            d['root'] = word
        d['pos']=w.pos
        d['synonyms']= [s.word for s in w.synonyms]
    else:
        d['word'] = word
        d['root'] = word
        d['pos'] = ['NOUN']
        d['synonyms'] = []
    return d