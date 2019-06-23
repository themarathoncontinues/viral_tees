import pandas as pd
from dotenv import load_dotenv
from pathlib import Path
import requests
import os
import tweepy
import json

import logging

logging.getLogger(__name__)

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)


TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
TWITTER_API_TOKEN = os.getenv('TWITTER_API_TOKEN')
TWITTER_API_ACCESS = os.getenv('TWITTER_API_ACCESS')

auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
auth.set_access_token(TWITTER_API_TOKEN, TWITTER_API_ACCESS)

api = tweepy.API(auth)


def tweepy_parser(filepath):
    nyc_trends = pd.read_csv(filepath)
    trends = nyc_trends['name'].tolist()
    trend_one = trends[:1]

    MAX_TWEETS = 100

    tweets_with_images = []
    for tweet in tweepy.Cursor(api.search, q=trend_one, include_entities=True).items(MAX_TWEETS):
        if 'media' in tweet.entities:
            json_str = json.dumps(tweet._json)
            parsable_obj = json.loads(json_str)
            tweets_with_images.append(parsable_obj)
        else:
            pass

    amount_of_tweets_obtained = len(tweets_with_images)
    logging.info('Using {} tweets to select images'.format(amount_of_tweets_obtained))

    find_target_tweets(trend_one, tweets_with_images)


def find_target_tweets(trend_one, tweets_with_images):
    for tweet in tweets_with_images:
        id_num = tweet['id']
        image_url = tweet['entities']['media'][0]['media_url']
        with open('data/images/{}_{}.jpg'.format(trend_one, id_num), 'wb') as handle:
            response = requests.get(image_url).content
            handle.write(response)

    logging.info('Images saved to data/images directory')


if __name__ == "__main__":
    filepath = 'data/trends/trends_0622_2019_1717_usa-nyc.csv'
    tweepy_parser(filepath)
