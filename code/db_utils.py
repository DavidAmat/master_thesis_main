import psycopg2
import pandas as pd


# Select anything from a table
def select_table(cursor, table = "", sel_cols = [], direct_query = False):
    
    if len(sel_cols) and len(table):
        columns_selected = ", ".join(sel_cols)
        query = f""" SELECT {columns_selected} FROM {table} """
    elif direct_query:
        query = direct_query
    else:
        query = f""" SELECT * FROM {table} """
        
    # Execute query
    cursor.execute(query)
    df_out = cursor.fetchall()
    
    if len(sel_cols):
        df_out = pd.DataFrame(df_out, columns = sel_cols)
    else:
        df_out = pd.DataFrame(df_out)
        
    return df_out

def artID(cursor, art_name):  
    query = f""" SELECT artist_id, artist_name from master_artist where artist_name like '%{art_name}%'  """
    cursor.execute(query)
    df_out = cursor.fetchall()
    df_out = pd.DataFrame(df_out, columns = ["artist_id", "artist_name"])
    return df_out

def songsArt(cursor, art_ID):
    query = f""" SELECT  track_id from rel_artist_track where artist_id = '{art_ID}'"""
    cursor.execute(query)
    df_out = cursor.fetchall()
    df_out = pd.DataFrame(df_out, columns = ["track_id"])
    return df_out

def SongNames(cursor, track_ID):
    query = f""" SELECT * from master_track where track_id  = '{track_ID}' """
    cursor.execute(query)
    df_out = cursor.fetchall()
    df_out = pd.DataFrame(df_out, columns = ["track_id", "track_name", "peak_date", "streams"])
    return df_out

def Songs_of_Artist(cursor, art_name):
    artist_ID = artID(cursor, art_name).values[0][0]
    trck_list = list(songsArt(cursor, artist_ID)["track_id"])
    songs = [SongNames(cursor, tr).values[0].tolist() for tr in trck_list]
    df_songs = pd.DataFrame(songs, columns = ["track_id", "track_name", "peak_date", "streams"])
    return df_songs
    
    
    