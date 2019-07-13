import os

from dotenv import load_dotenv
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.business import Business
from facebook_business.adobjects.productcatalog import ProductCatalog
from facebook_business.api import FacebookAdsApi

from utils.constants import ENV_PATH, SRC_DIR


load_dotenv(dotenv_path=ENV_PATH)

FACEBOOK_TOKEN = os.environ['FACEBOOK_TOKEN']
FACEBOOK_APP_ID = os.environ['FACEBOOK_APP_ID']
FACEBOOK_APP_SECRET = os.environ['FACEBOOK_APP_SECRET']
FACEBOOK_AD_ACCT_ID = os.environ['FACEBOOK_AD_ACCT_ID']
FACEBOOK_BUSINESS_ID = os.environ['FACEBOOK_BUSINESS_ID']

FacebookAdsApi.init(FACEBOOK_APP_ID, FACEBOOK_APP_SECRET, FACEBOOK_TOKEN)

my_account = AdAccount(FACEBOOK_AD_ACCT_ID)

fields = []
params = {
    'name': 'Test Catalog',
}


product_catalog = Business(FACEBOOK_BUSINESS_ID).create_owned_product_catalog(fields=fields, params=params)
print('product_catalog', product_catalog)


fields = ['link']
params = {
	'currency': 'USD',
	'description': 'first test post',
	'name': 'test name 1',
	'price': 20,
	'image_url': 'https://memeshappen.com/media/created/2018/11/SCOTT-S-OUR-MAN.jpg',
	'retailer_id': 'test',
	'category': 't-shirt',
	'link': 'https://viral-tees-gubr.myshopify.com/products/betawards-8'
}

product_catalog.create_product(fields=fields, params=params)

import ipdb; ipdb.set_trace()