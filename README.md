# Repository for a collaborative analysis of how Rap Music has changed over the years

### Group members:
Kwan, Boey

Marin Estrada, Adrian

Yan, Justin

### Project
Inspired by critismims of new school rap compared to old school rap (https://thespellbinder.net/2832/features/evolution-of-rap-lyrics/ , https://medium.com/@geneduterte/hip-hop-the-evolution-of-lyricism-c7b01aff29b2), we will be examining...

Criticisms around lyrics: “repetitive chants”, “"sound identical"; "same beats and lyrics", “decline of lyricism”, “simplistic styles”

To use our program to acquqire data using spoitify's API, ensure you have installed spotipy and run the command:

```python3 acquire_song_data.py original_songs.csv.gz example_output_file.csv.gz``` to have results saved in example_output_file.csv.gz

Or:

```python3 acquire_song_data.py original_songs.csv.gz example_output_file.csv.gz print > backup_output_file.csv``` to have results saved in example_output_file.csv.gz as well as print and redirect the results to a backupfile called backup_output.gz which you can then compress yourself.

original_songs.csv.gz is a cleaned up version of the Kaggle dataset we found at https://www.kaggle.com/datasets/jamiewelsh2/rap-lyrics

To perform the actual analysis run:

```python3 music_analysis.py``` Note, ensure you are running python3.10 or above
