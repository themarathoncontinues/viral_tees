import base64
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

def post_image(image_dict, response):

	product_id = response.json()['product']['id']

	headers = {
		"Accept": "application/json",
		"Content-Type": "application/json"
	}

	with open(image_dict['img'], "rb") as f:
		b64_fp = base64.encodestring(f.read()).decode('ascii')

	payload = {
		"image": {
			"position": 1,
			"attachment": b64_fp,
			"filename": image_dict['img']
		}
	}

	response = requests.post(
		"{}/products/{}/images.json".format(SHOPIFY_ENDPOINT, product_id),
		json=payload,
		headers=headers
	)

	return response