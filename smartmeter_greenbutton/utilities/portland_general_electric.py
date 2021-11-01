"""Fetch greenbutton data from Portland General Electric"""
# This module uses OAuth2 for access
# You must provide 2 arguments:
# 1) A refresh token
# 2) A client ID
# To generate these:
#   From a chrome browser, open up portlandgeneral.com
#   right click and open up 'inspect'
#   select the 'Network' tab
#   enter your username/password and wait for login to complete
#   in the network tab, filter for 'signIn' and locate the 'POST' request
#   This should looks somehing like:
#       https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=xxxxxxxxxxxxxxx
#   Select the 'Response' tab, and copy the 'refreshToken' string (1)
#   in the network tab filter for 'refresh' and locate the 'POST' request
#   This should look like:
#       https://api.portlandgeneral.com/pg-token-implicit/refresh?client_id=xxxxxxxxxxxxxx&response_type=token&redirect_uri=
#   Select the 'Response' tab, and copy the 'client_id' string (2)
#   Copy config.yaml.template to config.yaml
#   Edit the config.yaml file, and update the 'refresh_token' value with (1) and the 'client_id' valie with (2)

"https://pgn.opower.com/ei/edge/apis/multi-account-v1/cws/pgn/customers/current"
import datetime
import logging
import requests
from requests.exceptions import RequestException

URL = "https://cs.portlandgeneral.com"
REFRESH_URL = "https://api.portlandgeneral.com/pg-token-implicit/refresh?client_id={client_id}&response_type=token&redirect_uri="
ACCOUNT_URL = "https://pgn.opower.com/ei/edge/apis/multi-account-v1/cws/pgn/customers/current"
DATERANGE_URL = "https://pgn.opower.com/ei/edge/apis/DataBrowser-v1/cws/utilities/pgn/customers/{uuid}/usage_export"
#GREENBUTTON_URL = "https://pgn.opower.com/ei/edge/apis/DataBrowser-v1/cws/utilities/pgn/customers/{uuid}/usage_export/download?format=xml&startDate={start_date}&endDate={end_date}"
GREENBUTTON_URL = "https://pgn.opower.com/ei/edge/apis/DataBrowser-v1/cws/utilities/pgn/customers/{uuid}/usage_export/download?format=xml"

def fetch_data(conf, start_date):
    bearer_token = _get_bearer_token(conf)
    uuid = _get_account_uuid(bearer_token)
    _start_date, end_date = _get_date_range(bearer_token, uuid)
    start_date = max(_start_date, start_date or datetime.datetime.min)
    data = _get_greenbutton_data(start_date, end_date, bearer_token, uuid)
    return data

def _get_bearer_token(conf):
    """Get updated bearer token via OAuth2"""
    url = REFRESH_URL.format(client_id=conf['client_id'])
    headers = {
        'Content-Length': '0',
        'idp_refresh_token': conf['refresh_token'],
    }
    try:
        resp = requests.post(url, headers=headers)
        data = resp.json()
        access_token = data['access_token']
        return access_token
    except RequestException as _e:
        logging.error("Failed to get access_token: Error: %s", _e)
        raise

def _get_account_uuid(access_token):
    url = ACCOUNT_URL
    headers = { 'Authorization': f'Bearer {access_token}' }
    try:
        resp = requests.get(url, headers=headers)
        data = resp.json()
        uuid = data['uuid']
        return uuid
    except RequestException as _e:
        logging.error("Failed to get UUID: Error: %s", _e)
        raise

def _get_date_range(access_token, uuid):
    url = DATERANGE_URL.format(uuid=uuid)
    headers = { 'Authorization': f'Bearer {access_token}' }
    start_time = datetime.datetime.now()
    end_time = datetime.datetime.min
    try:
        resp = requests.get(url, headers=headers)
        data = resp.json()
        for obj in data['bills']:
            _start = datetime.datetime.fromisoformat(obj['startDate'][:-1])
            _end = datetime.datetime.fromisoformat(obj['endDate'][:-1])
            start_time = min(start_time, _start)
            end_time = max(end_time, _end)
        return start_time, end_time
    except RequestException as _e:
        logging.error("Failed to determine allowed date ranges: Error: %s", _e)
        raise

def _get_greenbutton_data(start_date, end_date, access_token, uuid):
    url = GREENBUTTON_URL.format(
        uuid=uuid,
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'))
    headers = { 'Authorization': f'Bearer {access_token}' }
    try:
        resp = requests.get(url, headers=headers)
        data = resp.content
        return data
    except RequestException as _e:
        logging.error("Failed to download greenbutton data: Error: %s", _e)
        raise
