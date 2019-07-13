import json
import logging
import os
import pandas as pd
import requests
import tweepy

from dotenv import load_dotenv
from math import floor
from pathlib import Path
from utils.constants import ENV_PATH


logging.getLogger(__name__)

load_dotenv(dotenv_path=ENV_PATH)

TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
TWITTER_API_TOKEN = os.getenv('TWITTER_API_TOKEN')
TWITTER_API_ACCESS = os.getenv('TWITTER_API_ACCESS')

auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
auth.set_access_token(TWITTER_API_TOKEN, TWITTER_API_ACCESS)

api = tweepy.API(auth)

# lat, lon
location_config = {
	'usa-nyc': (40.7128, -74.0060),
	'usa-lax': (34.0522, -118.2437),
	'usa-chi': (41.8781, -87.6298),
	'usa-dal': (32.7767, -96.7970),
	'usa-hou': (29.7604, -95.3698),
	'usa-wdc': (38.9072, -77.0369),
	'usa-mia': (25.7617, -80.1918),
	'usa-phi': (39.9526, -75.1652),
	'usa-atl': (33.7490, -84.3880),
	'usa-bos': (42.3601, -71.0589),
	'usa-phx': (33.4484, -112.0740),
	'usa-sfo': (37.7749, -122.4194),
	'usa-det': (42.3314, -83.0458),
	'usa-sea': (47.6062, -122.3321),
}

MAX_TWEETS = floor(3000/len(location_config))
# MAX_TWEETS = 500


def query(loc, trend):
	tweets = [
		x for x in tweepy.Cursor(
			api.search,
			q=trend,
			geocode='{},{},15mi'.format(
				location_config[loc][0],
				location_config[loc][1]
			),
		).items(MAX_TWEETS)
	]

	return tweets


def parse(tweets):

	data = [t._json for t in tweets]

	return data



