import itertools
import os

from dotenv import load_dotenv
from flask import Flask, request, render_template, redirect, send_from_directory, url_for
from models.mongo import connect_db, get_collection, retrieve_all_data, find_by_id
from utils.constants import SRC_DIR, IMAGES_DIR, LOG_DIR, ENV_PATH
from utils.post_shopify import get_products, delete_products


load_dotenv(dotenv_path=ENV_PATH)

LOCAL = os.getenv('IP_ADDRESS')


app = Flask(__name__)
app.debug = True
app.secret_key = 'secret'
app.config['STATIC_FOLDER'] = str(LOG_DIR)

@app.route('/')
@app.route('/home')
def index():
    return render_template(
    	'index.html',
    	header='Home'
    )


@app.route('/trends-view')
def trend_data():
	conn = connect_db()
	trends = get_collection(conn, 'trends')
	trends_data = retrieve_all_data(trends)
	conn = conn.close()

	return render_template(
		'trends.html',
		header='Trends',
		subheader='Data',
		data=trends_data
	)

@app.route('/tweets-view')
def tweet_data():
	conn = connect_db()
	tweets = get_collection(conn, 'tweets')
	tweets_data = retrieve_all_data(tweets)
	conn = conn.close()

	import ipdb; ipdb.set_trace()

	return render_template(
		'tweets.html',
		header='Tweets',
		subheader='Data',
		data=tweets_data
	)

@app.route('/shopify-view')
def shop_data():
	data = get_products()
	data = sorted(data, key=lambda x: x['created_at'], reverse=True)

	return render_template(
		'shopify.html',
		header='Shopify',
		subheader='Live Products',
		data=data
	)


@app.route('/shopify-delete')
def shop_delete():
	data = get_products()

	try:
		delete_products(data)
	except AssertionError:
		return redirect(url_for('shop_data'), code=302)

	return redirect(url_for('shop_data'), code=302)


@app.route('/images-view')
def image_data():
	data = [str(x.relative_to(SRC_DIR)) for x in IMAGES_DIR.iterdir()]

	final = []
	for check_item in data:
		check = check_item.split('_')[-4]
		for search in data:
			if check in search and check_item != search:
				pair = (check_item, search)
				final.append(pair)
			else:
				pass

	return render_template(
		'images.html',
		header='Images',
		data=final
	)


@app.route('/logs-view')
@app.route('/logs-view/<fname>')
def logs_data(fname=None):
	if fname:
		return send_from_directory(directory=LOG_DIR, filename=fname)
	else:
		data = [x for x in LOG_DIR.iterdir()]
		data = sorted(data, reverse=True)
		data = {x.name: str(x) for x in data}

		return render_template(
			'logs.html',
			header='Reports',
			data=data
		)



if __name__ == "__main__":
	# if you want to access from any device on your network
	# change the '0.0.0.0' to your IP address.
	# this domain will allow you to see the site from any
	# device connected to your network.
	app.run(host=LOCAL, port=5000)
