
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
| master_track | track_id   | varchar() | Y  |
| master_track | track_name | varchar() | N  |
| master_track | peak_date | date      | N  |
| master_track | streams | bigint      | N  |

</center>

For the songs that come from Spotify API (the songs for the "other_artists" instead of the peak date we have the "release date" which is more or less near in time so we will rely on that). 

- Finally, since one song can have many artists and one artist can have many songs, these relationships will be captured in the **rel_artist_track** table. It is important to state that if a featuring artist is NOT neither in the **master_artist** it will not appear in that table, and obviously, the same for a song that does not appear in the **master_track**. 

<center>

| table            | column    | type      | PK |
|------------------|-----------|-----------|----|
| rel_artist_track | track_id   | varchar() | N  |
| rel_artist_track | artist_id | varchar() | N  |

</center>

Recall that for the songs for the "other_artists" we will search the names of the songs, track_id and the featuring artists by means of the Spotify API. 

- After these information gets stored correctly, we will proceed to use the Spotify API again to retrieve **related artists**. This search, by setting as input an artist_id from the **master_artist** we will be able to get:
    - genres
    - followers
    - artist_name
    - artist_id

of the **similar artists** according to Spotify (popularity, followers and genres are referred to the similar artists, not the queried artist). Then, our task will be to check if any of these artists is present in the **master_artist** and if so, create a table to store those relationships:

<center>

| table             | column            | type      | PK |
|-------------------|-------------------|-----------|----|
| rel_artist_artist | query             | varchar() | N  |
| rel_artist_artist | rel_art           | varchar() | N  |
| rel_artist_artist | genre             | varchar() | N  |
| rel_artist_artist | popularity        | int       | N  |

</center>

This table will have double functionality, the maximum level of atomicity will be at the **genre** level, meaning that if artist A is similar to artist B and has 3 genres: 1,2,3, the table will look like:

<center>

| query | rel_art | genre | popularity |
|-----------------|-------------------|-------|------------|
| A               | B                 | 1     | 60         |
| A               | B                 | 2     | 60         |
| A               | B                 | 3     | 60         |

</center>

So to look at the genres that are more close to the query_artis_id = A we will do a SELECT DISTINCT of the column GENRE, whereas if we want to retrieve dual relationships between two artists, we will do a SELECT DISTINCT between the query and the similar artist_id columns. If we want to retrieve all the availables genres, we will only do a SELECT DISTINCT for the GENRE.

We will do a final table named **master_genre** to store univocally for each artist its gender or inferred gender (see Spotify code 05):

<center>

| table            | column    | type      | PK |
|------------------|-----------|-----------|----|
| master_genre | genre   | varchar() | N  |
| master_genre | artist_id | varchar() | N  |

</center>

- With these tables we are only left to create the graph, which will be explained in the next section.

### Credentials

- Username: david
- Password: pg
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
            - Feat artist list: is a list of the artist_id in the "With" column of the table. Before accepting any artist, we will check in the **set_artists** (both the "main" and "other" artists whether this artist_id exists in our database or not, if does not exist, we will NOT include them). 
            - This is the most time-consuming part, taking more than 1 hour to complete the webscrapping of all the artists top 30 tracks.

5. Convert the dictionary into pairs artist-track to feed the table **rel_artist_track**. 

6. For the **other** artists, since they are not present in the "kworb" dataset, we will query the top 10 tracks via Spotify. Using the Spotipy function "artist_top_tracks" we retrieve the **track_id**.

7. We upload all these pairs to the **rel_artist_track** also. 

### __04_Rel_Artist_Artist_Creation__

In this code we will try to extrack as many information as possible for each artist, retrieving the list of similar artists 100% via Spotipy.

The idea is to feed the table **rel_artist_artist**. We will query one artist and we will retrieve similar artists.

1. Get all the artists in our database (master_artist).

2. Create a set of artists (to search if the related artist is in our database).

3. For each artists, query the Spotipy function "artist_related_artists" and retrieve, for each artist_id similar to the queried one:
    - Popularity
    - A list of genres: loop through all the genres and append to a list all theses properties (popularity, artist_id, genre) for every genre in that list. Recall that the table "rel_artist_artist" has as many rows as genres per artist-artist pair. At each append we make sure that the artist_id of the similar artist **must be in the master_artist table**. We also correct the genre name to avoid characters like " ' " (single quote).

### __05_Rel_Genre_Artist_Creation__

