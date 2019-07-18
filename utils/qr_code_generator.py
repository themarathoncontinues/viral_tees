import pyqrcode
from utils.constants import IMAGES_DIR


def generate_qr_code(args_dict):
    """
    Generate QR Code that points to source tweet
    :param username:
    :param tweet_id:
    :return:
    """
    username = args_dict['user']
    tweet_id = str(args_dict['tweet_id'])

    fp = f'https://twitter.com/{username}/status/{tweet_id}'
    url = pyqrcode.create(fp)
    url.svg(f"{IMAGES_DIR}/qr_{args_dict['luigi_at']}_{args_dict['luigi_loc']}.svg", scale=8)

    return fp
