# created using https://www.youtube.com/watch?v=tmt5SdvTqUI&list=PLqgOPibB_QnzzcaOFYmY2cQjs35y0is9N&index=2 as reference
import os
import sys
import pathlib
# import json
import spotipy
# import webbrowser
# import spotipy.util as util
# from json.decoder import JSONDecodeError
from spotipy.oauth2 import SpotifyClientCredentials

import numpy as np

import time


import pandas as pd

# use as Ref
# https://www.youtube.com/watch?v=WAmEZBEeNmg
from requests import post, get # allows us to send post & get requests
import json
import base64 # allows us to send request as base64 object
from dotenv import load_dotenv # to get our environment variables
load_dotenv() #gets environment variables from our .env file

#global var
cid = os.getenv('SPOTIFY_CLIENT_ID')
secret = os.getenv('SPOTIFY_CLIENT_SECRET')

# we will use client credentials workflow

# step 1: get temporary aurhorization token
# token acquired will be used in future headers to make requests
# def get_token(client_id=cid, client_secret=secret):
def get_token():
    auth_string = cid + ":" + secret # concatonate id and secret
    auth_bytes = auth_string.encode("utf-8") #encode authorization string to udf-8
    auth_base64 = str(base64.b64encode(auth_bytes), 'utf-8') # returns base64 object to send request

    url = 'https://accounts.spotify.com/api/token' # where we doing our request to 
    headers = {
         "Authorization" : "Basic " + auth_base64, #where we sending authorization data
         "Content-Type": "application/x-www-form-urlencoded", # speficy content type (usually we have application json, 
        #  but here we specify specific type)
    }
    data = {"grant_type" : "client_credentials"} #grant type must be equal to client credentials

    # Now: we ready to formulate request
    result = post(url, headers = headers, data=data) # jason data will be avail in field 'object' ie: result.content
    json_result = json.loads(result.content)
    # print(f"cid is :{cid}")
    # print(f"secret is :{secret}")
    # print(f"result is:\n{result}")
    # print(f"json_result is:\n{json_result}")
    # print()
    token = json_result["access_token"]
    return token

# for any future requests to automatically be in right format
# developer.spotify.com/console/get-search-item/
def get_auth_header(token):
    return {"Authorization" : "Bearer " + token}

# developer.spotify.com/console/get-search-item/
def search_for_artist(token, artist_name=None, track_name=None):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)

    #need to construct query
    # note type is a comma delimited list
    # query = f"?q={artist_name}&type=artist&limit=1" #example for searching for artist
    query = f"?q={track_name}&type=track&limit=1" #example for searching for track TESTING
    # query = f"?q={artist_name}&type=artist,track&limit=1" #example for searching for artist &sing artist and track type
    # query = f"?q={artist_name}&type=artist,track&limit=1" #example for searching for artist

    query_url = url + query
    result = get(query_url, headers=headers)
    # print(f"result type is:{type(result)}\nresult is:\n{result}\nresult code is: {result.status_code}")
    # json_result = json.loads(result.content)
    if result.status_code == 200:
        json_result = json.loads(result.content)["tracks"]["items"]
        if len(json_result) == 0:
            print("track not found")
            return None, result.status_code
        # print(f"json_result is:\n{json_result}\n")
        return json_result[0], result.status_code
    else:
        return None, result.status_code

# def find_track(artist=artist, song=song):

#     # use as ref
#     # https://stackoverflow.com/questions/42766000/spotipy-how-do-i-search-by-both-artist-and-song
#     let q = String.init(format:"artist:%@ track:%@",artist,song)
#     return None

def print_result(result):
    if result != None:
        print(f"artist is: {result['artists'][0]['name']}")
        print(f"song is: {result['name']}")
        print(f"song release date is: {result['album']['release_date']}")
        print(f"song duration is: {result['duration_ms']}")
    else:
        print("Song not found")

# get track info if correct artist
def get_song_info(token = None, artist_name=None, track_name=None, print_output=False):
# def get_song_info(token = None, artist_name=None, track_name=None, artists_song_count = None):
    # time.sleep(10)
    # print('hi1')
    result, status_code = search_for_artist(token, track_name=track_name)
    # print_result(result)
    if status_code == 200:
        if result == None: #if no result do not count it
            # print('result is None')
            if print_output: print(f"{artist_name},{track_name},,,{status_code}")
            return None, None, status_code
        elif artist_name.lower() != result['artists'][0]['name'].lower(): # if artist name does not match do not count it
            # print('artist name did not match')
            if print_output: print(f"{artist_name},{track_name},,,{status_code}")
            return None, None, status_code
        else:
            # print("yay!")
            # return release_date & duration
            if print_output: print(f"{artist_name},{track_name},{result['album']['release_date']},{result['duration_ms']},{status_code}")
            return result['album']['release_date'], result['duration_ms'], status_code
    else:
        if print_output: print(f"{artist_name},{track_name},,,{status_code}")
        return None, None, status_code
    # print("done")
    # return result['album']['release_date'], result['duration_ms']


