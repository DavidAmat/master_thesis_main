
# 0. General

All the codes are assumed to be saved in the "Codigos" folder. Inside, there is a folder for each subtask (i.e Spotify) so, in each one you will find severals subfolders. The ones for developing code are **dev** and the final code is in **code**. 

<!--- 
Images:
<img src="imgs/img1.png" height=300px width=300px /> -->


## GitHub

All the repos will be in https://github.com/DavidAmat/. There will be a repo for each specific task in order not to mix dependencies for the dataset extraction, for the audio download and for the model construction.

To open a GitHub repo and link it to a local folder:

```bash
cd Codigos
mkdir Spotify
git init
git remote add origin https://github.com/DavidAmat/TFM_Spotify.git
git pull origin master
```
Each repo will have its own pipfile to avoid accumulate python packages for other tasks.

```bash

```


```bash

```
## Tables

Tables in Markdown are generated with https://www.tablesgenerator.com/markdown_tables

# 1. Spotify

The main code is in the folder **code/**.

The first thing to do is to create an **app** in Spotify API and get access in order to do Spotify API requests.

Once this is done, the main idea is to retrieve a list of artists from https://kworb.net/ with the idea to have all the top artists of Spotify and their songs as well as to create a graph for artists, songs (see which artists share songs) and similar artists and genres (edges from artist to artist and also from artist to genres). This dataset also provides the Spotify ID for either the artists and the songs, so it will be suitable for making future calls to the Spotify API to work always with such IDs. An artist who is NOT in Spotify cannot enter this study. To check an artist ID try: https://open.spotify.com/artist/<artist_id>

As regards architecture, we will first create a PostGRESQL and then convert this database named "Spotify" to a graph in Neo4j. This database will need info from songs too, we will either exploit the "kworb" dataset or, in case of artists which are not in that dataset and we want to include it, we will make a search in Spotify API for the top tracks of that artist.  

To start working on this section: 
```bash
cd Spotify
pipenv shell
pipenv run jupyter notebook
```

## 1.1 Description of the tasks 

So the order of steps to do is the following:

- Scrap the artists from the tables in the "kworb" website to create a list of artists which are present in kworb, we will denote these as "main_artists". 

- Use SpotifyAPI to find the Spotify ID for the artists that are not in the "main_artists" list, these artists will be denoted as "other_artists".

- Create a table **master_artist** to centralize all these results in PostGRESQL The "is_main" column will denote if either it has been found in the kworb website or not.

<center>

| table         | column      | type      | PK |
|---------------|-------------|-----------|----|
| master_artist | artist_id   | varchar() | Y  |
| master_artist | artist_name | varchar() | N  |
| master_artist | is_main     | bool      | N  |

</center>

This table should have as PK the artist_id to avoid inserting an artist_id that is already in the database. 

- After that we will query this table **master_artist** to retrive the is_main = 1, and scrap the "kworb" website, iterating for each artist and retrieving its top songs, as well as the featuring artists. This will be stored in another table, the **master_track** table:

<center>

| table        | column    | type      | PK |
|--------------|-----------|-----------|----|
| master_track | song_id   | varchar() | Y  |
| master_track | song_name | varchar() | N  |
| master_track | peak_date | date      | N  |
| master_track | streams | bigint      | N  |

</center>

For the songs that come from Spotify API (the songs for the "other_artists" instead of the peak date we have the "release date" which is more or less near in time so we will rely on that). 

- Finally, since one song can have many artists and one artist can have many songs, these relationships will be captured in the **rel_artist_track** table. It is important to state that if a featuring artist is NOT neither in the **master_artist** it will not appear in that table, and obviously, the same for a song that does not appear in the **master_track**. 

<center>

| table            | column    | type      | PK |
|------------------|-----------|-----------|----|
| rel_artist_track | song_id   | varchar() | N  |
| rel_artist_track | artist_id | varchar() | N  |

</center>

Recall that for the songs for the "other_artists" we will search the names of the songs, song_id and the featuring artists by means of the Spotify API. 

- After these information gets stored correctly, we will proceed to use the Spotify API again to retrieve **related artists**. This search, by setting as input an artist_id from the **master_artist** we will be able to get:
    - genres
    - followers
    - artist_name
    - artist_id

of the **similar artists** according to Spotify (popularity, followers and genres are referred to the similar artists, not the queried artist). Then, our task will be to check if any of these artists is present in the **master_artist** and if so, create a table to store those relationships:

<center>

| table             | column            | type      | PK |
|-------------------|-------------------|-----------|----|
| rel_artist_artist | query_artist_id   | varchar() | N  |
| rel_artist_artist | similar_artist_id | varchar() | N  |
| rel_artist_artist | genre             | varchar() | N  |
| rel_artist_artist | popularity        | int       | N  |

</center>

This table will have double functionality, the maximum level of atomicity will be at the **genre** level, meaning that if artist A is similar to artist B and has 3 genres: 1,2,3, the table will look like:

<center>

| query_artist_id | similar_artist_id | genre | popularity |
|-----------------|-------------------|-------|------------|
| A               | B                 | 1     | 60         |
| A               | B                 | 2     | 60         |
| A               | B                 | 3     | 60         |

</center>

So to look at the genres that are more close to the query_artis_id = A we will do a SELECT DISTINCT of the column GENRE, whereas if we want to retrieve dual relationships between two artists, we will do a SELECT DISTINCT between the query and the similar artist_id columns. If we want to retrieve all the availables genres, we will only do a SELECT DISTINCT for the GENRE.

- With these tables we are only left to create the graph, which will be explained in the next section.

## 1.2 Data

All the data will come either from scrapping https://kworb.net/ and the Spotify API.


## 1.3 Code

### __00_Database_Creation__

We have connected to the PostGreSQL server, located in /Applications/Postgres.app/Contents/Versions/12/bin/psql. To execute it run:

```bash
psql -p5432 'spotify'

# To get list of tables
\dt

# Get info of table schema
\d <table_name>
```
This notebook contains the scripts to generate the tables from the Spotify database.  

It makes use of the code __db_utils.py__ which is a set of functions that will help to reduce writing code to the basic queries to the PostGreSQL server. 

(CONTINUE)


### __01_Master_Artist_Creation__

This script relies on the __aux_utils.py__ which has the credentials and functions to connect to Spotify API.

1. **GLOBAL ARTISTS**: The extraction from the https://kworb.net/spotify/artists.html of the list of artists is done by means of the **requests** package and information is fetched using **BeautifulSoup**. This is the list of artists that globally appear to be the most listened in Spotify. There are up to 10,000 artists.

2. **COUNTRY SPECIFIC ARTISTS**: A second round of artists retrieval is done by using a country-specific (from Spain) list of artists in the same website in https://kworb.net/spotify/country/es_weekly_totals.html. Most of artists will be present in the previous dataset but there are some that are not (artists which may be very specific from Spain and do not appear in the top artists globally). About 120 artists from the list of 3,615 top artists in Spain are not present in the global list. So we will add them to our list of "main_artists".

3. We identify some other groups both in Spain and in Catalonia that are worth including in the dataset, so they will be added in a different list from the main, since these are "other_artists". 

4. We will search for the artist_id and the tracks of the *other_artists* which were artists popular but not found in kworb dataset. We will do this by using the **spotipy** API functionality "search". Once we found the result, we will realize that it does not return artists but it returns tracks whose artist is similar to the queried one. In order to see which artists is the one that we have queried and to retrieve their artist_id, we will **go over the json returned** and inspect whether we find and artist that matches or is very similar to the queried one. To do so, we will use the **Levenshtein** distance between two strings (from __aux_utils.py__ function).

5. We will put them together and avoid any duplicate entries

6. Use the **executemany** command to allow uploading a list of tuples (the joined dataframe converted to tuples) into the **master_artist** table. Wit this, we will end the artist dataset creation and we are all set to go for the master_track and rel_artist_track in the following notebooks.


### __02_Master_Track_Creation__


This script relies on the __aux_utils.py__ which has the credentials and functions to connect to Spotify API.

The main goal of this script is to perform two tasks to create the **master_track** table:

- Go to kworb database and get the top 30 songs for each artists that we have as "is_main = 1"
- Go to Spotify API and search for the "Top Tracks" (built-in function in Spotipy) (retrieves 10 tracks) for that artist. 

1. Query the **master_artist** table to retrieve all the artists from the previous step. Make 2 dataframes, one for the "is_main = 1" artists and another one for the "other" artists.

2. Query the "kworb" database. Now the queries will be by artist, as they follow always the same structure "https://kworb.net/spotify/artist/<artist_id>.html". We will make one requests per artist, hence we will parse the returned html table. This table is a table of tracks, its peak date, the featuring artists ("With" column) and the number of streams (will be used as a measure of popularity for that song). This table will have then as columns: "Peak Date", "Track", "With", "Streams". Where Track is only the name of the track, in order to find the track_id, we need to parse the "href" for that text. 

3. Since we are looking at the html table, in order to assure that the track_id we retrieve analyzing the href of the table match the name of the track, we will create a dictionary mapping the "Track" (track_name) with the "track_id" (the ID that we will retrieve from the href). This dictionary will be used to create a new column named "track_id" with the track_id already computed in that dataframe for the songs of that artists. Then, we sort the dataframe descendingly by number of Streams and pick the **30 most popular songs for that artist**. 

4. For those songs that are "is_main = 0", we will query the "artist_id" in the Spotify API and retrieve all the results that Spotipy returns (10 most popular tracks per artist). Here, we don't have the Peak Date but we know the "release date" of the album, so we will use it as a proxy for the "Peak Date". Moreover, here we don't have info about the "Streams", hence, to denote that it is a song that is not retrieved from "kworb" but from the Spotify API, in the Streams column we will put a **-1**.

5. We insert each part in the **master_tracks**


### __03_Rel_Artist_Track_Creation__

This script relies on the __aux_utils.py__ which has the credentials and functions to connect to Spotify API.

The main goal of the script is to create the **rel_artist_track**, a table which will serve as a way to know which artist takes part in a song and viceversa, which songs have the same artist. 

1. Do a query in the **master_track** and **master_artist** table. Create a set of artists and a set of tracks (identifiers). This **set_artist** and **set_tracks** will be later used.

2. Do a request to the same URL as we did in the 02 code, that is, go to "https://kworb.net/spotify/artist/<artist_id>.html" and now, instead of only retrieving the track_id, we will retrieve all the **artists that are either the principal artist (<artist_id> of the URL) or any artist that appears in the "With" column of that table**, with the constraint that a given artist_id in the "With" column, must exist in the **master_artist** (be a member of **set_artists**), and the given **track_id** must be in the **set_tracks**, otherwise this track_id or artist_id won't be present in the master tables. 

3. We will impose that a featuring artist can be any artist we have in the **master_artists** (either is_main = 1 or not), but for the tracks, since the is_main = 1 artists' tracks were derived from the kworb database, and we are scrapping this web, it makes more sense to impose that the track_id must be one in the **master_track** where Streams > 0 (as Streams = -1 are for the tracks of the "other" artists tracks). 

4. We create a big dictionary with this schema:
    - Artist_id: opens a new dictionary with tracks as keys
        -Track_id: tracks are keys and each key has a list:
            - Feat artist list: is a list of the artist_id in the "With" column of the table


## 1.4 Problems

- We are running intro problems in Mac with the import of psycopg2. We search for the error: https://stackoverflow.com/questions/57236722/what-does-import-error-symbol-not-found-pqencryptpasswordconn-mean-and-how-do and install two versions lower. FUNCIONA

# 2. Database