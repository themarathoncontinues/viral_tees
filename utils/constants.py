import os
import sys

from pathlib import Path


if sys.platform == 'darwin':
	SRC_DIR = Path(os.getcwd()).absolute()
elif sys.platform == 'linux2' or sys.platform == 'linux':
	SRC_DIR = Path('/home/git/viral_tees')
else:
	raise Exception('This system is not supported.')

DATA_DIR = SRC_DIR / 'data'
TRENDS_DIR = DATA_DIR / 'trends'
TRIMMED_DIR = DATA_DIR / 'trimmed'
IMAGES_DIR = DATA_DIR / 'images'
LOG_DIR = SRC_DIR / 'logs'
SHIRTS_DIR = DATA_DIR / 'shirts'
STATIC_DIR = SRC_DIR / 'static'
SHIRT_BG = STATIC_DIR / 'background.jpg'
SHOPIFY_JSON = DATA_DIR / 'json'
RESPONSE_JSON = DATA_DIR / 'response'
