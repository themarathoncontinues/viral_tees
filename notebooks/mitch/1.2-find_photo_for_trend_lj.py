import os
import argparse
import pandas as pd
import tweepy
import json
import requests


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

def find_photo_for_trend(trend_df):

    vol_sort = trend_df.sort_values(by=['tweet_volume'], ascending=False
                                    ).reset_index()

    print(vol_sort['name'].head(5))

    trending_list = vol_sort['name'].tolist()

    cached_tweets = []

    for trend in trending_list:
        results = tweepy.Cursor(api.search, q=trend).items(10)
        for result in results:
            # cached_tweets.append(result)
            # cached_tweets_df = pd.DataFrame(cached_tweets)
            import pdb; pdb.set_trace()
            print(result.text.encode('utf-8'))
            # cached_tweets_df.to_csv('cached_tweets.csv', index=0)
            break


def get_trends(input):

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
            'united-states'])

    args_dict = vars(parser.parse_args())
    run(args_dict)
