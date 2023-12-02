import os
import pathlib
import sys
import numpy as np
import pandas as pd
import cleaning

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

# Returns all original songs
def drop_covers(df):
    df = df.drop_duplicates(subset=['song', 'lyric'], keep='first')
    return df

# Returns duplicates according to specified columns
def duplicates(df, cols):
    df = df.sort_values('song', ascending=True)
    df['is_dupe'] = df.duplicated(subset=cols,keep=False)
    df = df[df['is_dupe']]
    return df

# Returns all covered songs (the original + its duplicates)
def duplicated_songs(df):
    return duplicates(df, ['song','lyric'])
covers = duplicated_songs

# Returns duplicated song titles (not necessarily covered songs)
def duplicated_titles(df):
    return duplicates(df, ['song'])

def export_original_songs(rap_archive = "rap_archive.zip", output_file = "original_songs.csv.gz"):
    # read lyric data
    lyric_data = pd.read_csv(rap_archive)
    lyric_data = lyric_data.drop('next lyric', axis=1)
    lyric_data = lyric_data.drop(lyric_data.columns[0], axis=1)

    # unique songs
    songs = join_lyrics(lyric_data)
    original_songs = drop_covers(songs)
    original_songs.to_csv(output_file, index=False, compression='gzip')