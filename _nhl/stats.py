import requests
from nhl_settings import player_url, match_url


def get_data(url):
    match_request = requests.request('GET', url)
    match_request = match_request.json()

    rows = []
    for weeks in match_request['data']:
        rows.append(
            weeks
        )

    print(rows)

    return rows


match_data = get_data(match_url)
player_data = get_data(player_url)
