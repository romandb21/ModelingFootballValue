import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import io
import random
import json

HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
response = requests.get('https://fbref.com/en/players/bf5948ea/Lorenzo-Lucchesi', headers=HEADERS)
response_text = response.text
tables = pd.read_html(io.StringIO(response_text))

# Extract stats and filter by seasons of interest
stats_table = tables[1]


print(stats_table)
"""
def scrape_club_players(club_url):
    
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    time.sleep(random.uniform(3, 7))  # Longer random delay
    
    response = requests.get(club_url, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    players_table = soup.find("table", id="stats_standard_combined")
    
    if not players_table:
        print(f"Warning: No player table found for club {club_url}")
        return []

    player_links = []
    for row in players_table.find_all("tr"):
        player_cell = row.find("th", {"data-stat": "player"})
        if player_cell and player_cell.find("a"):
            player_link = player_cell.find("a")["href"]
            
            # Build complete URL
            linkbefore = "https://fbref.com" + player_link
            linkmid = linkbefore.split("/")
            linkmid.insert(6, "all_comps")
            full_url = "/".join(linkmid) + "-Stats---All-Competitions"
            
            player_links.append(full_url)
    
    return player_links

print(scrape_club_players("https://fbref.com/en/squads/361ca564/2021-2022/all_comps/Tottenham-Hotspur-Stats-All-Competitions"))
"""