import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import random

# Header pour simuler un navigateur
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def get_club_urls(league_url):
    
    """
    Get clubs urls 
    """

    response = requests.get(league_url, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')
    clubs_table = soup.find("table", id="results2024-202591_overall")
    print(clubs_table)
    
    club_links = []
    for row in clubs_table.find_all("tr"):
        first_col = row.find("td", {"data-stat": "team"})
        if first_col and first_col.find("a"):
            link0="https://fbref.com" + first_col.find("a")["href"]
            parts = link0.split('/')
            parts.insert(6, "2024-2025")
            parts.insert(7, "all_comps")
            parts[-1] = parts[-1] + "-All-Competitions"
            link_transformed = "/".join(parts)
            club_links.append(link_transformed)
    
    return club_links

print(get_club_urls("https://fbref.com/en/comps/9/Premier-League-Stats"))

def scrape_club_players(club_url):
   
    """
    Get links for players from the club given by club_url
    """

    time.sleep(random.uniform(1, 3))  # random delay
    
    response = requests.get(club_url, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    players_table = soup.find("table", id="stats_standard_combined")
    
    player_links = []
    for row in players_table.find_all("tr"):
        player_cell = row.find("th", {"data-stat": "player"})
        if player_cell and player_cell.find("a"):
            player_link = player_cell.find("a")["href"]
            
            # Construire l'URL complète
            linkbefore = "https://fbref.com" + player_link
            linkmid = linkbefore.split("/")
            linkmid.insert(6, "all_comps")
            full_url = "/".join(linkmid) + "-Stats---All-Competitions"
            
            player_links.append(full_url)
    
    return player_links

#print(scrape_club_players("https://fbref.com/en/squads/cff3d9bb/2024-2025/all_comps/Chelsea-Stats-All-Competitions"))

def scrape_stats_player(player_url):
    
    """
    Get a player's statistics
    """

    time.sleep(random.uniform(1, 2))  # random delay
    
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
    
    os.makedirs("output", exist_ok=True)
    
    club_urls = get_club_urls(pl_url)
    
    all_players_stats = pd.DataFrame()
    
    for club_url in club_urls:
        print(f"Club treatment : {club_url}")
        
        player_urls = scrape_club_players(club_url)
        
        for player_url in player_urls:
            try:
                player_stats = scrape_stats_player(player_url)
                
                if not player_stats.empty:
                    all_players_stats = pd.concat([all_players_stats, player_stats], ignore_index=True)
                
            except Exception as e:
                print(f"Error : {e}")
        
        # Interim backup
        all_players_stats.to_csv("output/players_stats.csv", index=False)
    
    print("Scraping completed.")

"""if __name__ == "__main__":
    main()"""