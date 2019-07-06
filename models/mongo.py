import functools
import logging
import os
import pandas as pd
import time

from dotenv import load_dotenv
from luigi import Target
from pathlib import Path
from pymongo import MongoClient
from utils.constants import ENV_PATH, TRENDS_DIR


load_dotenv(dotenv_path=ENV_PATH)

MONGO_SERVER = os.environ['MONGO_SERVER']
MONGO_PORT = int(os.environ['MONGO_PORT'])
MONGO_DATABASE = os.environ['MONGO_DATABASE']
# Mongo requires a server port of type int.

MAX_AUTO_RECONNECT_ATTEMPTS = 5
# this is for AutoConnect exceptions


class MongoTarget(Target):

	def __init__(self, collection, predicate):
		self.client = MongoClient(MONGO_SERVER, MONGO_PORT)
		self.database = MONGO_DATABASE
		self.collection = collection
		self.predicate = predicate

	def connect(self):
		self.client = MongoClient(MONGO_SERVER, MONGO_PORT)
		return self.client()

	def exists(self):
		db = self.client[self.database]
		one = db[self.collection].find_one(self.predicate)
		self.client = self.client.close()
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

		self.client = self.client.close()
		return info


# quick utility functions
def connect_db(server=MONGO_SERVER, port=MONGO_PORT):
	client = MongoClient(server, port)
	return client

def get_database(client, db=MONGO_DATABASE):
	return client[db]

def get_collection(client, col, db=MONGO_DATABASE):
	return client[db][col]

def post_document(data, col):
	assert isinstance(data, dict)
	result = col.insert_one(data)
	return result

def retrieve_all_data(col):
	return [x for x in col.find({})]

def find_by_id(col, idx):
	return col.find_one({'_id': idx})

# this is not currently being used
def graceful_auto_reconnect(mongo_op_func):
	"""Gracefully handle a reconnection event."""
	@functools.wraps(mongo_op_func)
	def wrapper(*args, **kwargs):
		for attempt in xrange(MAX_AUTO_RECONNECT_ATTEMPTS):
			try:
				return mongo_op_func(*args, **kwargs)
			except pymongo.errors.AutoReconnect as e:
				wait_t = 0.5 * pow(2, attempt) # exponential back off
				logging.warning("PyMongo auto-reconnecting... %s. Waiting %.1f seconds.", str(e), wait_t)
				time.sleep(wait_t)

  return wrapper
