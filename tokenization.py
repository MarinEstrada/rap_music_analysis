import copy
import nltk
import numpy as np
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
nltk.download('stopwords')
stopwords_eng = set(stopwords.words('english')) # as shown in https://www.geeksforgeeks.org/removing-stop-words-nltk-python/
import pandas as pd
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer() # as shown in https://www.geeksforgeeks.org/python-lemmatization-with-nltk/

# POS Tagger for a line of text
def pos(line):
    return nltk.pos_tag(line)
pos_ufunc = np.frompyfunc(pos, 1, 1)

# Converts Treebank tag to WordNet tag
def convert_pos(pos):
    match pos[0]:
        case "N":
            return wn.NOUN
        case "V":
            return wn.VERB
        case "J":
            return wn.ADJ
        case "R":
            return wn.ADV
        case default:
            return None

# Additional lemmatizing criteria
def prelemmatize(word_with_pos):
    word = word_with_pos[0]
    pos = convert_pos(word_with_pos[1])

    # return words that lemmatizer would null (e.g. stopwords)
    if pos == None or word in stopwords_eng:
        return word

    # remove words with 3+ repeated consecutive letters
    if len(word) > 2:
        word_array = np.array(list(word))
        groups = (word_array != np.roll(word_array,1)).cumsum()
        _, counts = np.unique(groups, return_counts=True)
        gibberish = np.any(counts >= 3)
        if gibberish:
            return pd.NA
        
    # "ing" -> "in": contracted verb
    if len(word) > 2 and word[-2:] == "in":
        lemma = lemmatizer.lemmatize(word + "g", "v")
        if lemma != word:
            return lemma
   
    return lemmatizer.lemmatize(word, pos)

prelemmatize_ufunc = np.frompyfunc(prelemmatize, 1, 1)

# Uses ufunc to tokenize lyrics and put one token per row
def tokenize(song_data, first_run = False):

    if first_run: 
        words = copy.deepcopy(song_data)
        # tic = time.time()
        # get pos tags and lemmatize entire line
        words['lyric'] = pos_ufunc(words['lyric'].str.split())
        words = words.explode('lyric')
        words['lemma'] = prelemmatize_ufunc(words['lyric'])
        # print(time.time() - tic)

        words['lyric'] = words['lemma']
        words = words.drop('lemma', axis=1)
        words = words.dropna()

        words.to_csv("tokenized.csv.gz", index=False, compression='gzip')

    else:     
        words = pd.read_csv("tokenized.csv.gz")
    
    return words