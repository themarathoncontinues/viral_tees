from __future__ import unicode_literals

import os
import argparse
import pandas as pd
import tweepy
import json

from dotenv import load_dotenv
from utils.constants import ENV_PATH, SRC_DIR


load_dotenv(dotenv_path=ENV_PATH)

TWITTER_CONSUMER_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_CONSUMER_SECRET = os.getenv('TWITTER_API_SECRET')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_API_TOKEN')
TWITTER_TOKEN_SECRET = os.getenv('TWITTER_API_ACCESS')

'''
Here we have defined variables holding
WOEID (http://woeid.rosselliot.co.nz/lookup/)
of 14 largest metropolitan areas in the
United States.
'''
metro_cfg = {
    'global': 1,
    'usa': 23424977,
    'usa-nyc': 2459115,
    'usa-lax': 2442047,
    'usa-chi': 2379574,
    'usa-dal': 2388929,
    'usa-hou': 2424766,
    'usa-wdc': 2514815,
    'usa-mia': 2450022,
    'usa-phi': 2471217,
    'usa-atl': 2357024,
    'usa-bos': 2367105,
    'usa-phx': 2471390,
    'usa-sfo': 2487956,
    'usa-det': 2391585,
    'usa-sea': 2490383
}


def auth():

    auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
    auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_TOKEN_SECRET)
    api = tweepy.API(auth)

    return api


def get_trends(api, location):

    assert isinstance(location, (str, int)), 'Passed wrong location type!'

    if isinstance(location, str):
        location = metro_cfg[location]
    
    data = api.trends_place(location)[0]

    return data


def get_trends_df(trends_json):

    df = pd.DataFrame(trends_json[0]['trends'])
    df = df.sort_values(
        by=['tweet_volume'],
        ascending=False
    ).reset_index(
        drop=True
    )

    return df


def run(args_dict):

    loc = args_dict['location']
    api = auth()

    dfs = {}
    woeid = metro_cfg[loc]

    trends_json = get_trends(api, woeid)
    trends_df = get_trends_df(trends_json)
    dfs.update({places: trends_df})

    return dfs


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Service to provide viral tweets for given region.')
    parser.add_argument(
        '-loc', '--location',
        required=True,
        nargs=1,
        help='Select region in which trends to chose from.',
        choices=[code for code in metro_cfg.keys()]
    )

    args_dict = vars(parser.parse_args())
    run(args_dict)
