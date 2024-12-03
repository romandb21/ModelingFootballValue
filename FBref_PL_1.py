import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import random
import json

# Scraping configuration
CONFIG_FILE = 'scraping_progress.json'

def save_progress(data):
    """Save scraping progress to a JSON file"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f)

def load_progress():
    """Load previous scraping progress"""
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {'last_club': None, 'last_player': None}

def get_club_urls(league_url):
    """Get URLs for all clubs in the league"""
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(league_url, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')
    clubs_table = soup.find("table", id="results2024-202591_overall")
    
    club_links = []
    for row in clubs_table.find_all("tr"):
        first_col = row.find("td", {"data-stat": "team"})
        if first_col and first_col.find("a"):
            link0 = "https://fbref.com" + first_col.find("a")["href"]
            parts = link0.split('/')
            parts.insert(6, "2024-2025")
            parts.insert(7, "all_comps")
            parts[-1] = parts[-1] + "-All-Competitions"
            link_transformed = "/".join(parts)
            club_links.append(link_transformed)
    
    return club_links

def scrape_club_players(club_url):
    """Get player links for a specific club"""
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    time.sleep(random.uniform(3, 7))  # Longer random delay
    
    response = requests.get(club_url, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    players_table = soup.find("table", id="stats_standard_combined")
    
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

def scrape_stats_player(player_url):
    """Get statistics for a specific player"""
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    time.sleep(random.uniform(3, 7))  # Longer random delay
    
    player_name = player_url.split("/")[-1].replace("-Stats---All-Competitions", "").replace("-", " ")
    seasons_to_keep = ['2020-2021', '2021-2022', '2022-2023', '2023-2024', '2024-2025']
    
    response = requests.get(player_url, headers=HEADERS)
    tables = pd.read_html(response.text)
    
    stats_table = tables[1]
    stats_table = stats_table[stats_table[('Unnamed: 0_level_0', 'Season')].isin(seasons_to_keep)]
    
    stats_table[('Unnamed: -1_level_0','Player')] = player_name
    
    new_order = [('Unnamed: -1_level_0', 'Player')] + list(stats_table.columns[:-1])
    stats_table = stats_table[new_order]
    
    return stats_table

def main():
    pl_url = "https://fbref.com/en/comps/9/Premier-League-Stats"
    
    # Create output directory
    os.makedirs("output", exist_ok=True)
    
    # Load previous progress
    progress = load_progress()
    
    club_urls = get_club_urls(pl_url)
    
    # Load existing stats or create new DataFrame
    try:
        all_players_stats = pd.read_csv("output/players_stats.csv")
    except FileNotFoundError:
        all_players_stats = pd.DataFrame()
    
    # Determine starting point for clubs
    start_index = 0
    if progress['last_club']:
        try:
            start_index = club_urls.index(progress['last_club']) + 1
        except ValueError:
            start_index = 0
    
    for club_url in club_urls[start_index:]:
        print(f"Processing club: {club_url}")
        
        try:
            player_urls = scrape_club_players(club_url)
            
            # Determine starting point for players
            start_player_index = 0
            if progress['last_club'] == club_url and progress['last_player']:
                try:
                    start_player_index = player_urls.index(progress['last_player']) + 1
                except ValueError:
                    start_player_index = 0
            
            for player_url in player_urls[start_player_index:]:
                try:
                    player_stats = scrape_stats_player(player_url)
                    
                    if not player_stats.empty:
                        all_players_stats = pd.concat([all_players_stats, player_stats], ignore_index=True)
                    
                    # Save progress
                    save_progress({
                        'last_club': club_url,
                        'last_player': player_url
                    })
                    
                except Exception as e:
                    print(f"Player error: {e}")
                
                # Intermediate save
                all_players_stats.to_csv("output/players_stats.csv", index=False)
        
        except Exception as e:
            print(f"Club error: {e}")
    
    print("Scraping completed.")
    # Remove progress file at the end
    if os.path.exists(CONFIG_FILE):
        os.remove(CONFIG_FILE)

if __name__ == "__main__":
    main()