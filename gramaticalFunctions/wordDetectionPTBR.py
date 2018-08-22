import nltk
from nltk.corpus import stopwords

def unusualWords(texto):
    text_vocab = set(w.lower() for w in texto if w.isalpha())
    portuguese_vocab = set(w.lower() for w in nltk.corpus.floresta.words())
    #portuguese_vocab.update(w.lower() for w in nltk.corpus.mac_morpho.words())
    unusual = text_vocab - portuguese_vocab
    return sorted(unusual)

def stripStopWords(texto):
    stop_words = set(stopwords.words('portuguese')) # verif se subtração é melhor ou pior
    text_vocab = set(w.lower() for w in texto if w.isalpha())
    return text_vocab - stop_words

def contentFraction(texto):
    stop_words = set(stopwords.words('portuguese'))
    content = [w for w in texto if w.lower() not in stop_words]
    return len(content)/len(texto)