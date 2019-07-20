import os
from dotenv import load_dotenv
import datetime
import functools
import logging
import traceback
import slack
import sys
from utils.constants import \
    ENV_PATH, \
    LOG_DIR

load_dotenv(dotenv_path=ENV_PATH)

SLACK_USER_TOKEN = os.environ['SLACK_BOT_TOKEN']


def create_logger():
    """
    Creates a logging object and returns it
    """
    logger = logging.getLogger("example_logger")
    logger.setLevel(logging.INFO)
 
    # create the logging file handler
    date = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    fout = LOG_DIR / f'error.log'
    fh = logging.FileHandler(fout)
 
    fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(fmt)
    fh.setFormatter(formatter)
 
    # add handler to logger object
    logger.addHandler(fh)
    return logger
 
 
def exception(function):
    """
    A decorator that wraps the passed in function and logs
    exceptions should one occur
    """
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        # logger = create_logger()
        try:
            return function(*args, **kwargs)

        except Exception as ex:
            # log the exception

            date = datetime.datetime.now()
            # err = "There was an exception in "
            # err += function.__name__
            # logger.exception(err)

            client = slack.WebClient(token=SLACK_USER_TOKEN)

            msg = '''
##############################
==============================

*Error Alert*

{}

Function: `{}`
Error: `{}`

`{}`

```
{}: {}
```


            '''.format(
                date.strftime('%Y %b %d, %H:%M:%S'),
                function.__repr__(),
            	type(ex).__name__,
            	function.__code__,
            	type(ex).__name__,
            	str(ex)
            )

            response = client.chat_postMessage(
            	channel='#tech',
            	text=msg
            )

            raise
    return wrapper








