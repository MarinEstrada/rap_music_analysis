import os
import pathlib
import sys
import numpy as np
import pandas as pd

def main(zip_file = "rap_archive.zip"):

    music_data = pd.read_csv(zip_file)
    print(f"rap_data is:\n{music_data}")

    # TODO: access spotify API

    # TODO: join API data and music_data

    # TODO: actually perform analysis

if __name__ == '__main__':
    main()
