import nltk
from nltk.corpus import PlaintextCorpusReader

def loadTextFile(pathToFile):
    fileObject = open(pathToFile, "r")
    return fileObject

def textFileToList(pathToFile):
    fileObject = loadTextFile(pathToFile)
    textAsList = fileObject.readlines()
    return textAsList

def textFileToSentList(pathToFileFolder, FileNameWithExtension):
    wordlists = PlaintextCorpusReader(pathToFileFolder, '.*')
    return wordlists.sents(FileNameWithExtension)

def saveFilePhrasePerLine(listOfPhrases, fileName):
    fileToWrite = open(fileName+".txt", "w")
    
