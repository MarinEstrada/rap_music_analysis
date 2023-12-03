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
# nltk.download('stopwords)')
# stop_words = set(stopwords.words('english')) # as shown in https://www.geeksforgeeks.org/removing-stop-words-nltk-python/

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
    print(f"song_data is:\n{song_data}")

    # TODO: actually perform analysis
    song_data = count_unique(song_data, 'lyric', 'unique word count')
    song_data = wpm(song_data,'unique word count', 'minutes')
    print(f"song_data is:\n{song_data}")
    # song_data = tokenize_lyrics(song_data, 'lyric', 'tokenized_lyric')
    song_data['tokenized'] = song_data.apply(lambda item: word_tokenize(item['lyric']), axis=1)
    # print('hi')
    print(f"song_data is:\n{song_data}")

    wordy_songs = song_data[song_data['unique word count per minute'] > 450]
    wordy_songs = wordy_songs.sort_values(by='unique word count per minute',ascending=True)
    y = wordy_songs['unique word count per minute']
    x = wordy_songs['release_date']
    plt.scatter(x,y)
    # plt.show()
    # wordy_songs.to_csv('output_boey.csv')

    exit()

    song_data['unique_words'] = song_data['lyric'].apply(unique_words)
    song_data['words'] = len(song_data['lyric'].apply(lambda x: x.split()))
    song_data['words per minute'] = song_data['words'] / song_data['minutes']
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
        main(rap_archive=rap_archive, api_acquired=api_acquired, output_file=output_file)
