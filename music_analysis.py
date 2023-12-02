import os
import pathlib
import sys
import numpy as np
import pandas as pd
import cleaning

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

    # read lyric data from original songs
    first_run = False
    original_songs_filename = "original_songs.csv.gz"
    if (first_run):
        cleaning.export_original_songs(rap_archive, original_songs_filename)
    lyric_data = pd.read_csv(original_songs_filename)
    print(lyric_data)
    exit()

    # TODO: merge API data and music_data
    data = music_data.merge(lyric_data, on=['song','artist'], how='inner')

    # TODO: actually perform analysis

    # one row per word
    words = tokenize(lyric_data)

if __name__ == '__main__':
    main()
