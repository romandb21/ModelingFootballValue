import requests
from bs4 import BeautifulSoup
import pandas as pd

# Premier League players 2024-2025:

pl_url = "https://fbref.com/en/comps/9/Premier-League-Stats"

def get_club_urls(league_url):
    """
    Get all clubs in the league given by league_url
    """
    response = requests.get(league_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the table with all clubs 
    clubs_table = soup.find("table", id="results2024-202591_overall")
    
    # Get links from the first column of the table (these are the url for each clubs)
    club_links = []
    for row in clubs_table.find_all("tr"):
        first_col = row.find("td", {"data-stat": "team"})
        if first_col:
            link = first_col.find("a")
            if link:
                club_links.append("https://fbref.com" + link["href"] + "-All-Competitions")

    return club_links




def scrape_club_players(club_url):
    
    """
    Get the links for all players of the club given by club_url in FBref
    """
    
    response = requests.get(club_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Get the table that contains all players
    players_table = soup.find("table", id="stats_standard_combined")
    if not players_table:
        print("Players table not found!")
        return []

    # List to keep players links
    player_links = []
    for row in players_table.find_all("tr"):
        player_cell = row.find("th", {"data-stat": "player"})  # Trouver la cellule "player"
        if player_cell and player_cell.find("a"):
            player_link = player_cell.find("a")["href"]  # Extraire le lien
            linkbefore = "https://fbref.com" + player_link
            linkmid = linkbefore.split("/")
            linkmid.insert(6, "all_comps")
            full_url = "/".join(linkmid) + "-Stats---All-Competitions"
            player_links.append(full_url)

    return player_links

 
# print (scrape_club_players("https://fbref.com/en/squads/822bd0ba/2024-2025/all_comps/Liverpool-Stats-All-Competitions"))

def scrape_stats_player(player_url):

    """
    Get the statistics for the player given by player_url in FBref
    """

    response = requests.get(player_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Get the table that contains the player's stats
    tables = pd.read_html(response.text)
    stats_table=tables[1]
        
    return(stats_table)

#print(scrape_stats_player("https://fbref.com/en/players/e06683ca/all_comps/Virgil-van-Dijk-Stats---All-Competitions").head())

