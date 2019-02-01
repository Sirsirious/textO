import spacy
from spacy.lemmatizer import Lemmatizer
from spacy.lang.en import LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES
lemmatizer = Lemmatizer(LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES)
import math
##
def get_doc(sentdf, lang):
    """
    This function returns the doc statistics with term count.
    
    sentdf: a Pandas Dataframe with a sentence per row, with the sentence in the second column.
    lang: the language of the sentence, if supported by Spacy, the underlying tech. Else, english will be used.
    """
    doc_info = []
    for i, row in sentdf.iterrows():
        text = row[1]
        count = count_words(text, lang)
        values = {'doc_id' : i, 'doc_length':count}
        doc_info.append(values)
    return doc_info
##
def count_words(sent, lang):
    """
    Returns the total number of words in a sentence
    
    sent: a sentence represented by a String
    lang: the language of the sentence, if supported by Spacy, the underlying tech. Else, english will be used.
    """
    nlp = spacy.load(lang)
    return len(nlp(sent))

##

def create_freq_dict(sentdf, lang, lemmatize=True):
    """
    Returns the frequency dictionary for all terms in the sentence. This function ignores punctuations, stopwords and non alphanumeric terms. It can also lemmatize every word by default, if the flag is not off.
    
    sentdf: a Pandas Dataframe with a sentence per row, with the sentence in the second column. 
    lang: the language of the sentence, if supported by Spacy, the underlying tech. Else, english will be used.
    lemmatize: tells if every word is to be lemmatized - this can significantly reduce the final wordlist size, but increase processing time. Its on by default.
    """
    nlp = spacy.load(lang)
    freqDict_list = []
    for i, row in sentdf.iterrows():
        text = row[1]
        freq_dict = {}
        words = nlp(text)
        words = [token for token in words if not (token.is_punct or not token.is_alpha or token.is_stop)]
        for token in words:
            if lemmatize:
                word = lemmatizer(token.orth_, token.pos_)[0]
            else:
                word = token
            if word in freq_dict:
                freq_dict[word]+=1
            else:
                freq_dict[word]=1
            temp = {'doc_id' : i, 'freq_dict' : freq_dict}
        freqDict_list.append(temp)
    return freqDict_list
##
def computeTF(doc_info, freqDict_list):
    """
    A function to compute the Term Frequency for every term in a document, given that a frequencyDictionary list is passed, as well as the document own info.
    Retuns a dictionary with the doc_id, the TF_score and a key, for each word.
    
    doc_info: A Dictionary item with the document ID and the Document Length.
    freqDict_list: a list of Frequency Dictionaries with the words and its frequencies.
    """
    
    TF_scores = []
    for tempDict in freqDict_list:
        docid = tempDict['doc_id']
        for k in tempDict['freq_dict']:
            temp = {'doc_id' : docid, 'TF_score' : tempDict['freq_dict'][k]/doc_info[docid-1]['doc_length'], 'key' : k}
            TF_scores.append(temp)
    return TF_scores
##

def computeIDF(doc_info, freqDict_list):
    """
    Computes the Inverse Document Frequency for every term and document in the corpus.
    Retuns a dictionary with the doc_id, the IDF_score and a key, for each word/document.
    
    doc_info: A Dictionary item with the document ID and the Document Length.
    freqDict_list: a list of Frequency Dictionaries with the words and its frequencies.
    """
    IDF_scores=[]
    counter = 0
    for dic in freqDict_list:
        counter +=1
        for k in dic['freq_dict'].keys():
            count = sum([k in tempDict['freq_dict'] for tempDict in freqDict_list])
            temp = {'doc_id' : counter, 'IDF_score':math.log(len(doc_info)/count), 'key': k}
            
            IDF_scores.append(temp)
    return IDF_scores
##
def computeTFIDF(TF_scores, IDF_scores):
    """
    Computes the Term Frequency times the Inverse Document Frequency for each Term in the corpus.
    Returns a dict with the Doc_id, the TFIDF_score and key, for each term/document.

    TF_scores: a dictionary for every term frequency.
    IDF_scores: a dictionary for every term inverse document frequency.
    """
    TFIDF_scores = []
    for j in IDF_scores:
        for i in TF_scores:
            if j['key']==i['key'] and j['doc_id']==i['doc_id']:
                temp = {'doc_id' : j['doc_id'],
                       'TFIDF_score' : j['IDF_score']*i['TF_score'],
                       'key': i['key']}
            else:
                continue
            TFIDF_scores.append(temp)
    return TFIDF_scores
##
def getTopTerms(corpus, numterms, lang, lemmatize=True):
    """
    Returns a list of the n top terms found in the corpus, extracted using a TF-IDF methodology and removing puncts and stopwords.

    corpus: a pandas dataframe with one sentence per line, at the position 1.
    numterms: the number of top terms to retrieve
    lang: the language of the sentence, if supported by Spacy, the underlying tech. Else, english will be used.
    lemmatize: tells if every word is to be lemmatized - this can significantly reduce the final wordlist size, but increase processing time. Its on by default.
        
    """
    doc_info = get_doc(corpus, lang)
    freqDict_list = create_freq_dict(corpus, lang, lemmatize)
    TF_scores = computeTF(doc_info, freqDict_list)
    IDF_scores = computeIDF(doc_info, freqDict_list)
    TFIDF_scores = computeTFIDF(TF_scores, IDF_scores)
    sortedList = sorted(TFIDF_scores, key=lambda k: k['TFIDF_score'], reverse=True)
    if numterms < len(sortedList):
        s = slice(0, numterms)
    else:
        s = slice(0, len(sortedList))
    
    return [entry['key'] for entry in sortedList[s]]


