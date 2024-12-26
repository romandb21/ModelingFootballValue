import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import random
import json
import io




top5= pd.read_csv("/home/onyxia/work/ModelingFootballValue/players_stats_top5.csv", low_memory=False)
primeira=pd.read_csv("/home/onyxia/work/ModelingFootballValue/players_stats_primeiraliga.csv", low_memory=False)
eredivisie=pd.read_csv("/home/onyxia/work/ModelingFootballValue/players_stats_eredivisie.csv", low_memory=False)


# Keep common columns
common_columns = primeira.columns.intersection(top5.columns)


primeira_common = primeira[common_columns]
eredivisie_common = eredivisie[common_columns]
top5_common = top5[common_columns]


# Delete duplicated columns
primeira_common = primeira_common.loc[:, ~primeira_common.columns.duplicated()]
eredivisie_common = eredivisie_common.loc[:, ~eredivisie_common.columns.duplicated()]
top5_common = top5_common.loc[:, ~top5_common.columns.duplicated()]

# union of the 3 dataframes into top7 dataframe
top7= pd.concat([primeira_common, top5_common], ignore_index=True)
top7= pd.concat([eredivisie_common, top7], ignore_index=True)

# Deleting the duplicated (player, saison) and sorting by players
top7 = top7.drop_duplicates(subset = ['Player', 'Season'])
top7 = top7.sort_values(by = 'Player')

# save into a csv
top7.to_csv("/home/onyxia/work/ModelingFootballValue/players_stats_top7.csv", index=False)


# count players 
def count_players(file_path):
    players_per_season = df.groupby(('Season'))[('Player')].nunique()
    players = df[('Player')].nunique()
    return(players, players_per_season)