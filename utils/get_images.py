import json
import logging
import os
import pandas as pd
import requests
import tweepy

from dotenv import load_dotenv
from pathlib import Path

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

    return trend_one, tweets_with_images


def find_target_tweets(trend_one, tweets_with_images):

    url = {}
    tweet = tweets_with_images[0]
    id_num = tweet['id']
    image_url = tweet['entities']['media'][0]['media_url']

    logging.info('Images returned to Luigi')

    return trend_one[0], str(id_num), image_url

        # with open('data/images/{}_{}.jpg'.format(trend_one, id_num), 'wb') as handle:
        #     response = requests.get(image_url).content
        #     handle.write(response)

def run(args_dict):

    top_trend, img_lst = tweepy_parser(args_dict['input'])
    urls = find_target_tweets(top_trend, img_lst)

    return urls


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Retrieve images from trimmed trends CSV.')
    parser.add_argument('-i', '--input', required=True,
        help='Input path to CSV')
    parser.add_argument('-o', '--output', required=True,
        help='Path to image output.')

    args_dict = vars(parser.parse_args())

    run(args_dict)
