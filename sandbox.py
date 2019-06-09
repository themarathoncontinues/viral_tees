from __future__ import unicode_literals

import os
import argparse
import pandas as pd
import tweepy
import json


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
import pdb; pdb.set_trace()
api = tweepy.API(auth)

CONST = {
    'united-states': 23424977,
    'global': 1
}

def find_photo_for_trend(trend_df):

    vol_sort = trend_df.sort_values(by=['tweet_volume'], ascending=False
                                    ).reset_index()

    trending_list = vol_sort['name'].tolist()

    for trend in trending_list:
        results = api.search(q=trend)
        for result in results:
            print(result.text.encode('utf-8'))
            import pdb; pdb.set_trace()
            break


def get_trends(input):

    import pdb; pdb.set_trace()
    us_trends = api.trends_place(input)
    json_str = json.dumps(us_trends[0]['trends'])
    trend_df = pd.read_json(json_str, orient='list')

    find_photo_for_trend(trend_df)


def run(args_dict):

    try:
        place = args_dict['country'][0]
    except IndexError:
        place = args_dict['country']

    input = CONST.get(place)
    get_trends(input)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Service to provide viral tweets for given region.')
    parser.add_argument(
        '-c', '--country',
        required=False,
        nargs=1,
        help='Select region in which trends to chose from.',
        default='',
        choices=[
            'united-states',
            'global',
        ])

    args_dict = vars(parser.parse_args())
    run(args_dict)
