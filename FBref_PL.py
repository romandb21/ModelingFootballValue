import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import random
import json
import io

# Scraping configuration
CONFIG_FILE = 'scraping_progress.json'

def save_progress(data):
    """Save scraping progress to a JSON file, including the season."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f)



def load_progress():
    """Load previous scraping progress"""
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {'season': None, 'last_club': None, 'last_player': None}



def get_club_urls(league_url, season):
    """Get URLs for all clubs in the league for a specific season"""
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(league_url, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Replace dynamic ID based on the season
    table_id = f"results{season}91_overall"
    clubs_table = soup.find("table", id=table_id)
    
    if not clubs_table:
        raise ValueError(f"Could not find the clubs table with ID: {table_id}")

    club_links = []
    for row in clubs_table.find_all("tr"):
        first_col = row.find("td", {"data-stat": "team"})
        if first_col and first_col.find("a"):
            link0 = "https://fbref.com" + first_col.find("a")["href"]
            parts = link0.split('/')
            parts.insert(6, season)  # Insert the dynamic season
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



def scrape_stats_player(player_url, existing_players):
    """Get statistics for a specific player if not already in the dataset."""
    player_name = player_url.split("/")[-1].replace("-Stats---All-Competitions", "").replace("-", " ")

    if player_name in existing_players:
        print(f"Skipping {player_name} (already exists in the dataset).")
        return pd.DataFrame()

    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    time.sleep(random.uniform(3, 7))

    try:
        response = requests.get(player_url, headers=HEADERS)
        response_text = response.text
        tables = pd.read_html(io.StringIO(response_text))

        # Extract stats and filter by seasons of interest
        stats_table = tables[1]
        seasons_to_keep = ['2020-2021', '2021-2022', '2022-2023', '2023-2024', '2024-2025']
        stats_table = stats_table[stats_table[('Unnamed: 0_level_0', 'Season')].isin(seasons_to_keep)]

        # Créer une copie explicite pour éviter le SettingWithCopyWarning
        stats_table = stats_table.copy()

        # Ajouter le nom du joueur
        stats_table.loc[:, ('Unnamed: -1_level_0', 'Player')] = player_name

        # Reorder columns for consistency
        new_order = [('Unnamed: -1_level_0', 'Player')] + list(stats_table.columns[:-1])
        stats_table = stats_table[new_order]

        return stats_table
    except Exception as e:
        print(f"Error scraping stats for {player_name}: {e}")
        return pd.DataFrame()





def main(season, all_players_stats, existing_players):
    
    pl_url = f"https://fbref.com/en/comps/9/{season}/{season}-Premier-League-Stats"
    progress = load_progress()
    
    if progress.get('season') != season:
        progress = {'season': season, 'last_club': None, 'last_player': None}
        save_progress(progress)
    
    file_path = "/home/onyxia/work/ModelingFootballValue/players_stats_PL.csv"
    try:
        existing_data = pd.read_csv(file_path, header=[0, 1], low_memory=False)
        existing_players = set(existing_data[('Unnamed: -1_level_0', 'Player')].unique())
    except FileNotFoundError:
        existing_data = pd.DataFrame()
        existing_players = set()
    
    club_urls = get_club_urls(pl_url, season)
    all_players_stats = pd.DataFrame()
    
    start_index = 0
    if progress['last_club']:
        try:
            start_index = club_urls.index(progress['last_club']) + 1
        except ValueError:
            start_index = 0
    
    for club_url in club_urls[start_index:]:
        try:
            player_urls = scrape_club_players(club_url)
            
            start_player_index = 0
            if progress['last_club'] == club_url and progress['last_player']:
                try:
                    start_player_index = player_urls.index(progress['last_player']) + 1
                except ValueError:
                    start_player_index = 0
            
            for player_url in player_urls[start_player_index:]:
                player_stats = scrape_stats_player(player_url, existing_players)
                if not player_stats.empty:
                    all_players_stats = pd.concat([all_players_stats, player_stats], ignore_index=True)
                
                save_progress({'season': season, 'last_club': club_url, 'last_player': player_url})
        
        except Exception as e:
            print(f"Erreur pour le club {club_url}: {e}")
    
    print("Scraping terminé.")
    if os.path.exists(CONFIG_FILE):
        os.remove(CONFIG_FILE)
    
    return all_players_stats


def load_existing_data():
    """Load existing players_stats.csv"""
    file_path = "/home/onyxia/work/ModelingFootballValue/players_stats_PL.csv"
    try:
        df = pd.read_csv(file_path, header=[0, 1], low_memory=False)
        print("Loaded with multi-level headers successfully.")
    except Exception as e:
        print(f"Error loading file: {e}")
        df = pd.DataFrame()


def main_with_existing_data(season):
    # Définir le chemin du fichier initial
    file_path = "/home/onyxia/work/ModelingFootballValue/players_stats_PL.csv"
    
    # Charger les données existantes
    try:
        existing_data = pd.read_csv(file_path, header=[0, 1], low_memory=False)
        existing_players = set(existing_data[('Unnamed: -1_level_0', 'Player')].unique())
        print(f"Loaded existing data with {len(existing_data)} rows.")
    except FileNotFoundError:
        existing_data = pd.DataFrame()
        existing_players = set()
        print("No existing data found; starting fresh.")

    # Scraper les nouvelles données pour la saison donnée
    new_data = main(season, all_players_stats=existing_data, existing_players=existing_players)

    # Concaténer les nouvelles données avec les données existantes
    combined_data = pd.concat([existing_data, new_data], ignore_index=True)
    print(f"Data combined. Total rows after concatenation: {len(combined_data)}.")

    # Supprimer les doublons basés sur le joueur et la saison
    initial_count = len(combined_data)
    combined_data = combined_data.drop_duplicates(
        subset=[('Unnamed: -1_level_0', 'Player'), ('Unnamed: 0_level_0', 'Season')],
        keep='last'
    )
    print(f"Removed {initial_count - len(combined_data)} duplicate rows.")

    # Sauvegarder les données combinées dans le fichier CSV initial
    combined_data.to_csv(file_path, index=False)
    print(f"Updated CSV saved to {file_path}.")



main_with_existing_data("2020-2021")


def check_players_in_csv(club_url, csv_path):
    """
    Vérifie si tous les joueurs d'un club sont présents dans le fichier CSV existant.

    Args:
        club_url (str): URL du club à vérifier.
        csv_path (str): Chemin vers le fichier CSV `players_stats_PL.csv`.

    Returns:
        list: Liste des joueurs manquants.
    """
    import pandas as pd
    
    # Charger les données existantes
    try:
        existing_data = pd.read_csv(csv_path, header=[0, 1], low_memory=False)
        existing_players = set(existing_data[('Unnamed: -1_level_0', 'Player')].unique())
        print(f"Loaded {len(existing_players)} players from CSV.")
    except FileNotFoundError:
        print("CSV file not found.")
        return []

    # Scraper les joueurs d'un club (à partir de l'URL)
    try:
        club_players = scrape_club_players(club_url)  # Utiliser la fonction existante pour récupérer les liens
        club_player_names = [url.split("/")[-1].replace("-Stats---All-Competitions", "").replace("-", " ")
                             for url in club_players]
        print(f"Found {len(club_player_names)} players for the club.")
    except Exception as e:
        print(f"Error scraping club players: {e}")
        return []

    # Vérifier quels joueurs ne sont pas présents dans le fichier CSV
    missing_players = [player for player in club_player_names if player not in existing_players]

    # Résultat
    if not missing_players:
        print("All players from the club are present in the CSV.")
    else:
        print(f"Missing {len(missing_players)} players: {missing_players}")
    
    return missing_players

#check_players_in_csv("https://fbref.com/en/squads/361ca564/2021-2022/all_comps/Tottenham-Hotspur-Stats-All-Competitions","/home/onyxia/work/ModelingFootballValue/players_stats_PL.csv")

base) onyxia@vscode-python-566399-0:~/work$ /opt/conda/bin/python /home/onyxia/work/ModelingFootballValue/FBref_L1.py
Error scraping stats for Naoufel El Hannach: No tables found
Error scraping stats for Axel Tape: No tables found
Error scraping stats for Darryl Bakola: No tables found
Error scraping stats for Emmanuel Koum Mbondo: No tables found
Error scraping stats for Rony Mimb Baheng: No tables found
Error scraping stats for Jelle Van Neck: No tables found
