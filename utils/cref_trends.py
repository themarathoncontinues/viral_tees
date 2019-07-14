import luigi.contrib.mongodb
import os
from dotenv import load_dotenv
from models.mongo import connect_db, get_collection, retrieve_all_data, find_by_luigi_at
from utils.constants import ENV_PATH

load_dotenv(dotenv_path=ENV_PATH)

MONGO_DATABASE = os.environ['MONGO_DATABASE']


def generate_unique_trends(data):
    luigi_at = data['luigi_at']
    current_trends = [x['name'] for x in data['trends']]

    conn = connect_db()
    trimmed = get_collection(conn, col='trimmed', db=MONGO_DATABASE)
    captured_trimmed = find_by_luigi_at(trimmed, luigi_at)

    check_trend_list = []
    for x in captured_trimmed:
        check_trend_list.append(x['scope']['luigi_all_trend_list'])

    output_list = []
    for trend in current_trends:
        if not any(trend in sublist for sublist in check_trend_list):
            output_list.append(trend)

    conn = conn.close()

    return output_list
