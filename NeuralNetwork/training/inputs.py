import pandas as pd
import numpy as np
import os
import sys
from collections import Counter, defaultdict
import matplotlib.pyplot as plt
import tqdm
import cv2
import keras

from paths import *

# Spectogram files
data_files = os.listdir(PATH_DATA)


# ..............................................................................................
# ..............................................................................................

#                           Triplets

# ..............................................................................................
# ..............................................................................................


# Load triplets
df = pd.read_csv(PATH_TRIPLETS, delimiter= ";")

# List
triplets_input = list(df["output"])
size_triplets_input = len(triplets_input)

# Sample
triplets_input_v1 = triplets_input[:1000]
size_triplets_input = len(triplets_input_v1)

# Artists
artists_labels = np.sort(df.a1.unique())
df_artists = pd.DataFrame(data = artists_labels, columns = ["artist"]).reset_index()
df_artists.columns = ["id","artist"]

# DF Artists with artists as index
df_artists_index = df_artists.set_index("artist")
num_artists = df_artists.shape[0]

########################
#  Artists
########################
# Load artists and tracks
dfneo = pd.read_csv(PATH_NEO, sep = ";")
if ARTIST_CLASS == "catalan":
    
    # Set of artists
    set_art_cat = set()
    for ii, row in dfneo.iterrows():
        set_art_cat.add(row["a.artist_id"])
        set_art_cat.add(row["a2.artist_id"])
    sel_art = list(set_art_cat)
    df_artists_cat = df_artists[df_artists.artist.isin(set_art_cat)]["artist"].reset_index()
    df_artists_cat["id"] = df_artists_cat.index
    df_artists_cat.drop('index', axis=1, inplace = True)
else:
    set_art_cat = list(dfneo["artist"])
    df_artists_cat = df_artists[df_artists.artist.isin(set_art_cat)]["artist"].reset_index()
    df_artists_cat["id"] = df_artists_cat.index
    df_artists_cat.drop('index', axis=1, inplace = True)

# ..............................................................................................
# ..............................................................................................

#                           Labels

# ..............................................................................................
# ..............................................................................................

# Create final vector for the labels of each artist (target of the model)
df_artists_gen = df_artists_cat.copy()
labels_mat = keras.utils.to_categorical(df_artists_gen.id)
labels = dict()
for i, row in df_artists_gen.iterrows():
    labels[row.artist] = labels_mat[row.id,].astype(int)
    
# Number of different artists
num_artists = len(labels.keys())


# ..............................................................................................
# ..............................................................................................

#                           Songs

# ..............................................................................................
# ..............................................................................................

# Select artists that are in the set of the selected artists
df_gen = df[df.a1.isin(set_art_cat)]

# Create a dataframe with such columns
df1 = df_gen[["a1","tr1","win1","ini1","fin1"]].copy()
df2 = df_gen[["a1","tr2","win2","ini2","fin2"]].copy()

# Column names
colnames = ["art","tr","win","ini","fin"]
df1.columns = colnames
df2.columns = colnames

# Remove duplicates
df_concat = pd.concat([df1, df2])
df_concat.drop_duplicates(inplace = True)

# Create the name of the track as the concatenation of the track name, the window, the initial state and final state
df_concat["tr"] = df_concat.tr + "__" + df_concat.win.astype(str) +  \
    "__" + df_concat.ini.astype(str) + "__" + df_concat.fin.astype(str) + ".jpg"

# reset index
df_concat = df_concat.reset_index().drop("index", axis = 1)




