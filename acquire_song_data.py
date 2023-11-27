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


import pandas as pd

# use as Ref
# https://www.youtube.com/watch?v=WAmEZBEeNmg
from requests import post # allows us to send post requests
import json
import base64 # allows us to send request as base64 object
from dotenv import load_dotenv # to get our environment variables
load_dotenv() #gets environment variables from our .env file

#global var
cid = os.getenv('SPOTIFY_CLIENT_ID')
secret = os.getenv('SPOTIFY_CLIENT_SECRET')

# we will use client credentials workflow

# step 1: get temporary aurhorization token
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
    print(f"cid is :{cid}")
    print(f"secret is :{secret}")
    print(f"result is:\n{result}")
    print(f"json_result is:\n{json_result}")
    print()
    token = json_result["access_token"]
    return token


# def find_track(artist=artist, song=song):

#     # use as ref
#     # https://stackoverflow.com/questions/42766000/spotipy-how-do-i-search-by-both-artist-and-song
#     let q = String.init(format:"artist:%@ track:%@",artist,song)
#     return None

def main(zip_file = "rap_archive.zip", client_id=cid, client_secret=secret):

    # music_data = pd.read_csv(zip_file)
    # print(f"rap_data is:\n{music_data}")

    # using as reference
    # https://towardsdatascience.com/extracting-song-data-from-the-spotify-api-using-python-b1e79388d50

    # #Authentication - without user
    # client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
    # sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)
    
    #following new ref vid
    # print(f"cid: {cid}\nsecret: {secret}")
    token = get_token()
    print(f"token is: {token}")

    # print(f"sp is of type {type(sp)} and is:\n{sp}")

    # TODO: access spotify API

    # TODO: join API data and music_data

    # TODO: actually perform analysis

if __name__ == '__main__':
    # cid = sys.argv[1]
    # secret = sys.argv[2]
    main(client_id=cid, client_secret=secret)
