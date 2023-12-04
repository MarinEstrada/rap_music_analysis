import sys
import numpy as np
import pandas as pd
import datetime
import seaborn
seaborn.set()
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')
stopwords_eng = set(stopwords.words('english')) # as shown in https://www.geeksforgeeks.org/removing-stop-words-nltk-python/
lemmatizer = WordNetLemmatizer() # as shown in https://www.geeksforgeeks.org/python-lemmatization-with-nltk/

# custom modules
import original_songs
import tokenization
import word_manipulation
import output

# Parses string to timestamp
def to_timestamp(text):
    return text.timestamp()

# Reads API data
def read_api_data(api_data):
    # music_data = pd.read_csv(rap_archive)
    music_data = pd.read_csv(api_data)
    # print(f"api_data is:\n{music_data}")
    music_data = music_data[music_data['status_code']==200]
    # print(f"api_data with succesful API calls:\n{music_data}")
    music_data = music_data.dropna()
    music_data = music_data.drop('status_code', axis=1)
    # print(f"valid api_data is:\n{music_data}")

    # Parse dates
    music_data = music_data[music_data['release_date'].str.len() == 10]
    music_data['release_date'] = pd.to_datetime(music_data['release_date'], format='mixed')
    music_data['release_date'] = music_data['release_date'].apply(to_timestamp)
    music_data['minutes'] = music_data['duration_ms'] / 60000
    
    return music_data

# Reads lyric data from original songs
def read_lyric_data(rap_archive, first_run = False):
    originals_archive = "original_songs.csv.gz"

    if (first_run):
        original_songs.export_original_songs(rap_archive, originals_archive)
    originals_data = pd.read_csv(originals_archive)

    return originals_data

# Divides a col by the minutes column
def wpm(df, col):
    return df[col] / df['minutes']

# def main(rap_archive = "rap_archive.zip", api_data = "data-1.csv.gz", output_file=None):
def main(rap_archive = "rap_archive.zip", api_data = "api_original_songs.csv.gz", output_file=None):

    # access spotify API
    music_data = read_api_data(api_data)
    lyric_data = read_lyric_data(rap_archive, first_run=False)

    # merge API data and music_data
    song_data = music_data.merge(lyric_data, on=['song','artist'], how='inner')

    # look at albums as a whole entity
    # as each artist has their own style, we do not want the stats to be skewed simply by the prolificness of the artist
    # song_data = song_data.groupby(['release_date', 'artist'], as_index=False).agg({'lyric':lambda x: ' '.join(x), 'minutes':'sum'})

    lines_data = song_data

    # boey code: get one row per word, for different kinds of words
    words = tokenization.tokenize(song_data, first_run=True)
    content_words = word_manipulation.drop_stopwords(words)
    unique_content_words = word_manipulation.get_unique_words(content_words)

    # boey code: get wordcounts
    song_data = word_manipulation.add_wordcount(song_data, words, 'word count')
    song_data = word_manipulation.add_wordcount(song_data, content_words, 'content word count')
    song_data = word_manipulation.add_wordcount(song_data, unique_content_words.drop('frequency',axis=1), 'unique content word count')

    # boey code: scale wordcounts for analysis
    song_data['words per minute'] = wpm(song_data, 'word count')
    song_data['lexical density'] = song_data['content word count'] / song_data['word count']
    song_data['lexical diversity'] = song_data['unique content word count'] / song_data['content word count']
    song_data = song_data[song_data['words per minute'] <= 450] # prune songs over 450 words/min

    # linear regression figures
    output.plot(song_data['release_date'], song_data['words per minute'], 'release date', 'words per minute', 'words per minute by date')
    output.plot(song_data['release_date'], song_data['lexical density'], 'release date', 'lexical density (content words / total words)', 'lexical density by date')
    output.plot(song_data['release_date'], song_data['lexical diversity'], 'release date', 'lexical diversity (unique content words / content words)', 'lexical diversity by date')

    # linear regression statistics
    output.print_fit(song_data['release_date'], song_data['words per minute'],'words per minute over time')
    output.print_fit(song_data['release_date'], song_data['lexical density'],'lexical density over time')
    output.print_fit(song_data['release_date'], song_data['lexical diversity'],'lexical diversity over time')

    # top 5 words in year
    # unique_content_words['year'] = unique_content_words['release_date'].apply(lambda x: datetime.date.fromtimestamp(x).year)
    # grouped = unique_content_words.groupby(['year','lyric'], as_index=False)
    # ranked_content_words = unique_content_words
    # ranked_content_words['rank'] = grouped['frequency'].rank()
    # ranked_content_words = ranked_content_words.sort_values('rank',ascending=True)
    # ranked_content_words = ranked_content_words[ranked_content_words['rank'] <= 5]
    # ranked_content_words.to_csv('boey.csv')

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
