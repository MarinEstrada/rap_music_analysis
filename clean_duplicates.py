# Keeps unique song-lyric combos or the first of any duplicates
def drop_covers(df):
    df = df.drop_duplicates(subset=['song', 'lyric'], keep='first')
    return df

# Gets duplicates by subset
def duplicates(df, cols):
    df = df.sort_values('song', ascending=True)
    df['is_dupe'] = df.duplicated(subset=cols,keep=False)
    df = df[df['is_dupe']]
    return df

# Gets duplicated song title + lyric combos
def duplicated_songs(df):
    return duplicates(df, ['song','lyric'])
covers = duplicated_songs

# Gets duplicated song titles
def duplicated_titles(df):
    return duplicates(df, ['song'])