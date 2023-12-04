import datetime
import os
import pathlib
import sys
import numpy as np
import pandas as pd
import scipy
import cleaning
import matplotlib.pyplot as plt
import copy
from scipy import stats
import seaborn
seaborn.set()
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet as wn
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')
stopwords_eng = set(stopwords.words('english')) # as shown in https://www.geeksforgeeks.org/removing-stop-words-nltk-python/
lemmatizer = WordNetLemmatizer() # as shown in https://www.geeksforgeeks.org/python-lemmatization-with-nltk/

# Parses string to timestamp
def to_timestamp(text):
    return text.timestamp()
to_timestamp_ufunc = np.frompyfunc(to_timestamp, 1, 1)

# # uses nltk to tokenize
# def tokenize_lyrics(df, lyric_column, tokenized_name):
#     # df[tokenized_name] = df[lyric_column].apply(word_tokenize)
#     # df[tokenized_name] = df[lyric_column].apply(lambda lyric: word_tokenize(lyric))
#     df[tokenized_name] = df.apply(lambda item: word_tokenize(item[lyric_column]), axis=1)

# Reads API data
def read_api_data(api_data):
    # music_data = pd.read_csv(rap_archive)
    music_data = pd.read_csv(api_data)
    # print(f"api_data is:\n{music_data}")
    music_data = music_data[music_data['status_code']==200]
    # print(f"api_data with succesful API calls:\n{music_data}")
    music_data = music_data.dropna()
    music_data = music_data.drop('status_code', axis=1)
    # print(f"valid api_data is:\n{music_data}")

    # Parse dates
    music_data = music_data[music_data['release_date'].str.len() == 10]
    music_data['release_date'] = pd.to_datetime(music_data['release_date'], format='mixed')
    music_data['release_date'] = music_data['release_date'].apply(to_timestamp)
    music_data['minutes'] = music_data['duration_ms'] / 60000
    
    return music_data

# Reads lyric data from original songs
def read_lyric_data(rap_archive):
    first_run = False
    originals_archive = "original_songs.csv.gz"
    if (first_run):
        cleaning.export_original_songs(rap_archive, originals_archive)
    originals_data = pd.read_csv(originals_archive)
    return originals_data

# Splits string by whitespace
def split(text):
    return text.split()
split_ufunc = np.frompyfunc(split, 1, 1)

# Lemmatizes
def lemmatize(word):
    lemmas = wn._morphy(word, "n")
    if lemmas:
        return min(lemmas, key=len)
    return pd.NA
    # return lemmatizer.lemmatize(word)
lemmatize_ufunc = np.frompyfunc(lemmatize, 1, 1)

# Uses ufunc to tokenize lyrics and put one token per row
def tokenize(song_data):
    words = copy.deepcopy(song_data)
    words['lyric'] = split_ufunc(words['lyric'])
    words = words.explode('lyric')
    
    originals = copy.deepcopy(words)

    words['lyric'] = lemmatize_ufunc(words['lyric'])

    # searching for tokens with no lemma found
    originals['lemmas'] = words['lyric']
    originals = originals[originals.isna().any(axis=1)]
    originals = originals.drop_duplicates(subset=['lyric'])
    originals['lyric'].to_csv('no_lemma_found.csv', index=False)

    words = words.dropna()
    return words

# Puts only unique words per song on a new row
def get_unique_words(words_data):
    words = copy.deepcopy(words_data)
    words['frequency'] = np.ones(words.shape[0])
    cols = [c for c in words.columns if c != 'frequency']
    unique_words = words.groupby(cols, as_index=False).agg({'frequency':'sum'})
    return unique_words

# takes list of tokens and removes stopwords
def stop_word_removal(tokens):
    return [item for item in tokens if item not in stopwords_eng]

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

# Divides a col by the minutes column
def wpm(df, col):
    return df[col] / df['minutes']

