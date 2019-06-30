import base64
import os
import requests

from dotenv import load_dotenv
from utils.constants import ENV_PATH


load_dotenv(dotenv_path=ENV_PATH)

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
	"""
	Attaches image to Shopify API product.

	:param:
		

	:return:
		product_list (list):	List containing all product response
								JSONs from Shopify API.
	"""

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


def get_products():
	"""
	Returns a list of all products in form of response JSON
	from Shopify API endpoint connected to storefront.

	* Note: Shopify API allows 250 pruducts per call.

	:return:
		product_list (list):	List containing all product response
								JSONs from Shopify API.
	"""

	products = []
	is_remaining = True
	i = 1
	while is_remaining:

		if i == 1:
			params = {
				"limit": 250,
				"page": i
			}

			response = requests.get(
				"{}/products.json".format(SHOPIFY_ENDPOINT),
				params=params
			)

			products.append(response.json()['products'])
			i += 1

		elif len(products[i-2]) % 250 == 0:
			params = {
				"limit": 250,
				"page": i
			}

			response = requests.get(
				"{}/products.json".format(SHOPIFY_ENDPOINT),
				params=params
			)

			products.append(response.json()['products'])
			i += 1

		else:
			is_remaining = False

	products = [products[i][j] for i in range(0, len(products))
								for j in range(0, len(products[i]))]

	return products


def delete_products(product_list):
	"""
	Returns a list of response objects from product deletions.

	:param:
		product_list (list):	List containing all product response
								JSONs from Shopfy API.

	:return:
		responses (list):		Response objects from Shopify
								delete API endpoint.
	"""
	ids = [product['id'] for product in product_list]

	responses = []

	for idx in ids:
		response = requests.delete(
			"{}/products/{}.json".format(SHOPIFY_ENDPOINT, str(idx))
		)

		responses.append(response)

	return responses
