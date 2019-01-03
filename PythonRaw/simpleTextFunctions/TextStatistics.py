
# Returns the lexical diversity of the text, making a relation between the number of words and the number of distinct words.
def lexicalDiversity(text):
    return len(set(text))/len(text)

