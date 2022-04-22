import sys
sys.path.append('.')
import os
import json
import requests
from time import sleep
from typing import Optional
from getpass import getpass
from dotenv import load_dotenv
from datetime import datetime, timedelta
load_dotenv("Bayes/Token/_EsportEmpire.env")

EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')
TOKEN_FILE = 'Bayes/Token/token.json'
API_TOKENS= 50

def check_api_token():
    '''
    Check if api token is available.
    '''
    global API_TOKENS
    if API_TOKENS <= 0:
        sleep(0.5)
        API_TOKENS = 1

def use_api_token():
    '''
    Use api token.
    '''
    global API_TOKENS
    API_TOKENS -= 1


def portal_login(username: str, password: str) -> dict:
    '''
    Send API request to get an access token using supplied `username` and
    `password`. Return JSON response, received from the server.
    '''
    url = 'https://lolesports-api.bayesesports.com/auth/login'
    headers = {"Content-Type": "application/json"}
    creds = {'username': username, 'password': password}

    response = requests.post(url, json=creds, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

def store_token(response_token: dict, filename: str):
    '''
    Save access token details, received from the API to a JSON-file.
    The expiressIn field is replaced with expiresAt UNIX timestamp.
    '''

    result = dict(response_token)
    expire_date = datetime.now() + timedelta(seconds=result.pop('expiresIn'))
    result['expiresAt'] = expire_date.timestamp()
    #store a variable containing 30 days in seconds
    thirty_days = 30 * 24 * 60 * 60
    refresh_date = datetime.now() + timedelta(seconds=thirty_days)
    result['refreshAt'] = refresh_date.timestamp()
    result['refreshedAt'] = datetime.now().timestamp()
    try:
        with open(filename, 'r') as f:
            stored_token = json.load(f)
            result['refreshAt'] = stored_token['refreshAt']
    finally:
        with open(filename, 'w') as f:
            json.dump(result, f)


def refresh_token(stored_token: dict) -> str:
    '''
    Send API request to refresh the access token.
    '''

    url = 'https://lolesports-api.bayesesports.com/auth/refresh'
    headers = {"Content-Type": "application/json"}
    refreshToken = stored_token['refreshToken']
    creds = {'refreshToken': refreshToken}

    response = requests.post(url, json=creds, headers=headers)
    if response.status_code == 200:
        store_token(response.json(), TOKEN_FILE)
        return response.json()['accessToken']
    else:
        response.raise_for_status()

def is_stored_token_fresh(stored_token: dict) -> bool:
    '''Check if the access token that is stored in filename is still valid.'''
    expire_date = datetime.fromtimestamp(stored_token['expiresAt'])
    return datetime.now() < expire_date

def is_stored_token_refreshable(stored_token: dict) -> bool:
    '''Check if the access token that is stored in filename is still refreshable.'''
    refresh_date = datetime.fromtimestamp(stored_token['refreshAt'])
    refreshed_date = datetime.fromtimestamp(stored_token['refreshedAt'])

    return datetime.now() < refresh_date and refreshed_date + timedelta(seconds=15*24*60*60) > datetime.now()

def get_token_from_file(filename) -> Optional[str]:
    '''
    Load access token info from JSON `filename` and return the access token
    if it is still fresh. If it's not, or if the file is missing, return None.
    '''

    if not os.path.exists(filename):
        return None
    with open(filename) as f:
        stored_token = json.load(f)
    if is_stored_token_fresh(stored_token):
        return stored_token['accessToken']
    elif is_stored_token_refreshable(stored_token):
        return refresh_token(stored_token)
    else:
        return None

def get_token() -> str:
    '''
    Get an auth token from the local file or send an API request to login if
    stored token is too old.
    '''

    token = get_token_from_file(TOKEN_FILE)
    if token is None:
        username = \
            EMAIL or \
            input(f'Portal login: ')
        password = \
            PASSWORD or \
            getpass(f'Password for {username}: ')
        response_token = portal_login(username, password)
        store_token(response_token, TOKEN_FILE)
        token = response_token['accessToken']
    return token

if __name__ == '__main__':
    # print(get_token())
    refresh_token(json.load(open(TOKEN_FILE)))