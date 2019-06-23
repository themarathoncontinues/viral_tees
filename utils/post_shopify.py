import os
import requests

from dotenv import load_dotenv

load_dotenv('.env')

SHOPIFY_ENDPOINT = os.environ['SHOPIFY_API']

def create_product(input_dict):

	"""
	Example payload

	{'product': {'admin_graphql_api_id': 'gid://shopify/Product/1862885474394',
	             'body_html': 'product for testing body',
	             'created_at': '2019-06-22T18:45:39-04:00',
	             'handle': 'product-for-testing-1',
	             'id': 1862885474394,
	             'image': None,
	             'images': [],
	             'options': [{'id': 2572791513178,
	                          'name': 'Title',
	                          'position': 1,
	                          'product_id': 1862885474394,
	                          'values': ['Default Title']}],
	             'product_type': '',
	             'published_at': '2019-06-22T18:45:39-04:00',
	             'published_scope': 'web',
	             'tags': '',
	             'template_suffix': None,
	             'title': 'product for testing',
	             'updated_at': '2019-06-22T18:45:39-04:00',
	             'variants': [{'admin_graphql_api_id': 'gid://shopify/ProductVariant/17372859105370',
	                           'barcode': None,
	                           'compare_at_price': None,
	                           'created_at': '2019-06-22T18:45:39-04:00',
	                           'fulfillment_service': 'manual',
	                           'grams': 0,
	                           'id': 17372859105370,
	                           'image_id': None,
	                           'inventory_item_id': 17777622286426,
	                           'inventory_management': None,
	                           'inventory_policy': 'deny',
	                           'inventory_quantity': 0,
	                           'old_inventory_quantity': 0,
	                           'option1': 'Default Title',
	                           'option2': None,
	                           'option3': None,
	                           'position': 1,
	                           'price': '0.00',
	                           'product_id': 1862885474394,
	                           'requires_shipping': True,
	                           'sku': '',
	                           'taxable': True,
	                           'title': 'Default Title',
	                           'updated_at': '2019-06-22T18:45:39-04:00',
	                           'weight': 0.0,
	                           'weight_unit': 'lb'}],
	             'vendor': 'viral tees gubr'}}
	"""

	payload = {'product': input_dict}
	# 	"product": {
	# 		"title": "product for testing",
	# 		"body_html": "product for testing body",
	# 	}
	# }

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

