import os
import pandas as pd

from dotenv import load_dotenv
from luigi import Target
from pathlib import Path
from pymongo import MongoClient
from utils.constants import ENV_PATH, TRENDS_DIR


load_dotenv(dotenv_path=ENV_PATH)

MONGO_SERVER = os.environ['MONGO_SERVER']
MONGO_PORT = int(os.environ['MONGO_PORT'])
MONGO_DATABASE = os.environ['MONGO_DATABASE']
MONGO_COLLECTION = os.environ['MONGO_COLLECTION']
# Mongo requires a server port of type int.


class MongoTarget(Target):

	def __init__(self, predicate):
		self.client = MongoClient(MONGO_SERVER, MONGO_PORT)
		self.database = MONGO_DATABASE
		self.collection = MONGO_COLLECTION
		self.predicate = predicate

	def exists(self):
		db = self.client[self.database]
		one = db[self.collection].find_one(self.predicate)
		self.client.close()
		return one is not None

	def persist(self, data):
		db = self.client[self.database]
		col = db[self.collection]

		if isinstance(data, list):
			result = col.insert_many(data)
			info = result.inserted_ids
		elif isinstance(data, dict):
			result = col.insert_one(data)
			info = result.inserted_id
		else:
			raise TypeError('Passed the wrong type to insert MongoDB record.')

		self.client.close()

		return info


# quick utility functions
def connect_db(server=MONGO_SERVER, port=MONGO_PORT):
	client = MongoClient(server, port)
	return client

def get_database(client, db=MONGO_DATABASE):
	return client[db]

def get_collection(db, col=MONGO_COLLECTION):
	return db[col]

def post_document(data, col):
	assert isinstance(data, dict)
	result = col.insert_one(data)
	return result

def retrieve_all_data(col):
	return [x for x in col.find({})]


