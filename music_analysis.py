import os
import pathlib
import sys
import numpy as np
import pandas as pd

def main(rap_archive = "rap_archive.zip", data_acquired = "data-1.csv.gz"):

    # music_data = pd.read_csv(rap_archive)
    music_data = pd.read_csv(data_acquired)
    print(f"data_acquired is:\n{music_data}")
    music_data = music_data[music_data['status_code']==200]
    print(f"data_acquired with succesful API calls:\n{music_data}")
    music_data = music_data.dropna()
    print(f"valid data_acquired is:\n{music_data}")


    # TODO: access spotify API

    # read lyric data
    lyric_data = pd.read_csv(rap_archive)
    lyric_data = lyric_data.drop('next lyric', axis=1)
    lyric_data = lyric_data.drop(lyric_data.columns[0], axis=1)

    # TODO: merge API data and music_data
    music_data = music_data.merge(lyric_data, on=['song','artist'], how='inner')
    
    # DF: One song per row
    by_song = lyric_data.groupby(['artist', 'song']).agg({'lyric': ' '.join})
    # print(by_song)

    # DF: One word per row
    by_word =lyric_data
    by_word['lyric'] = by_word['lyric'].apply(lambda x: x.split())
    by_word = by_word.explode('lyric')
    # print(by_word)

    # TODO: actually perform analysis

if __name__ == '__main__':
    main()