Since the information of gender is provided in the table **rel_artist_artist** and its attributed to the "rel_artist" and not to the queried artist, we suspect that there will be some artists in the "master_artist" that will not have an associated genre. If this is the case we will **infer** the genre of the query artist (that has not been found in the rel_art column and appears in the master_artist), by looking at its rel_art and do a majority voting of the most popular genre among its related artists. If no genre is found, there will be a **undefined** genre for those cases. In case of tie, we will pick randomly the genre among the tied ones.  

The main idea is to create a table **master_genre** to store this information:

<center>

| table            | column    | type      | PK |
|------------------|-----------|-----------|----|
| master_genre | genre   | varchar() | N  |
| master_genre | artist_id | varchar() | N  |

</center>


## 1.4 Problems

- We are running intro problems in Mac with the import of psycopg2. We search for the error: https://stackoverflow.com/questions/57236722/what-does-import-error-symbol-not-found-pqencryptpasswordconn-mean-and-how-do and install two versions lower. FUNCIONA

# 2. Neo4j

## 2.1 Creating a Graph Model

Create a graph model with the password: qrks

- Path import folder: cd /Users/david/Library/Application\ Support/Neo4j\ Desktop/Application/neo4jDatabases/database-f313678c-0e5d-4cf0-bbec-5ee510a4fd59/installation-4.0.4/import
(alias shortcut: neo_import)

- Use the Neo4j Desktop app to create it.

## 2.2 06_Downloading_PostgreSQL_csv

The datasets downloaded from PostgreSQL will be stored in Codigos/Spotify/data/psql_out.
Such downloads are managend through this notebook (title)

### a) Master Track

- Remove the ";" of the track_names

### b) Master Artist

- Since we want our Artists to have a popularity score and not all artists have such score (which comes from the **rel_artist_artist**) we will do the following:

    - Select rel_art, popularity from that table as a DISTINCT table to link each artist with each popularity
    - For those artists in the Master Artists that don't have popularity associated, we will look at all of its rel_art and do the mean of the popularity to assign that popularity to the artist.
    - The resulting dataframe will be the one that will be downloaded as .CSV to feed the Neo4j graph


### c) Master Genre

Select all the genres (distinct) in the master_genre. 

### d) Relationships

We create the relationships querying the corresponding table:

- GEN_ART: genre -> artist_id from master_genre
- ART_TR: artist_id -> track_id from rel_artist_track
- REL_ART: artist_id1 -> artist_id2 from rel_artist_artist (query, rel_art)

All these csv files are stored in **/Users/david/Google Drive/16. Master BigData/5 - Modulos/Modulo 10 - TFM/2. TFM/Codigos/Spotify/data/psql_out**.

**We have to move manually those .csv files to the IMPORT folder for the Database instance created:** 

```bash
/Users/david/Library/Application Support/Neo4j Desktop/Application/neo4jDatabases/database-ada73e8c-396c-4507-82cc-758b5f072ea4/installation-4.0.4/import
```

## 2.3 07_Cypher_Database_Graph_Creation

Once we have added a Database named Spotify to our Project TFM we need  to write the Cypher queries that will read the .csv files in the "import" folder and upload them as nodes and relationships.


<img src="../imgs/img1.png" width="500"/>

### a) Define Database Schema

#### Nodes
- t:Track
    - track_id
    - track_name
    - peak_date
    - streams
- a:Artist
    - artist_id
    - popularity
    - artist_name
    - is_main
    
- g:Genre
    - genre_id

#### Relationships

- GEN_ART: artist - genre
- ART_TR: artist - track
- REL_ART: artist - artist

### b) Add the constraints

- Since we don't want any node to be duplicated in terms of artist_id, track_id or genre, we will add beforehand the constraints regarding such nodes (which do not exist yet):

```cypher
CREATE CONSTRAINT ON (t:Track) ASSERT t.track_id IS UNIQUE 
CREATE CONSTRAINT ON (a:Artist) ASSERT a.artist_id IS UNIQUE 
CREATE CONSTRAINT ON (g:Genre) ASSERT g.genre_id IS UNIQUE 
```
This is done because when doing a MERGE, Cypher has to check if that node already exists, so INDEXING its property of ID (track_id, artist_id, genre_id) will ease that task and reduce LOAD time.

### c) Artists

Upload the artist nodes taking into account that "popularity" is an integer and "is_main" should be a boolean, not a "True" / "False" string!

