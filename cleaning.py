import os
import pathlib
import sys
import numpy as np
import pandas as pd
import cleaning

# Splits lyric column by word
def tokenize(df, by):
    df[by] = df[by].apply(lambda x: x.split())
    df = df.explode(by)
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

def export_original_songs(input_file, output_file):
    lyric_data = pd.read_csv(input_file)
    lyric_data = lyric_data.drop(lyric_data.columns[0], 'next lyric', axis=1)

    song_data = join_lyrics(lyric_data)
    
    originals_data = drop_covers(song_data)
    originals_data.to_csv(output_file, index=False, compression='gzip')