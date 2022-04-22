import sys
sys.path.append('.')
import requests
from accessToken import get_token, use_api_token, check_api_token

URL = 'https://lolesports-api.bayesesports.com/historic/v1/riot-lol/'

#? Teams
def getTeams():
    '''
    List all the teams avaiable
    '''

    check_api_token()
    use_api_token()
    url = URL + 'teams'
    headers = {'Authorization': 'Bearer ' + get_token()}
    response = requests.get(url, headers=headers)
    return response.json()

#? Leagues
def getLeagues():
    '''
    List all the leagues avaiable
    '''

    check_api_token()
    use_api_token()
    url = URL + 'leagues'
    headers = {'Authorization': 'Bearer ' + get_token()}
    response = requests.get(url, headers=headers)
    return response.json()

def getLeague(leagueId):
    '''
    Get the league of the given id
    '''

    check_api_token()
    use_api_token()
    url = URL + 'leagues/' + id
    headers = {'Authorization': 'Bearer ' + get_token()}
    response = requests.get(url, headers=headers)
    return response.json()

def getLeagueByName(leagueName):
    '''
    Get a league by name
    '''

    leagues = getLeagues()
    for league in leagues:
        if league["name"] == leagueName:
            return league

def getLeagueLogoByName(leagueName):

    league = getLeagueByName(leagueName)
    logo = league["logoUrl"]
    return f"=Image(\"{logo}\",1)"

def getLeagueTournaments(leagueId):
    '''
    Get the tournaments of a league
    '''

    check_api_token()
    use_api_token()
    url = URL + 'leagues/' + leagueId + '/tournaments'
    headers = {'Authorization': 'Bearer ' + get_token()}
    response = requests.get(url, headers=headers)
    return response.json()

#? Tournaments
def getTournaments():
    '''
    List all the tournaments avaiable
    '''

    check_api_token()
    use_api_token()
    url = URL + 'tournaments'
    headers = {'Authorization': 'Bearer ' + get_token()}
    response = requests.get(url, headers=headers)
    return response.json()

def getTournamentByName(tournamentName):
    tournaments = getTournaments()
    for tournament in tournaments:
        if checkTournamentSplitName(tournament["name"], tournamentName):
            return tournament

def getTournamentId(tag):
    '''
    Get the id of a tournament by name
    '''

    tournaments = getTournaments()
    for tournament in tournaments:
        if tournament["name"] == tag:
            return tournament["id"]

def getTournament(id):
    '''
    Get a tournament by id
    '''

    check_api_token()
    use_api_token()
    url = URL + 'tournaments/' + id
    headers = {'Authorization': 'Bearer ' + get_token()}
    response = requests.get(url, headers=headers)
    return response.json()

def getTournamentMatches(id):
    '''
    Get a tournament matches by id
    '''

    if id == None:
        return None

    check_api_token()
    use_api_token()
    url = URL + 'tournaments/' + id + '/matches'
    headers = {'Authorization': 'Bearer ' + get_token()}
    response = requests.get(url, headers=headers)
    return response.json()

def getTournamentMatchesLen(tag):
    '''
    Get the sum of played games in the tournament passed as argument
    '''

    matches = getTournamentMatches(getTournamentId(tag))
    return len(matches) if matches != None else 0

def getTournamentsMatchesLen(tags):
    '''
    Get the sum of played games in the tournament passed as argument
    '''

    sum = 0
    for tag in tags:
        sum += getTournamentMatchesLen(tag)
    return sum

def checkTournamentSplitName(tournamentName, splitNames):

    '''
    Check if all the parts of the split name are in the actual Bayes tournament name
    '''

    # Loop through all the split names and check if all the parts of the split name are in the actual Bayes tournament name
    for splitName in splitNames:
        result = True
        for part in splitName.split(" "):
            if part not in tournamentName:
                result = False
                break
        if result:
            return True

    return False

def getTournamentsDates(tags):

    start_date = None
    end_date = None

    tournaments = getTournaments()
    for tournament in tournaments:
        if tournament["name"] != None and checkTournamentSplitName(tournament["name"], tags):
            tstart_date = tournament["startDate"]
            tend_date = tournament["endDate"]
            if start_date == None or tstart_date < start_date:
                start_date = tstart_date
            if end_date == None or tend_date > end_date:
                end_date = tend_date
    return start_date, end_date

#? Matches
def getMatches(matchOrGameId=None, teamIds=None, leagueIds=None, start_date=None, end_date=None, size=None, page_number=1):
    '''
    Get avaible games from the API matching filters
    '''

    check_api_token()
    use_api_token()
    url = URL + 'matches'
    headers = {'Authorization': 'Bearer ' + get_token()}
    params = {}
    if matchOrGameId != None:
        params["matchOrGameId"] = matchOrGameId
    if teamIds != None:
        params["teamIds"] = teamIds
    if leagueIds != None:
        params["leagueIds"] = leagueIds
    if start_date != None:
        params["startDate"] = start_date
    if end_date != None:
        params["endDate"] = end_date
    if size != None:
        params["size"] = size
    params["pageNumber"] = page_number

    response = requests.get(url, headers=headers, params=params)
    return response.json()

def getMatch(matchId):
    '''
    Get a match by id
    '''

    check_api_token()
    use_api_token()
    url = URL + 'matches/' + matchId
    headers = {'Authorization': 'Bearer ' + get_token()}
    response = requests.get(url, headers=headers)
    return response.json()

#? Games
def getCompactGameJsonLink(gameId):
    '''
    Get a game by id
    '''

    check_api_token()
    use_api_token()
    url = URL + f'games/{gameId}/downloadDump'
    headers = {'Authorization': 'Bearer ' + get_token()}
    response = requests.get(url, headers=headers)
    return response.json()["url"]

if __name__ == '__main__':
    # leagues = getLeagues()
    # for league in leagues:
    #     print(league["name"])
    print(getLeagueByName("PG Nationals"))




