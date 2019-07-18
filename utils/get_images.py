import json
import logging
import os
import pandas as pd
import tweepy

from dotenv import load_dotenv
from itertools import groupby
from pathlib import Path
from utils.constants import ENV_PATH


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

load_dotenv(dotenv_path=ENV_PATH)

TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
TWITTER_API_TOKEN = os.getenv('TWITTER_API_TOKEN')
TWITTER_API_ACCESS = os.getenv('TWITTER_API_ACCESS')

auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
auth.set_access_token(TWITTER_API_TOKEN, TWITTER_API_ACCESS)

api = tweepy.API(auth)


def image_parser(trends):
    """
    Query Twitter to get MAX_TWEETS per trend in given metro region
    :param trends:
    :return list of tweets with images:
    """

    MAX_TWEETS = 30

    logger.info(f'Trends being queried: {trends}')

    metadata_store = []
    tweets_with_images = []
    for trend in trends:
        tweet_cursor = tweepy.Cursor(api.search, q=trend, include_entities=True).items(MAX_TWEETS)

        data = api.rate_limit_status()
        print(data['resources']['search']['/search/tweets'])

        for tweet in tweet_cursor:
            json_str = json.dumps(tweet._json)
            model = json.loads(json_str)

            user = model['user']['screen_name']
            tweet_id = model['id_str']
            tweet_content = model['text']
            follower_count = model['user']['followers_count']
            retweet_count = model['retweet_count']
            favorte_count = model['favorite_count']

            tweet_metadata = {
                'user': user,
                'tweet_content': tweet_content,
                'tweet_id': tweet_id,
                'trend': trend,
                'follower_count': follower_count,
                'retweet_count': retweet_count,
                'favorite_count': favorte_count,
                'media_url': 'n/a'
            }

            if 'media' not in tweet.entities:
                metadata_store.append(tweet_metadata)
            else:
                media_url = model['entities']['media'][0]['media_url']
                media = {'media_url': media_url}
                tweet_metadata.update(media)

                metadata_store.append(tweet_metadata)
                tweets_with_images.append(tweet_metadata)

    amount_of_tweets_obtained = len(tweets_with_images)
    logger.info(f'Using {amount_of_tweets_obtained} tweets to select images')

    return tweets_with_images


def sort_tweets_with_images(tweets_with_images):
    sorted_tweets = sorted(tweets_with_images, key=lambda x: (x['retweet_count'], x['favorite_count']), reverse=True)
    unique_tweets = list({v['media_url']: v for v in sorted_tweets}.values())

    return unique_tweets


def run(args_dict):
    tweet_list = image_parser(args_dict['input'])
    image_dicts = sort_tweets_with_images(tweet_list)

    return image_dicts


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Retrieve images from trimmed trends CSV.')
    parser.add_argument('-i', '--input', required=True,
        help='Input path to CSV')
    parser.add_argument('-o', '--output', required=True,
        help='Path to image output.')

    args_dict = vars(parser.parse_args())

    run(args_dict)
