# Puts only unique words per song on a new row
import copy
import numpy as np
import pandas as pd
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')
stopwords_eng = set(stopwords.words('english')) # as shown in https://www.geeksforgeeks.org/removing-stop-words-nltk-python/


def get_unique_words(words_data):
    words = copy.deepcopy(words_data)
    words['frequency'] = np.ones(words.shape[0])
    cols = [c for c in words.columns if c != 'frequency']
    unique_words = words.groupby(cols, as_index=False).agg({'frequency':'sum'})
    return unique_words

# Returns content word or NA
def drop_stopword(word):
    if word not in stopwords_eng:
        return word
    return pd.NA
drop_stopword_ufunc = np.frompyfunc(drop_stopword, 1, 1)

# Returns a copy of 'df' without stopwords (only lexical/content words)
def drop_stopwords(df):
    content_words = copy.deepcopy(df)
    content_words['lyric'] = drop_stopword_ufunc(content_words['lyric'])
    content_words = content_words.dropna()
    return content_words

# Adds column to 'df' with the song-wise count of each lyric from 'words'
def add_wordcount(df, words, col_name):
    word_count = copy.deepcopy(words)
    word_count = word_count.groupby([c for c in words.columns if c != 'lyric'], as_index=False).count()
    word_count = word_count.rename(columns={'lyric':col_name})
    df = df.merge(word_count)
    return df