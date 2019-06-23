from __future__ import unicode_literals

import os
import argparse
import pandas as pd
import tweepy
import json

# For debugging. Remove later!
import gnureadline
from pprint import pprint

'''
Here we have defined variables holding
WOEID (http://woeid.rosselliot.co.nz/lookup/)
of 14 largest metropolitan areas in the
United States.
'''
metro = {
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

    try:
        consumer_key = os.environ['TWITTER_CONSUMER_KEY']
        consumer_secret = os.environ['TWITTER_CONSUMER_SECRET']
        access_token = os.environ['TWITTER_ACCESS_TOKEN']
        access_token_secret = os.environ['TWITTER_TOKEN_SECRET']
    except KeyError:
        from dotenv import load_dotenv

        load_dotenv('.env')

        consumer_key = os.getenv('TWITTER_API_KEY')
        consumer_secret = os.getenv('TWITTER_API_SECRET')
        access_token = os.getenv('TWITTER_API_TOKEN')
        access_token_secret = os.getenv('TWITTER_API_ACCESS')

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    return api


def get_trends(api, location):

    return api.trends_place(location)


def get_trends_df(trends_json):

    return pd.DataFrame(
        trends_json[0]['trends']).sort_values(
        by=['tweet_volume'],
        ascending=False).reset_index(
            drop=True)


def run(args_dict):

    places = args_dict['location']
    api = auth()

    dfs = {}

    if isinstance(places, list):
        for place in places:
            location = metro[place]
            trends_json = get_trends(api, location)
            trends_df = get_trends_df(trends_json)
            dfs.update({place: trends_df})
    elif isinstance(places, str):
        location = metro[places]
        trends_json = get_trends(api, location)
        trends_df = get_trends_df(trends_json)
        dfs.update({places: trends_df})
    else:
        print('Incorrect argument passed.')
        return -1

    return dfs


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Service to provide viral tweets for given region.')
    parser.add_argument(
        '-loc', '--location',
        required=False,
        nargs=1,
        help='Select region in which trends to chose from.',
        choices=[code for code in metro.keys()],
        default=[code for code in metro.keys()]
    )

    args_dict = vars(parser.parse_args())
    run(args_dict)
