import functools
import logging
import os
import pandas as pd
import time

from dotenv import load_dotenv
from luigi import Target
from pathlib import Path
from pymongo import MongoClient, ASCENDING, DESCENDING
from utils.constants import ENV_PATH, TRENDS_DIR


load_dotenv(dotenv_path=ENV_PATH)

MONGO_SERVER = os.environ['MONGO_SERVER']
MONGO_PORT = int(os.environ['MONGO_PORT'])
MONGO_DATABASE = os.environ['MONGO_DATABASE']
# Mongo requires a server port of type int.


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


def retrieve_all_data(col, limit=3500):
	data = [x for x in col.find().sort('datestamp', DESCENDING).limit(limit)]
	return data


def find_by_id(col, idx):
	return col.find_one({'_id': idx})
