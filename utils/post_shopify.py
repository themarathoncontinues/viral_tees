import os
import requests

from dotenv import load_dotenv

load_dotenv('.env')

SHOPIFY_ENDPOINT = os.environ['SHOPIFY_API']

def create_product(input_dict):

	payload = {'product': input_dict}

	headers = {
		"Accept": "application/json",
		"Content-Type": "application/json"
	}

	response = requests.post(
		"{}/products.json".format(SHOPIFY_ENDPOINT),
		json=payload,
		headers=headers
	)

	return response

