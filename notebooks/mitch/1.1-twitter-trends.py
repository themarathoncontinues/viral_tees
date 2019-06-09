import os
import base64
from dotenv import load_dotenv

load_dotenv('../../.env')

TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')

TWITTER_API_AUTH = '{}:{}'.format(TWITTER_API_KEY, TWITTER_API_SECRET).encode('ascii')
b64_encoded_key = base64.b64encode(TWITTER_API_AUTH)
b64_encoded_key = b64_encoded_key.decode('ascii')

import requests

base_url = 'https://api.twitter.com'
auth_url = '{}/oauth2/token'.format(base_url)

auth_headers = {
    'Authorization': 'Basic {}'.format(b64_encoded_key),
    'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
}

auth_data = {
    'grant_type': 'client_credentials'
}

auth_resp = requests.post(auth_url, headers=auth_headers, data=auth_data)

import pdb; pdb.set_trace()
