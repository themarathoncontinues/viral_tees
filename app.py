from flask import Flask, request, render_template, redirect
from models.mongo import connect_db, get_collection, retrieve_all_data, find_by_id
from utils.post_shopify import get_products, delete_products

app = Flask(__name__)

@app.route('/')
@app.route('/home')
def index():
    return render_template('index.html')

@app.route('/trends-view')
def trend_data():
	conn = connect_db()
	col = get_collection(conn, 'trends')
	data = retrieve_all_data(col)
	conn = conn.close()

	return render_template(
		'trends.html',
		header='Trends',
		subheader='Data',
		data=data
	)

@app.route('/shopify-view')
def shop_data():
	data = get_products()

	return render_template(
		'shopify.html',
		header='Shopify',
		subheader='Live Shirts',
		data=data
	)

if __name__ == "__main__":
    app.run(debug=True)