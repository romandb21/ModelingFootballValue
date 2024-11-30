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
club_url=("https://fbref.com/en/squads/822bd0ba/2024-2025/all_comps/Liverpool-Stats-All-Competitions")
print((club_url.split("/")[-1]).split("-")[0])