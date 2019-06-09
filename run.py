from base import Api
import os
from dotenv import load_dotenv
load_dotenv('.env')

key = os.getenv('TWITTER_API_KEY')
secret = os.getenv('TWITTER_API_SECRET')

api = Api(key, secret)

response = api.auth()

