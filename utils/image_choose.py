import os

from dotenv import load_dotenv
from models.mongo import connect_db, find_by_luigi_at
from utils.constants import ENV_PATH


load_dotenv(dotenv_path=ENV_PATH)

MONGO_SERVER = os.environ['MONGO_SERVER']
MONGO_PORT = int(os.environ['MONGO_PORT'])
MONGO_DATABASE = os.environ['MONGO_DATABASE']


def retrieve(date):
    conn = connect_db()
    db = conn[MONGO_DATABASE]
    trend_col = db['trends']
    trimmed_col = db['trimmed']
    img_col = db['images']

    # get from 3 collections
    trends = [x for x in find_by_luigi_at(trend_col, date)]
    trimmed = [x for x in find_by_luigi_at(trimmed_col, date)]
    images = [x for x in find_by_luigi_at(img_col, date)]

    conn = conn.close()

    # make sure all data is even
    assert len(trends) == len(trimmed) == len(images), 'Data lengths do not match.'

    return {
        'trends': trends,
        'trimmed': trimmed,
        'images': images
    }

def get_locations(trends, trimmed, images):

    trend_locs = [x['scope']['luigi_loc'] for x in trends]
    trimmed_locs = [x['scope']['luigi_loc'] for x in trimmed]
    image_locs = [x['scope']['luigi_loc'] for x in images]

    # make sure all locations are the same
    assert trend_locs == trimmed_locs == image_locs, 'Data locations do not match.'

    return image_locs


def associate(loc, trends, trimmed, images):

    trends_at_loc = [x for x in trends if x['scope']['luigi_loc'] == loc]
    trimmed_at_loc = [x for x in trimmed if x['scope']['luigi_loc'] == loc]
    images_at_loc = [x for x in images if x['scope']['luigi_loc'] == loc]

    return {
        loc: {
            'trends': trends_at_loc,
            'trimmed': trimmed_at_loc,
            'images': images_at_loc
        }
    }

def run(date):

    data = retrieve(date)
    locations = get_locations(data['trends'], data['trimmed'], data['images'])

    associated = {}
    for loc in locations:
        chunk = associate(loc, data['trends'], data['trimmed'], data['images'])

    return associated