# Plots data with optional best fit line
def plot(x, y, x_label, y_label, title, fit=None):
    plt.plot(x, y, 'b.', alpha=0.5)
    if fit != None:
        fit = scipy.stats.linregress(x,y)
        prediction = x.apply(lambda x : x*fit.slope + fit.intercept)
        plt.plot(x, prediction, 'r-', linewidth=3)
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.savefig("output_plots/"+"_".join(title.split()))
    plt.show()

# def main(rap_archive = "rap_archive.zip", api_data = "data-1.csv.gz", output_file=None):
def main(rap_archive = "rap_archive.zip", api_data = "api_original_songs.csv.gz", output_file=None):

    # access spotify API
    music_data = read_api_data(api_data)
    lyric_data = read_lyric_data(rap_archive)

    # merge API data and music_data
    song_data = music_data.merge(lyric_data, on=['song','artist'], how='inner')
    # print(f"song_data is:\n{song_data}")

    # look at albums as a whole entity
    # as each artist has their own style, we do not want the stats to be skewed simply by the prolificness of the artist
    # song_data = song_data.groupby(['release_date', 'artist'], as_index=False).agg({'lyric':lambda x: ' '.join(x), 'minutes':'sum'})

    lines_data = song_data

    # boey code: one row per word or unique word
    words = tokenize(song_data)
    unique_words = get_unique_words(words)
    content_words = drop_stopwords(words)
    unique_content_words = get_unique_words(content_words)

    # boey code: count words (all/content-only, unique/non-unique)
    song_data = add_wordcount(song_data, words, 'word count')
    song_data = add_wordcount(song_data, content_words, 'content word count')
    song_data = add_wordcount(song_data, unique_words.drop('frequency',axis=1), 'unique word count')
    song_data = add_wordcount(song_data, unique_content_words.drop('frequency',axis=1), 'unique content word count')

    # boey code: words and unique words per minute
    song_data['words per minute'] = wpm(song_data, 'word count')
    song_data['unique words per minute'] = wpm(song_data, 'unique word count')
    song_data['lexical density'] = song_data['content word count'] / song_data['word count']
    song_data['lexical diversity'] = song_data['unique content word count'] / song_data['content word count']
    song_data = song_data[song_data['words per minute'] <= 450] # prune songs over 450 words/min

    # linear regression: words per minute
    plot(song_data['release_date'], song_data['words per minute'], 'release date', 'words per minute', 'words per minute by date', True)
    plot(song_data['release_date'], song_data['lexical density'], 'release date', 'lexical density (content words / total words)', 'lexical density by date', True)
    plot(song_data['release_date'], song_data['lexical diversity'], 'release date', 'lexical diversity (unique content words / content words)', 'lexical diversity by date', True)
    plot(song_data['release_date'], song_data['unique words per minute'], 'release date', 'unique words per minute', 'unique words per minute by date', True)

    # boey code: most frequent content words per song
    percentile = 75.0
    grouped = unique_content_words.groupby([c for c in unique_content_words.columns if c not in ['lyric','frequency count']], as_index=False)
    unique_content_words['word count rank'] = grouped['frequency'].rank(pct=True)
    top_content_words = unique_content_words[unique_content_words['word count rank'] >= (percentile/100.0)]
    top_content_words = top_content_words.sort_values('word count rank',ascending=True)
    # print(f"top_content_words is:\n{top_content_words}")

    # justin code: sentiment analysis
    # song_data['sentiment score'] <-- 


if __name__ == '__main__':
    if len(sys.argv) <2: 
        main() # no arguments provided, go normal
    else:
        if len(sys.argv) < 3:
            print("please add inputs and optional output files to command,")
            print("input file should be csv (compressed or uncompress), output file should be COMPRESSED _.csv.gz")
            print("ie:\npython3 music_analysis.py <input_raparchive> <input_data acquired> {<output_file>}")
            exit()
        rap_archive = sys.argv[1]
        api_acquired = sys.argv[2]
        if len(sys.argv) >= 4: output_file = sys.argv[3]
        else: output_file = None
        main(rap_archive=rap_archive, api_data=api_acquired, output_file=output_file)
