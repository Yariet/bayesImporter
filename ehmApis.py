
import sys
sys.path.append('.')
import json
import requests
from accessToken import get_token, use_api_token, check_api_token

#? COSTANTS
URL = 'https://lolesports-api.bayesesports.com/emh/v1/'
GAME_ASSETS = ['GAMH_DETAILS', 'GAMH_SUMMARY', 'ROFL_REPLAY']
GAME_INFO_ASSETS = ['GAMH_DETAILS', 'GAMH_SUMMARY']
GAME_REPLAY = 'GAMH_REPLAY'
GAME_IDS_FILE = 'Bayes/Ehm/__game_ids.json'

#? 1 api call
def list_tags():
    '''
    List all available tags to use as get_games parameter.
    '''
    use_api_token()
    url = URL + 'tags'
    headers = {'Authorization': 'Bearer ' + get_token()}
    response = requests.get(url, headers=headers)
    return response.json()

#? 1 api call
def get_games(**kwargs):
    '''
    List available games. The results are paginated.

    Filtering
    - platform_id: To filter by platform id. DOESNT WORK
    - tags: To filter by tags. This filter uses "OR" logic. E.g. tags=["Lfl", "LEC"]
    - To change page size, use size query parameter. E.g. size=50
    - To choose page number, use page query parameter. E.g. page=2
    - from_/to: To filter by game start and end dates.The value of these parameters should be in ISO 8601 datetime format
        e.g.: a UTC date and time: 2021-03-20T22:00:00Z (Z means UTC), or date and time with time zone: 2021-03-20T22:00:00+02:00.

    '''
    use_api_token()
    url = URL + 'games'
    headers = {'Authorization': 'Bearer ' + get_token()}
    body = {}
    for key, value in kwargs.items():
        if key.endswith('_'):
            key = key[:-1]
        body[key] = value
    response = requests.get(url, params=body ,headers=headers)
    return response.json()

#? 1 api call
def get_game_overview(game_id):
    '''
    Get overview information about a specific game by ID.
    '''
    check_api_token()
    use_api_token()

    url = URL + 'games/' + game_id
    headers = {'Authorization': 'Bearer ' + get_token()}
    response = requests.get(url, headers=headers)
    return response.json()

#? Up to 3 api calls
def get_game_assets(game_id, types):
    '''
    Get detailed information about a specific game by ID.
    '''
    assets = {}
    check_api_token()
    game_assets = get_game_overview(game_id)['assets']
    use_api_token()
    for type in types:
        if type in game_assets:
            url = URL + 'games/' + game_id + '/download'
            headers = {'Authorization': 'Bearer ' + get_token()}
            body = {'type': type}
            check_api_token()
            response = requests.get(url, params=body, headers=headers)
            use_api_token()
            assets[type] = response.json()['url']
    return assets

def filter_by_tricode(games, tricode):
    #Check if all games have the team tricode
    for game in games[:]:
        if (tricode not in game['teamTriCodes']) and (tricode not in game['name']):
            games.remove(game)
    return games

def get_games_id(games):
    '''
    Get game ids from games list.
    '''
    gameids = []
    for game in games:
        gameids.append(game['platformGameId'])
    with open(GAME_IDS_FILE, 'w') as f:
        json.dump(gameids, f)
    return gameids

def get_game_summary(game_assets):
    '''
    Get games summary as json.
    '''
    check_api_token()
    use_api_token()

    summary_link = game_assets["GAMH_SUMMARY"]
    response = requests.get(summary_link)
    return response.json()

def get_game_details(game_assets):
    '''
    Get games timeline as json.
    '''

    check_api_token()
    use_api_token()

    details_link = game_assets["GAMH_DETAILS"]
    response = requests.get(details_link)
    return response.json()

def getLeagues():
    use_api_token()
    url = 'https://lolesports-api.bayesesports.com/historic/v1/riot-lol/leagues'
    headers = {'Authorization': 'Bearer ' + get_token()}
    response = requests.get(url, headers=headers)
    return response.json()

if __name__ == '__main__':
    # print(get_games(size=size, tags=tags)['games'])
    # print(get_game_overview('ESPORTSTMNT04_2230161'))
    print(getLeagues())
