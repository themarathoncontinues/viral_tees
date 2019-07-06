from flask import Flask, request, render_template, redirect, url_for
from models.mongo import connect_db, get_collection, retrieve_all_data, find_by_id
from utils.constants import IMAGES_DIR
from utils.post_shopify import get_products, delete_products


app = Flask(__name__)
app.debug = True
app.secret_key = 'secret'
app._static_folder = str(IMAGES_DIR)

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
	col = get_collection(conn, 'trends')
	data = retrieve_all_data(col)
	conn = conn.close()

	return render_template(
		'trends.html',
		header='Trends',
		data=data
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
	data = [x for x in IMAGES_DIR.iterdir()]
	data = {x.name: str(x) for x in data}

	return render_template(
		'images.html',
		header='Images',
		data=data
	)


if __name__ == "__main__":
	app.run()
