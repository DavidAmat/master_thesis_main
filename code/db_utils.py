import psycopg2
import pandas as pd

def select_table(cursor, table = "", sel_cols = [], direct_query = False):
    
    if len(sel_cols):
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