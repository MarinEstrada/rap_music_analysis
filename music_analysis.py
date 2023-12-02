import os
import pathlib
import sys
import numpy as np
import pandas as pd
import clean_duplicates

# Splits lyric column by word
def tokenize(df):
    df['lyric'] = df['lyric'].apply(lambda x: x.split())
    df = df.explode('lyric')
    return df

# Joins lyric column after grouping by every other column
def join_lyrics(df):
    cols = [col for col in df.columns if col != 'lyric']
    df['lyric'] = df['lyric'].apply(lambda x: x.strip())
    df = df.groupby(cols, as_index=False).agg({'lyric': ' '.join})
    return df

# Sorts by release date (old to new)
def sort(df):
    df = df.sort_values('release_date', ascending=True)
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

    # read lyric data
    lyric_data = pd.read_csv(rap_archive)
    lyric_data = lyric_data.drop('next lyric', axis=1)
    lyric_data = lyric_data.drop(lyric_data.columns[0], axis=1)

    # unique songs
    songs = join_lyrics(lyric_data)
    original_songs = clean_duplicates.drop_covers(songs)
    original_songs.to_csv('original_songs.csv')

    # TODO: merge API data and music_data
    data = music_data.merge(lyric_data, on=['song','artist'], how='inner')

    # TODO: actually perform analysis

    # one row per word
    words = tokenize(lyric_data)

if __name__ == '__main__':
    main()
