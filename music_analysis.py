import datetime
import os
import pathlib
import sys
import numpy as np
import pandas as pd
import cleaning
import matplotlib.pyplot as plt
import copy
from scipy import stats
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')
stopwords_eng = set(stopwords.words('english')) # as shown in https://www.geeksforgeeks.org/removing-stop-words-nltk-python/
lemmatizer = WordNetLemmatizer() # as shown in https://www.geeksforgeeks.org/python-lemmatization-with-nltk/

# Parses string to timestamp
def to_timestamp(text):
    return text.timestamp()
to_timestamp_ufunc = np.frompyfunc(to_timestamp, 1, 1)

# Splits string by whitespace
def split(text):
    return text.split()
split_ufunc = np.frompyfunc(split, 1, 1)

# Lemmatizes
def lemmatize(word):
    return lemmatizer.lemmatize(word)
lemmatize_ufunc = np.frompyfunc(lemmatize, 1, 1)

# Uses ufunc to tokenize lyrics and put one token per row
def tokenize(song_data):
    words = copy.deepcopy(song_data)
    words['lyric'] = split_ufunc(words['lyric'])
    words = words.explode('lyric')
    words['lyric'] = lemmatize_ufunc(words['lyric'])
    return words

# Puts only unique words per song on a new row
def get_unique_words(words_data):
    words = copy.deepcopy(words_data)
    words['frequency'] = np.ones(words.shape[0])
    cols = [c for c in words.columns if c != 'frequency']
    unique_words = words.groupby(cols, as_index=False).agg({'frequency':'sum'})
    return unique_words

# Divides a col by the minutes column
def wpm(df, col):
    return df[col] / df['minutes']

# takes list of tokens and removes stopwords
def stop_word_removal(tokens):
    return [item for item in tokens if item not in stopwords_eng]

def drop_stopword(word):
    if word not in stopwords_eng:
        return word
    return pd.NA
drop_stopword_ufunc = np.frompyfunc(drop_stopword, 1, 1)

# # uses nltk to tokenize
# def tokenize_lyrics(df, lyric_column, tokenized_name):
#     # df[tokenized_name] = df[lyric_column].apply(word_tokenize)
#     # df[tokenized_name] = df[lyric_column].apply(lambda lyric: word_tokenize(lyric))
#     df[tokenized_name] = df.apply(lambda item: word_tokenize(item[lyric_column]), axis=1)

def read_api_data(api_data):
    # music_data = pd.read_csv(rap_archive)
    music_data = pd.read_csv(api_data)
    # print(f"api_data is:\n{music_data}")
    music_data = music_data[music_data['status_code']==200]
    # print(f"api_data with succesful API calls:\n{music_data}")
    music_data = music_data.dropna()
    # print(f"valid api_data is:\n{music_data}")

    music_data = music_data[music_data['release_date'].str.len() == 10]
    # music_data['release_date'] = pd.to_datetime(music_data['release_date'], format='mixed')
    music_data['release_date'] = pd.to_datetime(music_data['release_date'], format="%Y-%m-%d")
    music_data['release_date'] = music_data['release_date'].apply(to_timestamp)
    music_data['minutes'] = music_data['duration_ms'] / 60000
    music_data = music_data.drop('status_code', axis=1)
    return music_data

def read_lyric_data(rap_archive):
    # read lyric data from original songs
    first_run = False
    originals_archive = "original_songs.csv.gz"
    if (first_run):
        cleaning.export_original_songs(rap_archive, originals_archive)
    originals_data = pd.read_csv(originals_archive)
    return originals_data

# def main(rap_archive = "rap_archive.zip", api_data = "data-1.csv.gz", output_file=None):
def main(rap_archive = "rap_archive.zip", api_data = "api_original_songs.csv.gz", output_file=None):

    # TODO: access spotify API
    music_data = read_api_data(api_data)
    lyric_data = read_lyric_data(rap_archive)

    # TODO: merge API data and music_data
    song_data = music_data.merge(lyric_data, on=['song','artist'], how='inner')
    # print(f"song_data is:\n{song_data}")

    lines_data = song_data

    # TODO: actually perform analysis

    # boey code: one row per word or unique word
    words = tokenize(song_data)
    unique_words = get_unique_words(words)
    # print(f"words dataframe is:\n{words}")
    # print(f"unique_words dataframe is:\n{unique_words}")

    # boey code: content words
    content_words = copy.deepcopy(words)
    content_words['lyric'] = drop_stopword_ufunc(content_words['lyric'])
    content_words = content_words.dropna()

    # boey code: count words
    word_count = words.groupby([c for c in words.columns if c != 'lyric'], as_index=False).count()
    word_count = word_count.rename(columns={'lyric':'word count'})
    song_data = song_data.merge(word_count)
    # print(f"song_data is:\n{song_data}")

    # boey code: count unique words
    unique_word_count = words.groupby([c for c in words.columns if c != 'lyric'], as_index=False).agg({'lyric':'nunique'})
    unique_word_count = unique_word_count.rename(columns={'lyric':'unique word count'})
    song_data = song_data.merge(unique_word_count)
    # print(f"song_data is:\n{song_data}")

    # boey code: count content words
    content_word_count = content_words.groupby([c for c in content_words.columns if c != 'lyric'], as_index=False).count()
    content_word_count = content_word_count.rename(columns={'lyric':'content word count'})
    song_data = song_data.merge(content_word_count)
    # print(f"song_data is:\n{song_data}")

    # boey code: words and unique words per minute
    song_data['words per minute'] = wpm(song_data, 'word count')
    song_data['unique words per minute'] = wpm(song_data, 'unique word count')
    song_data['lexical density'] = song_data['content word count'] / song_data['word count']
    # song_data = song_data.sort_values('words per minute')
    song_data = song_data[song_data['words per minute'] <= 450] # prune songs over 450 words/min
    # print(f"song_data is:\n{song_data}")

    # boey code: most frequent content words per song
    percentile = 75.0
    unique_content_words = get_unique_words(content_words)
    grouped = unique_content_words.groupby([c for c in unique_content_words.columns if c not in ['lyric','frequency count']], as_index=False)
    unique_content_words['word count rank'] = grouped['frequency'].rank(pct=True)
    top_content_words = unique_content_words[unique_content_words['word count rank'] >= (percentile/100.0)]
    top_content_words = top_content_words.sort_values('word count rank',ascending=True)
    # print(f"top_content_words is:\n{top_content_words}")

    # linear regression: words per minute
    song_data = song_data.sort_values('release_date')
    fit = stats.linregress(x=song_data['release_date'], y=song_data['words per minute'])
    print(fit)

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
