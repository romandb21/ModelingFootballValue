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

# Load the CSV with multi-level headers
file_path = "/home/onyxia/work/ModelingFootballValue/players_stats.csv"
try:
    df = pd.read_csv(file_path, header=[0, 1], low_memory=False)
    print("Loaded with multi-level headers successfully.")
except Exception as e:
    print(f"Error loading file: {e}")
    df = pd.DataFrame()  # Fallback to an empty DataFrame

player_col = ('Unnamed: -1_level_0', 'Player')
if player_col in df.columns:
    print(f"Player column found: {player_col}")
    existing_players = set(df[player_col].dropna().unique())
    print(f"Loaded {len(existing_players)} existing players.")
else:
    print("Player column not found.")

