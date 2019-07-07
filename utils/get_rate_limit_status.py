import logging
import os
import tweepy

from dotenv import load_dotenv
from utils.constants import ENV_PATH

load_dotenv(dotenv_path=ENV_PATH)

TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
TWITTER_API_TOKEN = os.getenv('TWITTER_API_TOKEN')
TWITTER_API_ACCESS = os.getenv('TWITTER_API_ACCESS')

auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
auth.set_access_token(TWITTER_API_TOKEN, TWITTER_API_ACCESS)

api = tweepy.API(auth)

print(api.rate_limit_status()['resources']['search']['/search/tweets'])
print(api.rate_limit_status()['resources']['trends']['/trends/place'])
