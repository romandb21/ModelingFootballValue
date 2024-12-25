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


def rename_columns(df):
    new_columns = []
    for col in df.columns:
        # Si le niveau supérieur commence par "Unnamed", on garde uniquement le niveau inférieur
        if str(col[0]).startswith("Unnamed"):
            new_columns.append(col[1])
        else:
            # Sinon, on combine le niveau supérieur et le niveau inférieur avec ":"
            new_columns.append(f"{col[0]} : {col[1]}")
    
    # Appliquer les nouveaux noms de colonnes
    df.columns = new_columns
    return df


def flatten_columns(df):
    """
    Transforme un DataFrame avec colonnes multi-indexées en colonnes simples
    en prenant uniquement le premier élément des tuples.
    """
    # Vérifie si les colonnes sont des tuples (multi-indexées)
    if isinstance(df.columns, pd.MultiIndex):
        # Remplace les colonnes par le premier élément des tuples
        df.columns = [col[0] for col in df.columns]
    return df



def get_club_urls(league_url, season):
    """Get URLs for all clubs in the league for a specific season"""
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(league_url, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Replace dynamic ID based on the season
    table_id = f"results{season}131_overall"
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
            link_transformed = "/".join(parts)
            club_links.append(link_transformed)
    
    return club_links


def scrape_club_players(club_url):
    """Get player links for a specific club"""
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    time.sleep(random.uniform(3, 4))  # random delay 
    
    response = requests.get(club_url, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    players_table = soup.find("table", id="stats_standard_13")
    
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

        seasons_to_keep = [
            '2010-2011', '2011-2012', '2012-2013', '2013-2014', 
            '2014-2015', '2015-2016', '2016-2017', '2017-2018', 
            '2018-2019', '2019-2020', '2020-2021', '2021-2022', 
            '2022-2023', '2023-2024', '2024-2025'
        ]
        stats_table = stats_table[stats_table[('Unnamed: 0_level_0', 'Season')].isin(seasons_to_keep)]


        # Créer une copie explicite pour éviter le SettingWithCopyWarning
        stats_table = stats_table.copy()

        # Ajouter le nom du joueur
        stats_table.loc[:, ('Unnamed: -1_level_0', 'Player')] = player_name

        # Reorder columns for consistency
        new_order = [('Unnamed: -1_level_0', 'Player')] + list(stats_table.columns[:-1])
        stats_table = stats_table[new_order]
        stats_table = rename_columns(stats_table)
        stats_table = flatten_columns(stats_table)

        return stats_table
    except Exception as e:
        print(f"Error scraping stats for {player_name}: {e}")
        return pd.DataFrame()





def main(season, all_players_stats, existing_players):
    
    L1_url = f"https://fbref.com/en/comps/13/{season}/{season}-Ligue-1-Stats"
    progress = load_progress()
    
    if progress.get('season') != season:
        progress = {'season': season, 'last_club': None, 'last_player': None}
        save_progress(progress)
    
    file_path = "/home/onyxia/work/ModelingFootballValue/players_stats_Big5.csv"
    try:
        existing_data = pd.read_csv(file_path)
        existing_players = set(existing_data['Player'].unique())
    except FileNotFoundError:
        existing_data = pd.DataFrame()
        existing_players = set()
    
    club_urls = get_club_urls(L1_url, season)
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



def main_with_existing_data(season):
    # Load existing data
    file_path = '/home/onyxia/work/ModelingFootballValue/players_stats_Big5.csv'
    try:
        existing_data = pd.read_csv(file_path)
        print(existing_data.columns)
        existing_players = set(existing_data['Player'].unique())
    except FileNotFoundError:
        existing_data = pd.DataFrame()
        existing_players = set()
        existing_data = pd.DataFrame()
        existing_players = set()

    # Initialize all_players_stats with existing data
    all_players_stats = existing_data

    # Scrape new data for the given season
    all_players_stats = main(season, all_players_stats, existing_players)

    # Remove duplicates (if necessary)
    if all_players_stats.duplicated(subset=['Player', 'Season']).any():
        all_players_stats = all_players_stats.drop_duplicates(subset=['Player','Season'])

    # Save the updated dataset back to the original file
    all_players_stats.to_csv(file_path, index=False)


'''
#seasons_list=['2015-2016', '2016-2017', '2017-2018', '2018-2019', '2019-2020', '2020-2021', '2021-2022', '2022-2023', '2023-2024', '2024-2025']
seasons_list=['2020-2021', '2021-2022', '2022-2023', '2023-2024', '2024-2025']
for season in seasons_list:
    main_with_existing_data(season)
'''




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
        existing_players = set(existing_data['Player'].unique())
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



#check_players_in_csv("https://fbref.com/en/squads/d53c0b06/2023-2024/Lyon-Stats", "/home/onyxia/work/ModelingFootballValue/players_stats_L1.csv")



def find_and_print_player_occurrences(player_name, file_path="/home/onyxia/work/ModelingFootballValue/players_stats_L1.csv"):
    """
    Trouve et affiche les lignes où un joueur apparaît dans le fichier CSV.
    
    :param player_name: Nom du joueur à rechercher.
    :param file_path: Chemin du fichier CSV.
    :return: Nombre d'occurrences du joueur.
    """
    try:
        # Charger le fichier CSV avec les en-têtes multi-niveaux
        df = pd.read_csv(file_path, header=[0, 1], low_memory=False)
        
        # Vérifier si la colonne "Player" existe
        if ( 'Unnamed: -1_level_0',    'Player') not in df.columns:
            raise KeyError("La colonne 'Squad' n'existe pas dans le fichier.")
        
        # Filtrer les lignes correspondant au joueur
        club_rows = df[df[( 'Unnamed: -1_level_0',    'Player')] == player_name]
        
        # Afficher le nombre d'occurrences
        occurrences = club_rows.shape[0]
        print(f"Le joueur '{player_name}' apparaît {occurrences} fois dans le fichier.")
        
        # Afficher les lignes où il apparaît
        if occurrences > 0:
            print(club_rows)
        else:
            print(f"Aucune ligne trouvée pour le joueur '{player_name}'.")
        
        return occurrences, club_rows
    except FileNotFoundError:
        print(f"Le fichier '{file_path}' est introuvable.")
        return 0, pd.DataFrame()
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")
        return 0, pd.DataFrame()


#find_and_print_player_occurrences('Bradley Barcola', "/home/onyxia/work/ModelingFootballValue/players_stats_L1.csv")




file_path = "/home/onyxia/work/ModelingFootballValue/players_stats_eredivisie.csv"

ered=pd.read_csv(file_path, header=[0, 1], low_memory=False)
ered=rename_columns(ered)
ered=flatten_columns(ered)

big5= pd.read_csv("/home/onyxia/work/ModelingFootballValue/players_stats_Big5.csv")

# Identifier les colonnes communes
common_columns = ered.columns.intersection(big5.columns)

# Sélectionner ces colonnes
ered_common = ered[common_columns]
big5_common = big5[common_columns]
ered_common = ered_common.loc[:, ~ered_common.columns.duplicated()]



# Concaténation
top6 = pd.concat([ered_common, big5_common], ignore_index=True)

top6 = top6.drop_duplicates(subset= ['Player', 'Season'])
top6 = top6.sort_values(by = 'Player')
top6.to_csv("/home/onyxia/work/ModelingFootballValue/players_stats_top7.csv", index=False)

'''
# Charger tous les fichiers CSV et les concaténer
all_data = pd.concat([pd.read_csv(file, header=[0, 1], low_memory=False) for file in csv_files], ignore_index=True)

# Supprimer les doublons
# Vous pouvez spécifier une ou plusieurs colonnes à utiliser pour détecter les doublons.
# Exemple : all_data.drop_duplicates(subset=[('Unnamed: -1_level_0', 'Player'), ('Unnamed: 0_level_0', 'Season')])
all_data = all_data.drop_duplicates(subset=[('Unnamed: -1_level_0', 'Player'), ('Unnamed: 0_level_0', 'Season')])
all_data = all_data.sort_values(by = ('Unnamed: -1_level_0', 'Player'))

# Sauvegarder dans un nouveau fichier CSV si besoin
all_data.to_csv("/home/onyxia/work/ModelingFootballValue/players_stats_Big5.csv", index=False)

print("Les fichiers ont été concaténés et les doublons supprimés.")

big5 = pd.read_csv("/home/onyxia/work/ModelingFootballValue/players_stats_Big5.csv", header=[0, 1], low_memory=False)



# Exemple d'utilisation
big5 = flatten_columns(big5)



big5.to_csv("/home/onyxia/work/ModelingFootballValue/players_stats_Big5.csv", index=False)



'''

