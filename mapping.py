import requests
import bs4
import pandas as pd
import geopandas as gpd
import folium
import webbrowser

def retrieve_page(url: str) -> bs4.BeautifulSoup:
    """
    Retrieves and parses a webpage using BeautifulSoup.

    Args:
        url (str): The URL of the webpage to retrieve.

    Returns:
        bs4.BeautifulSoup: The parsed HTML content of the page.
    """
    r = requests.get(url)
    page = bs4.BeautifulSoup(r.content, "html.parser")
    return page


def extract_team_name_url(team: bs4.element.Tag) -> dict:
    """
    Extracts the team name and its corresponding Wikipedia URL.

    Args:
        team (bs4.element.Tag): The BeautifulSoup tag containing the team information.

    Returns:
        dict: A dictionary with the team name as the key and the Wikipedia URL as the value, or None if not found.
    """
    try:
        team_url = team.find("a").get("href")
        equipe = team.find("a").get("title")
        url_get_info = f"http://fr.wikipedia.org{team_url}"
        print(f"Retrieving information for {equipe}")
        return {equipe: url_get_info}
    except AttributeError:
        print(f'No <a> tag for "{team}"')
        return None


def explore_team_page(wikipedia_team_url: str) -> bs4.BeautifulSoup:
    """
    Retrieves and parses a team's Wikipedia page.

    Args:
        wikipedia_team_url (str): The URL of the team's Wikipedia page.

    Returns:
        bs4.BeautifulSoup: The parsed HTML content of the team's Wikipedia page.
    """
    r = requests.get(wikipedia_team_url)
    page = bs4.BeautifulSoup(r.content, "html.parser")
    return page


def extract_stadium_info(search_team: bs4.BeautifulSoup) -> tuple:
    """
    Extracts stadium information from a team's Wikipedia page.

    Args:
        search_team (bs4.BeautifulSoup): The parsed HTML content of the team's Wikipedia page.

    Returns:
        tuple: A tuple containing the stadium name, latitude, and longitude, or (None, None, None) if not found.
    """
    for stadium in search_team.findAll("tr"):
        try:
            header = stadium.find("th", {"scope": "row"})
            if header and header.contents[0].string == "Stade":
                name_stadium, url_get_stade = extract_stadium_name_url(stadium)
                if name_stadium and url_get_stade:
                    latitude, longitude = extract_stadium_coordinates(url_get_stade)
                    return name_stadium, latitude, longitude
        except (AttributeError, IndexError) as e:
            print(f"Error processing stadium information: {e}")
    return None, None, None


def extract_stadium_name_url(stadium: bs4.element.Tag) -> tuple:
    """
    Extracts the stadium name and URL from a stadium element.

    Args:
        stadium (bs4.element.Tag): The BeautifulSoup tag containing the stadium information.

    Returns:
        tuple: A tuple containing the stadium name and its Wikipedia URL, or (None, None) if not found.
    """
    try:
        url_stade = stadium.findAll("a")[1].get("href")
        name_stadium = stadium.findAll("a")[1].get("title")
        url_get_stade = f"http://fr.wikipedia.org{url_stade}"
        return name_stadium, url_get_stade
    except (AttributeError, IndexError) as e:
        print(f"Error extracting stadium name and URL: {e}")
        return None, None


def extract_stadium_coordinates(url_get_stade: str) -> tuple:
    """
    Extracts the coordinates of a stadium from its Wikipedia page.

    Args:
        url_get_stade (str): The URL of the stadium's Wikipedia page.

    Returns:
        tuple: A tuple containing the latitude and longitude of the stadium, or (None, None) if not found.
    """
    try:
        soup_stade = retrieve_page(url_get_stade)
        kartographer = soup_stade.find("a", {"class": "mw-kartographer-maplink"})
        if kartographer:
            coordinates = (
                kartographer.get("data-lat") + "," + kartographer.get("data-lon")
            )
            latitude, longitude = coordinates.split(",")
            return latitude.strip(), longitude.strip()
        else:
            return None, None
    except Exception as e:
        print(f"Error extracting stadium coordinates: {e}")
        return None, None


def extract_team_info(url_team_tag: bs4.element.Tag, division: str) -> dict:
    """
    Extracts information about a team, including its stadium and coordinates.

    Args:
        url_team_tag (bs4.element.Tag): The BeautifulSoup tag containing the team information.
        division (str): Team league

    Returns:
        dict: A dictionary with details about the team, including its division, name, stadium, latitude, and longitude.
    """

    team_info = extract_team_name_url(url_team_tag)
    url_team_wikipedia = next(iter(team_info.values()))
    name_team = next(iter(team_info.keys()))
    search_team = explore_team_page(url_team_wikipedia)
    name_stadium, latitude, longitude = extract_stadium_info(search_team)
    dict_stadium_team = {
        "division": division,
        "equipe": name_team,
        "stade": name_stadium,
        "latitude": latitude,
        "longitude": longitude,
    }
    return dict_stadium_team


def retrieve_all_stadium_from_league(
    url_list: dict, division: str = "L1"
) -> pd.DataFrame:
    """
    Retrieves information about all stadiums in a league.

    Args:
        url_list (dict): A dictionary mapping divisions to their Wikipedia URLs.
        division (str): The division for which to retrieve stadium information.

    Returns:
        pd.DataFrame: A DataFrame containing information about the stadiums in the specified division.
    """
    page = retrieve_page(url_list[division])
    teams = page.findAll("span", {"class": "toponyme"})
    all_info = []

    for team in teams:
        all_info.append(extract_team_info(team, division))

    stadium_df = pd.DataFrame(all_info)
    return stadium_df
