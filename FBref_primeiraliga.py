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
    table_id = f"results{season}321_overall"
    clubs_table = soup.find("table", id=table_id)
    
    if not clubs_table:
        raise ValueError(f"Could not find the clubs table with ID: {table_id}")

    club_links = []
    for row in clubs_table.find_all("tr"):
        first_col = row.find("td", {"data-stat": "team"})
        if first_col and first_col.find("a"):
            link0 = "https://fbref.com" + first_col.find("a")["href"]
            club_links.append(link0)
    
    return club_links

#print(get_club_urls("https://fbref.com/en/comps/12/La-Liga-Stats", "2024-2025"))

def scrape_club_players(club_url):
    """Get player links for a specific club"""
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    time.sleep(random.uniform(3, 4))  # random delay
    
    response = requests.get(club_url, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    players_table = soup.find("table", id="stats_standard_32")
    
    if not players_table:
        print(f"Warning: no players table for {club_url} ")
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
    time.sleep(random.uniform(3, 4)) # random delay

    try:
        response = requests.get(player_url, headers=HEADERS)
        soup = BeautifulSoup(response.text, 'html.parser')
        stats_table = soup.find("table", id="stats_standard_expanded")
        
        if stats_table is None:
            stats_table = soup.find("table", id="stats_standard_dom_lg")
            
        if stats_table is None:
            print(f"No stats table found for URL: {player_url}")
            return pd.DataFrame()

        # Convertir le tableau HTML en DataFrame
        try:
            stats_table_html = str(stats_table)  # Convertir en chaîne
            stats_table = pd.read_html(io.StringIO(stats_table_html), header=[0, 1])[0]
        except ValueError as e:
            print(f"Error reading HTML table for {player_name}: {e}")
            return pd.DataFrame()

        # Créer une copie explicite pour éviter le SettingWithCopyWarning
        stats_table = stats_table.copy()

        # Ajouter le nom du joueur
        stats_table.loc[:, ('Unnamed: -1_level_0', 'Player')] = player_name

        # Reorder columns for consistency
        new_order = [('Unnamed: -1_level_0', 'Player')] + list(stats_table.columns[:-1])
        stats_table = stats_table[new_order]

        # **Ajout du filtre avec une liste de saisons**
        # Définir la liste des saisons autorisées
        allowed_seasons = [
            '2010-2011', '2011-2012', '2012-2013', '2013-2014', 
            '2014-2015', '2015-2016', '2016-2017', '2017-2018', 
            '2018-2019', '2019-2020', '2020-2021', '2021-2022', 
            '2022-2023', '2023-2024', '2024-2025'
        ]

        # Identifier la colonne de saison (par exemple : ('Unnamed: 0_level_0', 'Season'))
        season_column = ('Unnamed: 0_level_0', 'Season')
        if season_column in stats_table.columns:
            stats_table = stats_table[
                stats_table[season_column].isin(allowed_seasons)
            ]

        return stats_table
    except Exception as e:
        print(f"Error scraping stats for {player_name}: {e}")
        return pd.DataFrame()


 

def main(season, all_players_stats, existing_players):
    """
    Main function to scrape stats for a specific season, resuming from saved progress.
    """
    primeira_url = f"https://fbref.com/en/comps/32/{season}/{season}-Primeira-Liga-Stats"
    progress = load_progress()

    # Mettre à jour la saison si nécessaire
    if progress.get('season') != season:
        progress = {'season': season, 'last_club': None, 'last_player': None}
        save_progress(progress)

    file_path = "/home/onyxia/work/ModelingFootballValue/players_stats_primeiraliga.csv"

    # Charger les données existantes
    try:
        existing_data = pd.read_csv(file_path, header=[0, 1], low_memory=False)
        existing_players = set(existing_data[('Unnamed: -1_level_0', 'Player')].unique())
    except FileNotFoundError:
        existing_data = pd.DataFrame()
        existing_players = set()

    # Récupérer les URL des clubs
    club_urls = get_club_urls(primeira_url, season)
    all_players_stats = pd.DataFrame()

    # Identifier le point de reprise pour les clubs
    start_club_index = 0
    if progress['season'] == '2020-2021' and progress['last_club']:
        normalized_last_club = progress['last_club'].split("/squads/")[1].split("/")[0]  # Extraire l'identifiant unique du club
        try:
        # Trouver le club avec le même identifiant dans la liste
            for i, club_url in enumerate(club_urls):
                if f"/squads/{normalized_last_club}/" in club_url:
                    start_club_index = i
                    print(f"Reprise à partir du club index {start_club_index}: {club_url}")
                    break  # Arrêter la boucle une fois qu'une correspondance est trouvée
                else:
                    print("Aucun club correspondant trouvé. Reprise depuis le début.")
                    start_club_index = 0
        except Exception as e:
            print(f"Erreur lors de la recherche du club: {e}")
            start_club_index = 0

    for club_url in club_urls[start_club_index:]:
        try:
            print(f"Scraping club: {club_url}")
            player_urls = scrape_club_players(club_url)

            # Identifier le point de reprise pour les joueurs
            start_player_index = 0
            if progress['season'] == season and progress['last_club'] == club_url and progress['last_player']:
                try:
                    start_player_index = player_urls.index(progress['last_player'])
                    print(f"Reprise à partir du joueur index {start_player_index}: {progress['last_player']}")
                except ValueError:
                    print("Le joueur de progression n'a pas été trouvé. Reprise depuis le début.")
                    start_player_index = 0

            for player_url in player_urls[start_player_index:]:
                print(f"Scraping player: {player_url}")
                player_stats = scrape_stats_player(player_url, existing_players)
                if not player_stats.empty:
                    all_players_stats = pd.concat([all_players_stats, player_stats], ignore_index=True)

                # Sauvegarder la progression après chaque joueur
                save_progress({'season': season, 'last_club': club_url, 'last_player': player_url})

        except Exception as e:
            print(f"Error for club {club_url}: {e}")

    print("Scraping terminé.")
    if os.path.exists(CONFIG_FILE):
        os.remove(CONFIG_FILE)

    return all_players_stats



def main_with_existing_data(season):
    # Load existing data
    file_path = "/home/onyxia/work/ModelingFootballValue/players_stats_primeiraliga.csv"
    try:
        existing_data = pd.read_csv(file_path, header=[0, 1], low_memory=False)
        existing_players = set(existing_data[('Unnamed: -1_level_0', 'Player')].unique())
    except FileNotFoundError:
        existing_data = pd.DataFrame()
        existing_players = set()

    # Initialize all_players_stats with existing data
    all_players_stats = existing_data

    # Scrape new data for the given season
    all_players_stats = main(season, all_players_stats, existing_players)

    # Remove duplicates (if necessary)
    if all_players_stats.duplicated(subset=[('Unnamed: -1_level_0', 'Player'), ('Unnamed: 0_level_0', 'Season')]).any():
        all_players_stats = all_players_stats.drop_duplicates(subset=[('Unnamed: -1_level_0', 'Player'), ('Unnamed: 0_level_0', 'Season')])

    # Save the updated dataset back to the original file
    all_players_stats.to_csv(file_path, index=False)



for season in ['2015-2016', '2016-2017', '2017-2018', '2018-2019', '2019-2020', '2020-2021', '2021-2022', '2022-2023', '2023-2024', '2024-2025']:
    main_with_existing_data(season)




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