# def main(zip_file = "new_rap_archive.zip", client_id=cid, client_secret=secret):
def main(input_file=None, output_file=None, client_id=cid, client_secret=secret, print_output=False):

    music_data = pd.read_csv(input_file)
    # print(f"rap_data is:\n{music_data}")

    songs_df = music_data.drop(columns=['lyric'])

    

    # commented out for acquisition using original_songs.csv.gz
    '''
    songs_df = music_data.drop(columns=['extra','lyric','next lyric'])
    songs_df = songs_df.drop_duplicates()# drop non-unique rows
    # print(f"rap_data with droped columns is:\n{songs_df}")

    # artist_count = songs_df.groupby(['song']).agg('count')

    # Remove songs that have more than 1 artist (song repitition/covers)
    artist_count = songs_df.groupby(['song']).count()
    artist_count = artist_count.rename(columns={'artist':'artist_count'}) #rename count of artsts by song title
    artist_count = artist_count[artist_count['artist_count'] == 1] #keep only if song has one artist
    # artist_count = artist_count.reset_index()
    # print(f"grouped by df is\n{artist_count}")

    #join count and songs to remove
    songs_df = songs_df.set_index('song')
    songs_df = songs_df.join(artist_count)
    songs_df = songs_df.dropna() #keep the songs that had only one artist
    songs_df = songs_df.reset_index()
    songs_df = songs_df.drop(columns=['artist_count'])
    # print(f"joined dfs is:\n{songs_df}")

    # #acquire how many songs per artist
    # #THIS SHOULD BE DONE LAST
    # song_count = songs_df.groupby(['artist']).count()
    # song_count = song_count.rename(columns={'song' : 'artists_song_count'}) #rename count of songs by artists
    # # print(f"song_count is:\n{song_count}")
    # songs_df = songs_df.set_index('artist')
    # # print(f"songs_df is:\n{songs_df}")
    # songs_df = songs_df.join(song_count)
    # songs_df = songs_df.reset_index()
    # print(f"joined dfs is:\n{songs_df}")
    
    # cleaned df to its own seperate csv for reference
    songs_df.to_csv('df_for_analysis.csv.gz', index=False, compression='gzip')
    '''


    # #following new ref vid
    # # print(f"cid: {cid}\nsecret: {secret}")
    # token = get_token()
    # # print(f"token is: {token}")
    # # search_for_artist(token, artist_name="ACDC")
    # result = search_for_artist(token, track_name="Paint it Black")
    # # search_for_artist(token, artist_name="The Rolling Stones", track_name="Paint it Black")

    # # print(f"result is:\n{result}")
    # # print('\nhi')

    #STUFF THAT WORKS:

    token = get_token()
    # result = search_for_artist(token, track_name="Paint it Black")
    # print_result(result)

    # test pandas df
    artist_list = ["The Rolling Stones", "The Rolling Stones", "The Beatles", "Blink182"]
    song_list = ["Paint it Black", "Satisfaction", "Hey Jude", "The Rock Show"]
    test_dict = {'artist': artist_list,
                'song': song_list}
    test_df = pd.DataFrame(test_dict)
    # print(f"Test df is:\n{test_df}")
    # print(f"song list is length {len(song_list)}")
    # print(f"artist list is length {len(artist_list)}")
    # print(f"shape of test df is {test_df.shape}")

    #Using https://stackoverflow.com/questions/30026815/add-multiple-columns-to-pandas-dataframe-from-function as ref
    # test_df[['release_date', 'duration_ms']] = test_df.apply(lambda item: pd.Series(get_song_info(token, item['artists'], item['songs'])), axis=1)
    lambda_add_info = lambda item: pd.Series(get_song_info(token, item['artist'], item['song'], print_output))
    # test_df[['release_date', 'duration_ms','status_code']] = test_df.apply(lambda_add_info, axis=1)
    songs_df[['release_date', 'duration_ms', 'status_code']] = songs_df.apply(lambda_add_info, axis=1)

    # print(f"Improved test df is:\n{test_df}")

    # test_df.to_csv('data-1.csv.gz', index=False, compression='gzip')
    # songs_df.to_csv('data-1.csv.gz', index=False, compression='gzip')
    songs_df.to_csv(output_file, index=False, compression='gzip')
    songs_df = songs_df.merge(music_data, on=['song','artist'], how='inner') #taken from boey's contribution of code
    songs_df.to_csv("merged_"+ output_file, index=False, compression='gzip')

    # music_data.to_csv('test.csv.gz', index=False, compression='gzip')



    # TODO: access spotify API

    # TODO: join API data and music_data

    # TODO: actually perform analysis

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("please add input and output files to command,")
        print("input file should be csv (compressed or uncompress), output file should be COMPRESSED _.csv.gz")
        print("ie:\npython3 acquire_song_data.py <input_file> <output_file> {print}")
        exit()
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    print_output = False
    if len(sys.argv) >= 4:
        if sys.argv[3] == 'print':
            print_output = True
    main(input_file=input_file, output_file=output_file, client_id=cid, client_secret=secret, print_output=print_output)
