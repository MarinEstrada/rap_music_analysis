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

# Adds a column with the number of unique words in the 'by' column
def count_unique(df, by, count_name):
    df[count_name] = df[by].apply(lambda x: len(set(x.split())))
    return df

# Adds a column with the word_column divided by the minutes_column
def wpm(df, word_column, minutes_column):
    df[word_column + ' per minute'] = df[word_column] / df[minutes_column]
    return df


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

    # TODO: merge API data and music_data
    music_data = music_data.drop('status_code', axis=1)
    song_data = music_data.merge(originals_data, on=['song','artist'], how='inner')
    song_data['minutes'] = song_data['duration_ms'] / 60000

    # TODO: actually perform analysis
    song_data = count_unique(song_data, 'lyric', 'unique word count')
    song_data = wpm(song_data,'unique word count', 'minutes')

    wordy_songs = song_data[song_data['unique word count per minute'] > 450]
    wordy_songs = wordy_songs.sort_values(by='unique word count per minute',ascending=True)
    y = wordy_songs['unique word count per minute']
    x = wordy_songs['release_date']
    plt.scatter(x,y)
    plt.show()
    wordy_songs.to_csv('output_boey.csv')

    exit()

    song_data['unique_words'] = song_data['lyric'].apply(unique_words)
    song_data['words'] = len(song_data['lyric'].apply(lambda x: x.split()))
    song_data['words per minute'] = song_data['words'] / song_data['minutes']
    print(song_data)

    # one row per word
    

if __name__ == '__main__':
    main()