```cypher
LOAD CSV WITH HEADERS FROM "file:///master_artist.csv" AS line FIELDTERMINATOR ';'
MERGE (a:Artist {  
                    artist_id: line.artist_id,
                    artist_name: line.artist_name,
                    popularity: toInteger(line.popularity),
                    is_main: (case line.is_main when 'True' then true else false end)
                     })
```

### d) Tracks

Here we have to remember to convert the peak_date string to a date and streams to integer:

```cypher
LOAD CSV WITH HEADERS FROM "file:///master_track.csv" AS line FIELDTERMINATOR ';'
MERGE (t:Track {  
                    track_id: line.track_id,
                    track_name: line.track_name,
                    streams: toInteger(line.streams),
                    peak_date: date(line.peak_date)
                     })
```


### d) Genre

Finally, we add the genre names as genre_id, since those are simply strings and a ID will not help in easing the identification of genres, which are only 1,000 strings more or less.

### e) Create index on names

After all nodes have been added with its properties, now we can set an index for the artists and track names to ease querying by a certain name.

```cypher
CREATE INDEX ArtistName FOR (a:Artist) ON (a.artist_name) 
CREATE INDEX TrackName FOR (t:Track) ON (t.track_name) 
```

### f) Add the relationships

Here we add the 3 relationships that we have presented before:

```cypher
LOAD CSV WITH HEADERS FROM "file:///rel_GEN_ART.csv" AS line FIELDTERMINATOR ';' 
    MATCH (g:Genre {genre_id: line.genre})
    MATCH (a:Artist {artist_id: line.artist_id})
    MERGE (g)-[:GEN_ART]->(a)
```

```cypher
LOAD CSV WITH HEADERS FROM "file:///rel_ART_TR.csv" AS line FIELDTERMINATOR ';' 
    MATCH (a:Artist {artist_id: line.artist_id})
    MATCH (t:Track {track_id: line.track_id})
    MERGE (a)-[:ART_TR]->(t)
```

```cypher
LOAD CSV WITH HEADERS FROM "file:///rel_REL_ART.csv" AS line FIELDTERMINATOR ';' 
    MATCH (a1:Artist {artist_id: line.artist_id1})
    MATCH (a2:Artist {artist_id: line.artist_id2})
    MERGE (a1)-[:REL_ART]->(a2)
```

### g) BackUp

We finally do a BackUp to store in the "import" folder a .bk copy of the actual database.


## 2.4 08_Graph_Analysis

Contains the most used queries to validate that everything has been added properly.

Example:
```cypher
// Most Streamed songs, getting artist and genre
MATCH (a:Artist)-[:ART_TR]->(t:Track)
WITH a, t
ORDER BY t.streams DESC
LIMIT 20
MATCH (g:Genre)-[:GEN_ART]->(a:Artist)
RETURN a, g, t                  
```


## 2.5 09_Neo4j_Python_Connection

We install "py2neo" to query the Spotify Database with a python driver.
We can retrieve the results in a dataframe.


## 2.6 10_Create_List_Song_Artist_Query_Youtube

Now is a crucial step, we need to decide if we are going to download all songs or just a few. The idea is that if we manage to download all audios, we will be able to select as many songs as we want for each artist when training the neural network, otherwise, if we need more data we will be stucked and need to re-run again this code to generate a much wider list of artist-track.

Data is exported to /Spotify/data/01_queries_yt where there is a .csv named queries.csv that will be the file that will take the queue for sending jobs to each instance.

# 3. AWS

## 3.1 PuTTY

Using XQuartz, launch a terminal and put tfm, navigate to the folder where the .pem exist and convert it to .ppk:

```bash
sudo puttygen TFM_London.pem -o TFM_London.ppk -O private
```

## 3.2 AWS Parallel Cluster

1. Create a new user:

- User: tfm

- Enable Programmatic access

- Credentials:
    Look in Codigos/credentials/user_tfm

2. Install both parallel cluster and awscli python packages in the Codigos/AWS folder (which is linked with a different pipenv). 

3. Parallel Cluster configuration is written in /Users/david/.parallelcluster/config

4. Now we are going to test which configuration does the instance needs to initialize with selenium downloaded.

### 3.2.1 Install Selenium on a t2.small

- Named: test_selenium
- SSH into it (assuming we are on the /Codigos/AWS directory)

```bash
# First protect the .pem file (only the first time)
chmod 400 TFM_London.pem

# Run the command
tfm
cd AWS/
ssh -i "../credentials/AWS_KeyPair_London/TFM_London.pem" ec2-user@ec2-35-179-75-206.eu-west-2.compute.amazonaws.com
```

