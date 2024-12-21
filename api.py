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
    return players_df


'''Define a function to plot a football team on the pitch'''

def draw_team(team_id):
    
    players_df = get_players(team_id)
    
    role_positions = {
        "Goalkeeper" : [(50,98-i*2) for i in range(10)],
        "Right-Back" : [(15,70-i*2) for i in range(10)],
        "Centre-Back" :[(35 + (30 if i > 2 else 0), 80-(i*2 if i<2 else (i%3)*2)) for i in range(10)],
        "Left-Back" : [(85,70-i*2) for i in range(10)],
        "Central Midfield" :[(30,45-i*2) for i in range(10)],
        "Defensive Midfield" : [(50,60-i*2) for i in range(10)],
        "Attacking Midfield" : [(70,45-i*2) for i in range(10)],
        "Right Winger" : [(20,25-i*2) for i in range(10)],
        "Centre-Forward" : [(50,20-i*2) for i in range(10)],
        "Left Winger" : [(80,25-i*2) for i in range(10)], }
    
    
    positions = []
    position_counters = {role: 0 for role in role_positions}
    
    for _, player in players_df.iterrows():
        role = player["Position"]
        if role in role_positions:
            counter = position_counters[role]
            if counter < len(role_positions[role]):  # Vérifie si une position est disponible
                pos = role_positions[role][counter]
                position_counters[role] += 1
                positions.append({"name": player["Player Name"], "x": pos[0], "y": pos[1]})
    
    position_df = pd.DataFrame(positions)
    
    plt.figure(figsize=(8, 12)).patch.set_facecolor("green")  # Dimensions of the pitch
    plt.plot([0, 100], [0, 0], color="white") # All the lines of the pitch 
    plt.plot([0, 0], [0, 100], color="white")  
    plt.plot([100, 100], [0, 100], color="white")  
    plt.plot([0, 100], [100, 100], color="white")  
    plt.plot([30, 70], [90, 90], color="white")
    plt.plot([30, 70], [10, 10], color="white")
    plt.plot([30, 30], [90, 100], color="white")
    plt.plot([70, 70], [90, 100], color="white")
    plt.plot([30, 30], [0, 10], color="white")
    plt.plot([70, 70], [0, 10], color="white")
    plt.plot([0, 100], [50, 50], color="white")
    circle = plt.Circle((50, 50), 10, color="white", fill=False)
    plt.gca().add_patch(circle)
    plt.xlim(0, 100)
    plt.ylim(0, 100)
    plt.axis("off")  # hide axes

   
    for _, row in position_df.iterrows():
        plt.text(row["x"], row["y"], row["name"], color="black", fontsize=8,
                 ha="center", va="center")

    
    plt.show()

draw_team(521)
