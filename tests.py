import requests
from bs4 import BeautifulSoup
import pandas as pd

"""
response = requests.get('https://fbref.com/en/squads/822bd0ba/2024-2025/all_comps/Liverpool-Stats-All-Competitions')
soup = BeautifulSoup(response.text, 'html.parser')

# Trouver la première table sur la page (statistiques des joueurs)
tables = pd.read_html(response.text)

print(tables[0].head())
"""
player_url=("https://fbref.com/en/players/0426b987/all_comps/Ranel-Young-Stats---All-Competitions")
player_name = player_url.split("/")[-1].replace("-Stats---All-Competitions", "").replace("-", " ")
print(player_name)
