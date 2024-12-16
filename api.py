import requests

url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"

headers = {
    "X-RapidAPI-Key": "fa20724dc98dc24393213f7f8540b91e",
    "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}
leagues = [39, 61, 135, 140, 78]  # Premier League, Ligue 1, Serie A, Liga, Bundesliga
seasons = [2021, 2022]  # Seasons 2021 and 2022 are the only ones available in the free plan.

for league in leagues:
    for season in seasons:
        url = f"https://api-football-v1.p.rapidapi.com/v3/fixtures?league={league}&season={season}"
        response = requests.get(url, headers=headers)
        print(f"Ligue {league}, Saison {season}")
        print(response.json())
    
    # Does not work since I'm not susbribed to API Football, but it should work.
