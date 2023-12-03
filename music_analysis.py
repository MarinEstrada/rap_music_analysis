import os
import pathlib
import sys
import numpy as np
import pandas as pd
import cleaning
import matplotlib.pyplot as plt

# Sorts by release date (old to new)
def sort(df):
    df = df.sort_values('release_date', ascending=True)
    return df

def split(text):
    return text.split()
split_ufunc = np.frompyfunc(split, 1, 1)

# Tokenizes and puts words per song on a new row
def tokenize(song_data):
    # method 1:
    words = song_data
    words['lyric'] = split_ufunc(words['lyric'])
    words = words.explode('lyric')
    return words

# Divides a col by the minutes column
def wpm(df, col):
    return df[col] / df['minutes']

# Puts only unique words per song on a new row
def unique_words(song_data):
    words = tokenize(song_data)
    words['unique word count'] = np.ones(words.shape[0])
    cols = [c for c in words.columns if c != 'unique word count']
    unique_words = words.groupby(cols, as_index=False).agg({'unique word count':'sum'})
    return unique_words

def main(rap_archive = "rap_archive.zip", data_acquired = "data-1.csv.gz"):

    # music_data = pd.read_csv(rap_archive)
    music_data = pd.read_csv(data_acquired)
    # print(f"data_acquired is:\n{music_data}")
    music_data = music_data[music_data['status_code']==200]
    # print(f"data_acquired with succesful API calls:\n{music_data}")
    music_data = music_data.dropna()
    # print(f"valid data_acquired is:\n{music_data}")

    # TODO: access spotify API

    # read lyric data from original songs
    first_run = False
    originals_archive = "original_songs.csv.gz"
    if (first_run):
        cleaning.export_original_songs(rap_archive, originals_archive)
    originals_data = pd.read_csv(originals_archive)

    # merge API data and music_data
    music_data = music_data.drop('status_code', axis=1)
    song_data = music_data.merge(originals_data, on=['song','artist'], how='inner')
    song_data['minutes'] = song_data['duration_ms'] / 60000

    # TODO: actually perform analysis

    # words
    words = tokenize(song_data)
    song_data['words per minute'] = wpm(song_data, 'words')

    # unique words
    unique_words = unique_words(words)
    song_data['unique words per minute'] = wpm(song_data, 'unique words')

    # one row per word
    

if __name__ == '__main__':
    main()
