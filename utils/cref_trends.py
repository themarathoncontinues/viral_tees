import itertools
import os
import Levenshtein
from dotenv import load_dotenv
from models.mongo import connect_db, get_collection, retrieve_all_data, find_by_luigi_at
from utils.constants import ENV_PATH

load_dotenv(dotenv_path=ENV_PATH)

MONGO_DATABASE = os.environ['MONGO_DATABASE']


def generate_unique_trends(data):
    luigi_at = data['luigi_at']
    current_trends = [x['name'].replace('#','').lower() for x in data['trends']]
    conn = connect_db()
    trimmed = get_collection(conn, col='trimmed', db=MONGO_DATABASE)
    captured_trimmed = find_by_luigi_at(trimmed, luigi_at)

    trend_list = []
    for x in captured_trimmed:
        trends = x['scope']['trends']
        loc = x['scope']['luigi_loc']
        time = x['scope']['luigi_at']
        for item in trends:
            item.update({'loc': loc})
            item.update({'time': time})

            trend_list.append(item)

    names = list(set([x['name'] for x in trend_list]))

    htag_removal = list(set([x.replace('#', '').lower() for x in names]))
    deletes = [a for a, b in itertools.combinations(htag_removal, 2) if Levenshtein.distance(a, b) < 2]

    l_distance = [n for n in htag_removal if n not in deletes]

    check_trend_list = []
    for x in l_distance:
        check_trend_list.append(x)

    output_list = []
    for trend in current_trends:
        if not any(trend in sublist for sublist in check_trend_list):
            output_list.append(trend)

    conn = conn.close()

    return output_list
