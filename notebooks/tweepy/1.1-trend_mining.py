import os
import argparse
import pandas as pd
import tweepy
import json


consumer_key = os.environ['TWITTER_CONSUMER_KEY']
consumer_secret = os.environ['TWITTER_CONSUMER_SECRET']
access_token = os.environ['TWITTER_ACCESS_TOKEN']
access_token_secret = os.environ['TWITTER_TOKEN_SECRET']


auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

CONST = {
    'united-states': 23424977
}


def get_trends(input):

    us_trends = api.trends_place(input)
    # search_hashtag = tweepy.Cursor(api.search, q='hashtag').items(5000)
    # for tweet in search_hashtag:
    #     print(json.dumps(tweet))
    # print(json.dumps(us_trends, indent=1))


    json_str = json.dumps(us_trends[0]['trends'])
    trend_df = pd.read_json(json_str, orient='list')

    print(trend_df)

    return trend_df


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
            'united-states'])

    args_dict = vars(parser.parse_args())
    run(args_dict)