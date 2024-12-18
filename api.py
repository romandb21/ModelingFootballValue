import requests
import pandas as pd
import matplotlib.pyplot as plt

# Details for the utilization of API
API_KEY = "7fee06d41d0344a7b06b6907341c8a2b"
BASE_URL = "https://api.football-data.org/v4"

''' Definition of a function which creates a dataframe with information on all the teams of the
 chosen league. '''


def get_teams(competition_id):
    url = f"{BASE_URL}/competitions/{competition_id}/teams"
    headers = {"X-Auth-Token": API_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        teams = response.json()["teams"]  # list with all the teams of the league
    else:
        print(f"Error fetching teams: {response.status_code} - {response.text}")
        return []
    teams_list = []
    for team in teams:
        teams_list.append({  # all the information we want from the information set
            "Team ID": team["id"],
            "Team Name": team["name"],
            "Short Name": team["shortName"],
            "Area": team["area"]["name"],
            "Founded": team.get("founded", "N/A"),
            "Stadium": team.get("venue", "N/A")
        })
    teams_df = pd.DataFrame(teams_list)
    print(teams_df)


''' Definition of a function which creates a dataframe with information on all the players of the
chosen team. '''


def get_players(team_id):
    url = f"{BASE_URL}/teams/{team_id}"
    headers = {"X-Auth-Token": API_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        squad = response.json()["squad"]  # all the players of the team
        team_data = response.json()
        team = team_data.get("name", "Unknown Team") 
        # method to get the name of the team which is not included 
        # in the information set of the players
    else:
        print(f"Error fetching teams: {response.status_code} - {response.text}")
        return []
    players_list = []
    for player in squad:
        players_list.append({  # all the information we need
            "Player Name": player["name"],
            "Position": player["position"],
            "Date of Birth": player.get("dateOfBirth", "N/A"),
            "Nationality": player.get("nationality", "N/A"),
            "Team Name": team,
            "Market Value ": player.get("marketValue", "N/A")
            # with the free plan we cannot obtain the market value
        })
    players_df = pd.DataFrame(players_list)
    print(players_df)


# Configuration du terrain
def draw_pitch():
    plt.figure(figsize=(8, 12))  # Dimensions du terrain
    plt.plot([0, 100], [0, 0], color="black")  # Ligne de but bas
    plt.plot([0, 0], [0, 100], color="black")  # Ligne de touche gauche
    plt.plot([100, 100], [0, 100], color="black")  # Ligne de touche droite
    plt.plot([0, 100], [100, 100], color="black")  # Ligne de but haut

    # Surface de réparation (haut et bas)
    plt.plot([20, 80], [90, 90], color="black")
    plt.plot([20, 80], [10, 10], color="black")
    plt.plot([20, 20], [90, 100], color="black")
    plt.plot([80, 80], [90, 100], color="black")
    plt.plot([20, 20], [0, 10], color="black")
    plt.plot([80, 80], [0, 10], color="black")

    # Ligne médiane
    plt.plot([50, 50], [0, 100], color="black")

    # Cercle central
    circle = plt.Circle((50, 50), 10, color="black", fill=False)
    plt.gca().add_patch(circle)

    # Paramètres généraux
    plt.xlim(0, 100)
    plt.ylim(0, 100)
    plt.axis("off")  # Masquer les axes


# Positions des joueurs pour une formation 4-3-3
positions = {
    "Goalkeeper": [(50, 5)],
    "Defender": [(20, 20), (40, 20), (60, 20), (80, 20)],
    "Midfielder": [(30, 50), (50, 50), (70, 50)],
    "Forward": [(30, 80), (50, 80), (70, 80)],
}

# Exemple de joueurs par poste
players = {
    "Goalkeeper": ["Player 1"],
    "Defender": ["Player 2", "Player 3", "Player 4", "Player 5"],
    "Midfielder": ["Player 6", "Player 7", "Player 8"],
    "Forward": ["Player 9", "Player 10", "Player 11"],
}


# Dessiner le terrain et les joueurs
def draw_team(players, positions):
    draw_pitch()
    for role, coords in positions.items():
        for i, coord in enumerate(coords):
            player_name = players[role][i] if i < len(players[role]) else "Unknown"
            x, y = coord
            plt.text(x, y, player_name, fontsize=10, ha="center", va="center", bbox=dict(boxstyle="round,pad=0.3", edgecolor="black", facecolor="white"))
    plt.show()


# Afficher l'équipe
draw_pitch()


# Exemple de données : joueurs et leurs positions
players = [
    {"name": "Goalkeeper 1", "position": "Goalkeeper"},
    {"name": "Defender 1", "position": "Defender"},
    {"name": "Defender 2", "position": "Defender"},
    {"name": "Defender 3", "position": "Defender"},
    {"name": "Defender 4", "position": "Defender"},
    {"name": "Midfielder 1", "position": "Midfielder"},
    {"name": "Midfielder 2", "position": "Midfielder"},
    {"name": "Midfielder 3", "position": "Midfielder"},
    {"name": "Midfielder 4", "position": "Midfielder"},
    {"name": "Forward 1", "position": "Forward"},
    {"name": "Forward 2", "position": "Forward"},
]

# Formation: 4-4-2
formation = {
    "Goalkeeper": [(5, 10)],  # x, y position
    "Defender": [(2, 7), (4, 7), (6, 7), (8, 7)],
    "Midfielder": [(2, 5), (4, 5), (6, 5), (8, 5)],
    "Forward": [(3, 3), (7, 3)],
}


# Fonction pour dessiner le terrain
def draw_pitch():
    plt.plot([0, 10], [0, 0], color="black")  # Ligne de but bas
    plt.plot([0, 10], [10, 10], color="black")  # Ligne de but haut
    plt.plot([0, 0], [0, 10], color="black")  # Ligne de touche gauche
    plt.plot([10, 10], [0, 10], color="black")  # Ligne de touche droite
    plt.plot([5, 5], [0, 10], color="black", linestyle="--")  # Ligne centrale

    # Cercle central
    circle = plt.Circle((5, 5), 1, color="black", fill=False)
    plt.gca().add_patch(circle)

    # Surface de réparation
    plt.plot([2, 8], [8, 8], color="black")  # Haut de la surface
    plt.plot([2, 2], [8, 10], color="black")  # Côté gauche
    plt.plot([8, 8], [8, 10], color="black")  # Côté droit

    plt.show()


# Dessiner le terrain
plt.figure(figsize=(8, 12))
draw_pitch()

# Positionner les joueurs
for player in players:
    position = formation.get(player["position"], [])
    if position:
        x, y = position.pop(0)  # Récupérer la position disponible
        plt.text(x, y, player["name"], ha="center", va="center", fontsize=8, color="blue")

# Ajuster les limites et afficher
plt.xlim(0, 10)
plt.ylim(0, 10)
plt.axis("off")
plt.title("Formation 4-4-2")
plt.show()