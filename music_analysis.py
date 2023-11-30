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

    # TODO: join API data and music_data

    # TODO: actually perform analysis

if __name__ == '__main__':
    main()
