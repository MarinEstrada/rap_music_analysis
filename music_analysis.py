import os
import pathlib
import sys
import numpy as np
import pandas as pd
import cleaning
import matplotlib.pyplot as plt
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
nltk.download('stopwords')
stopwords_eng = set(stopwords.words('english')) # as shown in https://www.geeksforgeeks.org/removing-stop-words-nltk-python/

# Splits string by whitespace
def split(text):
    return text.split()
split_ufunc = np.frompyfunc(split, 1, 1)

# Uses ufunc to tokenize lyrics and put one token per row
def tokenize(song_data):
    words = song_data
    words['lyric'] = split_ufunc(words['lyric'])
    words = words.explode('lyric')
    return words

# Puts only unique words per song on a new row
def unique_words(song_data):
    words = tokenize(song_data)
    words['unique word count'] = np.ones(words.shape[0])
    cols = [c for c in words.columns if c != 'unique word count']
    unique_words = words.groupby(cols, as_index=False).agg({'unique word count':'sum'})
    return unique_words

# Divides a col by the minutes column
def wpm(df, col):
    return df[col] / df['minutes']

# takes list of tokens and removes stopwords
def stop_word_removal(tokens):
    return [item for item in tokens if item not in stopwords_eng]

# # uses nltk to tokenize
# def tokenize_lyrics(df, lyric_column, tokenized_name):
#     # df[tokenized_name] = df[lyric_column].apply(word_tokenize)
#     # df[tokenized_name] = df[lyric_column].apply(lambda lyric: word_tokenize(lyric))
#     df[tokenized_name] = df.apply(lambda item: word_tokenize(item[lyric_column]), axis=1)


def main(rap_archive = "rap_archive.zip", api_data = "data-1.csv.gz", output_file=None):

    # music_data = pd.read_csv(rap_archive)
    music_data = pd.read_csv(api_data)
    # print(f"api_data is:\n{music_data}")
    music_data = music_data[music_data['status_code']==200]
    # print(f"api_data with succesful API calls:\n{music_data}")
    music_data = music_data.dropna()
    # print(f"valid api_data is:\n{music_data}")

    # TODO: access spotify API

    # read lyric data from original songs
    first_run = False
    originals_archive = "original_songs.csv.gz"
    if (first_run):
        cleaning.export_original_songs(rap_archive, originals_archive)
    originals_data = pd.read_csv(originals_archive)

    # TODO: merge API data and music_data
    music_data = music_data.drop('status_code', axis=1)
    song_data = music_data.merge(originals_data, on=['song','artist'], how='inner')
    song_data['minutes'] = song_data['duration_ms'] / 60000
    # print(f"song_data is:\n{song_data}")

    # TODO: actually perform analysis

    # print(f"song_data is:\n{song_data}")
    song_data = song_data[song_data['unique word count per minute'] <= 450] # prune songs over 450 words/min
    # song_data = tokenize_lyrics(song_data, 'lyric', 'tokenized_lyric')
    song_data['tokenized'] = song_data.apply(lambda item: word_tokenize(item['lyric']), axis=1) #tokenization of lyrics as seperate column
    print(f"song_data is:\n{song_data}")
    song_data['tokenized'] = song_data.apply(lambda item: stop_word_removal(item['tokenized']), axis=1) #removes stopwords from tokens
    print(f"song_data is:\n{song_data}")
    song_data['unique_words'] = song_data.apply(lambda item: set(item['tokenized']), axis=1) #by changing list of tokens to set we get unique words
    print(f"song_data is:\n{song_data}")


    song_data.to_csv('adri_output.csv')
    exit()

    # boey code: words
    words = tokenize(song_data)
    song_data['words per minute'] = wpm(song_data, 'words')

    # boey code: unique words
    unique_words = unique_words(words)
    song_data['unique words per minute'] = wpm(song_data, 'unique words')

    print(f"song_data is:\n{song_data}")

    # one row per word
    

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