Inside the **test_selenium** instance do:

```bash
sudo su
sudo yum update -y

# Install python 3.7 and pipenv
sudo yum install python37

# Get pip
curl -O https://bootstrap.pypa.io/get-pip.py

#Run it
python3 get-pip.py --user

#Install pipenv
sudo pip3 install pipenv

#Add pipenv to path
export PATH=/usr/local/bin:$PATH

# But is better to modify the ~/.bashrc file and add this
# this will enable localization of the pipenv in the PATH variable
export PATH=/usr/local/bin:$PATH

# mkdir scrap
mkdir scrap

# This time we will not download the pipfile from the github repo
# what we will do is to download the package by our own
pipenv shell

touch requirements.txt
nano requirements.txt

# Copy and paste this list
pipenv install pandas==1.0.5
pipenv install numpy==1.19.0
pipenv install tqdm==4.46.1
pipenv install boto3==1.14.12
pipenv install v_log==1.0.1
pipenv install awscli
pipenv install jupyter

# Configure the AWS credentials for the London region
aws configure

# Change the Security Group Inbound rule for TCP in port range 8888
# since we will need to acces through Jupyter

# Go to the sg and create a Custom TCP for port 8888 for source 0.0.0.0/0

# Generate the config to allow running jupyter notebook and accessing through another IP
pipenv run jupyter notebook --generate-config

# Configuration is written in /root/.jupyter/jupyter_notebook_config.py
# Edit it
vi /root/.jupyter/jupyter_notebook_config.py
/
c.NotebookApp.ip = '*'

# Save and quit. Now run finnaly:
pipenv run jupyter notebook --no-browser --allow-root

# Copy the http and change the DNS for the IP (in our local browser)
http://ip-172-31-5-84.eu-west-2.compute.internal:8888/?token=e63b5cb4248372d1f8fd35c88bdddfbb4741ca279a75b740

# Change it to
http://35.179.75.206:8888/?token=e63b5cb4248372d1f8fd35c88bdddfbb4741ca279a75b740

# INSTALL SELENIUM

## Install chromedriver
sudo su
yum -y install libX11 
cd /tmp/
sudo wget https://chromedriver.storage.googleapis.com/83.0.4103.39/chromedriver_linux64.zip
sudo unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/bin/chromedriver
chromedriver --version
# IMPORTANT! make SURE that the chromedriver version matchs the google-chrome --version below

## Install binary Google Chrome
sudo curl https://intoli.com/install-google-chrome.sh | bash
sudo mv /usr/bin/google-chrome-stable /usr/bin/google-chrome 
google-chrome --version && which google-chrome
#IMPORTANT! make SURTE this version of google chrome matches the chromedriver

## Install Selenium
#su ec2-user #change user and go to the scrap/ folder and run
pipenv shell
pipenv install selenium
```

We can try a Python Script to check that it works:

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options

#Selenium options
options = Options()
options.add_argument("--headless")
options.add_argument("window-size=1400,1500")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("start-maximized")
options.add_argument("enable-automation")
options.add_argument("--disable-infobars")
options.add_argument("--disable-dev-shm-usage")

url = 'https://github.com/'

driver = webdriver.Chrome(options=options)

# Navigate to github.com
driver.get(url)

# Extract the top heading from github.com
text = driver.find_element_by_class_name('h000-mktg').text

print(text)
```

### 3.2.2 FileZilla to transfer the queries.csv

We need inside this instance the file in which we have all the artists and tracks to search for. Hence, we will connect to the EC2 instance with FileZilla:

- First add the key file as they say in here:

https://stackoverflow.com/questions/16744863/connect-to-amazon-ec2-file-directory-using-filezilla-and-sftp

- What it is not explained is that you have to go to the File > Site Manager Add and choose:
    - Protocolo: SFTP - SSH File Transfer Protocol
    - Servidor: <paste_here_the_DNS_of_the_instance>
    - Puerto: leave as empty
    - Modo de acceso: Archivo de claves
    - Usuario: ec2-user
    - Archivo de claves: select the .pem file

- Drag and drop the queries.csv file in the /Spotify/data/01_queries_yt (created in the 2.6 Section: 10_Create_List_Song_Artist_Query_Youtube)

- We will create a directory named "/data" inside the "scrap" folder in the EC2 instance. Since the folder is created with the "root" user, we will not be able to drag and drop to data/. Hence, we drag and drop to the ec2-user folder and then in the terminal, as root, we will move the queries.csv to the data/ folder.