import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import random
import json
import io


primeira_path = 'scraping_data/results_csv/players_stats_primeiraliga.csv'
top5_path = 'scraping_data/results_csv/players_stats_top5.csv'
eredivisie_path = 'scraping_data/results_csv/players_stats_eredivisie.csv'


top5= pd.read_csv(top5_path, low_memory=False)
primeira=pd.read_csv(primeira_path, low_memory=False)
eredivisie=pd.read_csv(eredivisie_path, low_memory=False)

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
top7.to_csv('scraping_data/results_csv/players_stats_top7.csv', index=False)

