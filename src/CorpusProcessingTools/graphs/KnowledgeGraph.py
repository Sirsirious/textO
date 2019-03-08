import pandas as pd
import spacy, copy, textacy, json, logging, multiprocessing, textacy.keyterms
from dicio import Dicio
from multiprocessing import Pool

class KnowledgeGraph:
    
    def __init__(self, network_dataframe=None, language='pt', dictFilePath = 'data/SupportingStructures/completedict.json'):
        self.nodes = dict()
        if network_dataframe is not None:
            loadDataframe(network_dataframe)
        self.nlp = spacy.load(language)
        self.multiprocessing = True
        if dictFilePath != '':
            with open(dictFilePath, 'r') as file:
                self.dicioDict = json.load(file)
        else:
            self.dicioDict = {}

    def loadDataframe(self, network_dataframe):
        '''
        Loads a graph based on a Dataframe.
        This graph must be described as two columns 'from' and 'to', representing the original node and the destination.
        
        network_dataframe: a dataframe containing columns named 'from' and 'to'
        
        '''
        graph = dict()
        for index, edge in network_dataframe.iterrows():
            if not(edge['from'] in graph):
                graph[edge['from']]={'weight':0, 'documents':dict(), 'edges':[]}
            if not(edge['to'] in graph):
                graph[edge['to']]={'weight':0, 'documents':dict(), 'edges':[]}
            graph[edge['from']]['edges'].append({'term':edge['to'],'weight':0})
        self.nodes= graph

    def getNodeDictionary(self):
        '''
        Returns a set of all nodes in the loaded graph.
        '''
        dictionary = set()
        for edge in self.nodes:
            dictionary.add(edge)
        return dictionary
    
    def addDocument(self, document_id, document_text, normalized = False, allowRepetitions = True, useTFIDF = True):
        '''
        Adds a document to the graph. The algorithm will break the document into its words and will add a 'pointer' to the document id in each activated node.
        document_id: The identifier of the document
        document_text: The document's text
        normalized: If True, the weight of all words in document will be balanced. False by default.
        allowRepetitions: If True, a word that appears twice will have twice the value. True by default.
        useTFIDF: To be implemented.

        '''
        termsInDocument = listOfWords(document_text)
        if allowRepetitions == False:
            termsInDocument = set(termsInDocument)
        toAdd = 1
        if normalized == True:
            toAdd = 1 /len(termsInDocument) if len(termsInDocument) > 0 else 1
        for term in termsInDocument:
            if document_id in self.nodes[term]['documents']:
                self.nodes[term]['documents'][document_id] +=toAdd
            else:
                self.nodes[term]['documents'][document_id] = toAdd

    def addAnswer(self, answer_id, answer_text):
        '''
        Does the same as addDocument. However, it uses Textranked tuples to do the job. The normalization is then given by a third-party algorithm.
        answer_id: The identifier of the document/answer.
        answer_text: The document's/answer's text.
        '''
        words = wordTuples(answer_text)
        for word in words:
            for key, val in word.items():
                    self.nodes[key]['documents'][answer_id] = val
        
    def getMostRanked(self, input_string, listsize = 10, decay = 0.2):
        '''
        Returns a sorted list of the n best ranked documents and its score.
        input_string: the input string which is going to be inserted in the graph in order to generate the list of related documents.
        listsize: the size of the list of answers. Default is 10 or the maximum number of outputs.
        decay: the decay value to be applied to the algorithm. Default is 0.2
        
        '''
        grp = copy.deepcopy(self.nodes)
        grp = activeGraph(_processSent(grp, input_string, decay))
        docvalues = dict()
        for entry in grp:
            for doc in grp[entry]['documents']:
                if doc in docvalues:
                    docvalues[doc] = grp[entry]['weight']*grp[entry]['documents'][doc]+docvalues[doc]
                else:
                    docvalues[doc] = grp[entry]['weight']*grp[entry]['documents'][doc]
        maxsize = len(docvalues.items())
        return sorted(docvalues.items(), key=lambda kv: kv[1], reverse=True)[:min(listsize, maxsize)]

    def isHit(self, input_string, correct_answer, listsize = 10, decay = 0.2, audit = False):
        '''
        Evaluates to True or False based on wheter the input_string causes the system to get the correct answer as the first most ranked. Based of of getMostRanked function.
        input_string: the string used to retrieve the most relevant documents.
        correct_answer: the id of the correct answer.
        listsize: the size of the list of answers. Default is 10 or the maximum number of outputs.
        decay: the decay value to be applied to the algorithm. Default is 0.2
        audit: Prints to the standard output the retrieved output, the expected answer and the comparison between them.
        
        '''
        retrievedAnswers = getMostRanked(input_string, listsize, decay = decay)
        # This gets rid of the score.
        topn = [answer[0] for answer in retrievedAnswers]
        if audit == True and len(topn)>0:
            print(topn, correct_answer, topn[0]==correct_answer)
        if len(topn) > 0 and (topn[0] == correct_answer):
            return True
        elif len(topn) ==0:
            print('Error, no Document found to be compared')
            return False
        else:
            return False

    def isCorrectAnswerInWindow(self, input_string, correctanswer, listsize = 10, decay = 0.2):
        '''
        Evalutes if the correct answer is in the defined window. Used for more general topic detection tests.
        input_string: the string used to retrieve the most relevant documents.
        correct_answer: the id of the correct answer.
        listsize: the window size. Default is 10 or the maximum number of outputs.
        decay: the decay value to be applied to the algorithm. Default is 0.2
        
        '''
        retrievedAnswers = getMostRanked(input_string, listsize, decay)
        topn = [answer[0] for answer in retrievedAnswers]
        if correctanswer in topn:
            return True;
        else:
            return False;

    def _processSent(self, graph, input_string, decay = 0.2):
        '''
        The core entry point for any comparison attempt. It takes in a text entry and finds related documents in graph.
        graph: a graph copy, passed explicitly in order so that one question search does not mess with another one.
        input_string: the string used to retrieve the most relevant documents.
        decay: the decay value to be applied to the algorithm. Default is 0.2
        '''
        if self.multiprocessing:
            mpl = multiprocessing.log_to_stderr()
            mpl.setLevel(logging.ERROR)
        traversedList = set()
        words = listOfWords(graph, input_string)
        for word in words:
            graph[word]['weight']=1
            graph, traversedList = __spread(word, graph, traversedList, previousScore=1, decay=decay)
        return graph

    def __spread(self, word, graph, traversedList, previousScore=1, decay=0.2, treshold=0.1):
        '''
        A recursive implementation of the breadth-first spreading activation algorithm. Given a specific word, it spreads to neighboring nodes, returning a graph and a traversedList (the traversedList is to ensure it stops, since it's recursive).
        word: the node word to be spread into.
        graph: a graph copy in which to calculate spreading.
        traversedList: the list of nodes already traversed.
        previousScore: the score, which is updated each time, at wich nodes will be activated.
        decay: the decay value to be applied to the score. Default is 0.2
        treshold: directly related to decay and default previousScore, it defines when the spreading should stop.
        
        '''
        if graph[word]['weight']==0:
            graph[word]['weight']=previousScore
        futureTraversals = Queue()
        if (previousScore > treshold):
            for i in range(1, len(graph[word]['edges'])-1):
                if graph[word]['edges'][i].get('weight')==0:
                    graph[word]['edges'][i].update({'weight':previousScore})
                graph[word]['edges'][i].update({'weight':graph[word]['edges'][i].get('weight')*decay})
                if graph[word]['edges'][i]['term'] not in traversedList:
                    futureTraversals.put({'term':graph[word]['edges'][i].get('term'), 'weight':graph[word]['edges'][i].get('weight')})
                    traversedList.add(graph[word]['edges'][i].get('term'))
            if(not futureTraversals.empty()):
                while not futureTraversals.empty():
                    totraverse = futureTraversals.get()
                    graph, traversedList = spread(word=totraverse['term'], graph=graph, traversedList=traversedList, previousScore=totraverse['weight'])

        else:
            return graph, traversedList
        return graph, traversedList

    def activeGraph(graph):
        gcopy = copy.deepcopy(graph)
        itemsToPop = []
        for val in gcopy:
            if gcopy[val]['weight']==0:
                itemsToPop.append(val)
            else:
                gcopy[val]['edges'] = [w for w in gcopy[val]['edges'] if w.get('weight') !=0]
        for item in itemsToPop:
            del gcopy[item]
        return gcopy
    
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
    


    def listOfWords(graph, textEntry, useTFIDF = True, useTextRank=False):

        tokens = [w for w in nlp(textEntry) if not (w.is_punct or not w.is_alpha)]
        terms = []
        with Pool(min(len(tokens), 50)) as pool:
            results = pool.map_async(dicioDef, ((token.orth_, token.pos_) for token in tokens))
            terms = results.get()
        words = []
        for term in terms:
            if term['word'] in graph:
                words.append(term['word'])
            if term['root'] in graph and term['root']!=term['word']:
                words.append(term['root'])
            else:
                for syn in term['synonyms']:
                    if syn in graph:
                        words.append(syn)
        return words

    def wordTuples(graph, textEntry):
        text = rootify(graph, textEntry)
        pt = textacy.load_spacy('pt')
        doc = textacy.Doc(text, lang=pt)
        ts = textacy.TextStats(doc)
        words = [{w[0]:w[1]} for w in textacy.keyterms.textrank(doc, normalize='lower', n_keyterms=ts.n_unique_words)]

        return words


    def activeGraphNoDocuments(graph):
        gcopy = activeGraph(graph)
        for val in gcopy:
            del gcopy[val]['documents']
        return gcopy

    def rootify(graph, text):
        tokens = [w for w in nlp(text) if not (w.is_punct or not w.is_alpha)]
        terms = []
        with Pool(min(len(tokens), 50)) as pool:
            results = pool.map_async(dicioDef, ((token.orth_, token.pos) for token in tokens))
            terms = results.get()
        words = []
        for term in terms:
            if term['word'] in graph:
                words.append(term['word'])
            elif term['root'] in graph and term['root']!=term['word']:
                words.append(term['root'])
            else:
                for syn in term['synonyms']:
                    if syn in graph:
                        words.append(syn)
                        break
        return (" ").join(words)
