import requests
import pandas as pd

#Details for the utilization of API
API_KEY = "7fee06d41d0344a7b06b6907341c8a2b"
BASE_URL = "https://api.football-data.org/v4"

#Definition of a function which creates a dataframe with information on all the teams of the chosen league.


def get_teams(competition_id):
    url = f"{BASE_URL}/competitions/{competition_id}/teams"
    headers = {"X-Auth-Token": API_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        teams = response.json()["teams"]
    else:
        print(f"Error fetching teams: {response.status_code} - {response.text}")
        return []
    teams_list = []
    for team in teams:
        teams_list.append({
            "Team ID": team["id"],
            "Team Name": team["name"],
            "Short Name": team["shortName"],
            "Area": team["area"]["name"],
            "Founded": team.get("founded", "N/A"),
            "Stadium": team.get("venue", "N/A")
        })
    teams_df = pd.DataFrame(teams_list)
    print(teams_df)

#Definition of a function which creates a dataframe with information on all the players of the chosen team.
def get_players(team_id):
    url = f"{BASE_URL}/teams/{team_id}"
    headers = {"X-Auth-Token": API_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        squad = response.json()["squad"]
        team_data = response.json()
        team = team_data.get("name", "Unknown Team")
    else:
        print(f"Error fetching teams: {response.status_code} - {response.text}")
        return []
    players_list = []
    for player in squad:
        players_list.append({
            "Player Name": player["name"],
            "Position": player["position"],
            "Date of Birth": player.get("dateOfBirth", "N/A"),
            "Nationality": player.get("nationality", "N/A"),
            "Team Name": team
        })
    players_df = pd.DataFrame(players_list)
    print(players_df)


get_teams(2015)
get_players(521)
