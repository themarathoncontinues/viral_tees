import cv2
import json
import logging as vt_logging
import luigi
import os
import pandas as pd
import requests
import pickle

from datetime import datetime
from dotenv import load_dotenv
from json import JSONEncoder
from luigi.contrib.external_program import ExternalProgramTask
from luigi.contrib.mongodb import MongoCellTarget, MongoRangeTarget
from pathlib import Path
from subprocess import Popen, PIPE

from utils.constants import \
    SRC_DIR, \
    LOG_DIR, \
    DATA_DIR, \
    TRENDS_DIR, \
    TRIMMED_DIR, \
    IMAGES_DIR, \
    SHIRTS_DIR, \
    SHIRT_BG, \
    SHOPIFY_JSON, \
    RESPONSE_JSON, \
    ENV_PATH, \
    TMP_DIR


load_dotenv(dotenv_path=ENV_PATH)

MONGO_SERVER = os.environ['MONGO_SERVER']
MONGO_PORT = int(os.environ['MONGO_PORT'])
MONGO_DATABASE = os.environ['MONGO_DATABASE']

DATESTRFORMAT = "%Y%m%d_%H%M%S"

LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / datetime.now().strftime(f"vt_{DATESTRFORMAT}.log")
vt_logging.basicConfig(
    level=vt_logging.INFO,
    filename=LOG_FILE
)

locations = [
    'usa-nyc',
    'usa-lax',
    'usa-chi',
    'usa-dal',
    'usa-hou',
    'usa-wdc',
    'usa-mia',
    'usa-phi',
    'usa-atl',
    'usa-bos',
    'usa-sfo',
    'usa-det',
    'usa-phx',
    'usa-sea',
]


####### UTILITY TASKS

class DeepClean(ExternalProgramTask):

    def program_args(self):
        vt_logging.warning('Cleaned data drive.')
        return ['{}/execs/clean_data.sh'.format(SRC_DIR)]

####### PIPELINE

class StartLogging(luigi.Task):

    date = luigi.DateMinuteParameter()

    def run(self):
        log = self.output().open('w')
        log.write('Starting viral tees log: {}'.format(self.date))
        log.close()
        vt_logging.info('Starting internal logger.')


    def output(self):
        fname = 'vt_{}.log'.format(self.date.strftime(DATESTRFORMAT)).replace(' ', '_')
        fout = LOG_DIR / fname
        os.makedirs(os.path.dirname(fout), exist_ok=True)
        return luigi.LocalTarget(fout)

##################################################

class QueryTwitterTrends(luigi.Task):

    date = luigi.DateMinuteParameter()
    loc = luigi.Parameter()

    def requires(self):
        return StartLogging(date=self.date)

    def output(self):
        fname = 'trends_{}_{}.json'.format(self.date.strftime(DATESTRFORMAT), self.loc)
        fout = TRENDS_DIR / fname

        return luigi.LocalTarget(fout)

    def run(self):
        from utils.retrieve_trends import auth, get_trends

        api = auth()
        data = get_trends(api, self.loc)
        f = self.output().open('w')
        json.dump(data, f)
        f.close()
        vt_logging.info('Querying Twitter trends.')


class StoreTrendsData(luigi.Task):

    date = luigi.DateMinuteParameter()
    loc = luigi.Parameter()

    def requires(self):
        return QueryTwitterTrends(date=self.date, loc=self.loc)

    def output(self):
        from models.mongo import connect_db
        
        idx = Path(self.requires().output().path).stem
        
        return MongoCellTarget(
            connect_db(MONGO_SERVER, MONGO_PORT),
            MONGO_DATABASE,
            'trends',
            idx,
            'scope'
        )

    def run(self):
        query_json = self.requires().output().path
        f = open(query_json, 'r')
        data = json.load(f)

        data.update({
            'luigi_at': self.date,
            'luigi_loc': self.loc,
            'luigi_fp': Path(self.requires().output().path).stem,
            'luigi_status': 'full_trend'
        })

        self.output().write(data)


class StoreTrimTrendsData(luigi.Task):

    date = luigi.DateMinuteParameter()
    loc = luigi.Parameter()

    def requires(self):
        return StoreTrendsData(date=self.date, loc=self.loc)

    def output(self):
        from models.mongo import connect_db

        name = f"trim_trends_{self.date.strftime(DATESTRFORMAT)}_{self.loc}"

        return MongoCellTarget(
            connect_db(MONGO_SERVER, MONGO_PORT),
            MONGO_DATABASE,
            'trimmed',
            name,
            'scope'
        )

    def run(self):
        from utils.cref_trends import generate_unique_trends
        data = self.requires().output().read()

        # manipulate data in some way
        data['trends'] = data['trends'][:5]
        trend_lst = [d['name'] for d in data['trends']]

        trends_out = generate_unique_trends(data)

        # we should save this down to disk also
        # need 2 targets
        data.update({
            'luigi_fp': 'trim_{}'.format(data['luigi_fp']),
            'luigi_status': 'trimmed_trend',
            'luigi_all_trend_list': trend_lst,
            'luigi_unique_trend_list': trends_out
        })

        self.output().write(data)


class StoreImageTweets(luigi.Task):

    date = luigi.DateMinuteParameter()
    loc = luigi.Parameter()

    def requires(self):
        return StoreTrimTrendsData(date=self.date, loc=self.loc)

    def output(self):
        from models.mongo import connect_db

        name = f"img_tweets_{self.date.strftime(DATESTRFORMAT)}_{self.loc}"

        return MongoCellTarget(
            connect_db(MONGO_SERVER, MONGO_PORT),
            MONGO_DATABASE,
            'tweets',
            name,
            'scope'
        )

    def run(self):
        from utils.get_images import image_parser, sort_tweets_with_images

        data = self.requires().output().read()
        import ipdb; ipdb.set_trace()
        trends = data['luigi_unique_trend_list']

        tweets = image_parser(trends)
        tweets = sort_tweets_with_images(tweets)
        tweets = {'tweets': tweets, 'loc': self.loc, 'date': self.date}

        self.output().write(tweets)

##################################################

class OutputTwitterTasks(luigi.WrapperTask):

    date = luigi.DateMinuteParameter(default=datetime.now())

    def requires(self):

        for loc in locations:
         yield StoreImageTweets(date=self.date, loc=loc)

    def output(self):

        # clean this directory up
        fout = RESPONSE_JSON / 'summary_{}.json'.format(self.date.strftime(DATESTRFORMAT))
        return luigi.LocalTarget(str(fout))

    def run(self):

        summary = {}

        for prereq in self.requires():
            datestamp = self.date.strftime(DATESTRFORMAT)
            tag = f"{datestamp}_{prereq.to_str_params()['loc']}"
            summary[tag] = prereq.output().read()
            summary[tag]['date'] = datestamp

        report = self.output().open('w')
        json.dump(summary, report)
        report.close()

##################################################

##################################################

##################################################


class SaveImage(luigi.Task):

    date = luigi.DateMinuteParameter()
    loc = luigi.Parameter()
    tweet = luigi.DictParameter()

    def output(self):

        fname = f"{abs(hash(self.tweet['media_url']))}_{self.date.strftime(DATESTRFORMAT)}_{self.loc}.jpg"
        fout = IMAGES_DIR / fname
        os.makedirs(os.path.dirname(fout), exist_ok=True)
        return luigi.LocalTarget(fout)

    def run(self):

        response = requests.get(self.tweet['media_url']).content
        f = open(self.output().path, 'wb')
        f.write(response)
        f.close()


class CropImage(luigi.Task):

    date = luigi.DateMinuteParameter()
    loc = luigi.Parameter()
    tweet = luigi.DictParameter()

    def requires(self):

        return SaveImage(loc=self.loc, date=self.date, tweet=self.tweet)

    def output(self):

        fname = f"cropped_{abs(hash(self.tweet['media_url']))}_{self.date.strftime(DATESTRFORMAT)}_{self.loc}.jpg"
        fout = IMAGES_DIR / fname
        os.makedirs(os.path.dirname(fout), exist_ok=True)
        return luigi.LocalTarget(fout)

    def run(self):
        from utils.image_munge import run as munge

        image = munge({'photopath': self.input().path})

        f = open(self.output().path, 'wb')
        cv2.imwrite(f.name, image)
        f.close()

class ParseImageTweets(luigi.Task):

    date = luigi.DateMinuteParameter()
    loc = luigi.Parameter()

    def requires(self):
        from models.mongo import connect_db, get_collection, find_by_id

        client = connect_db()
        col = get_collection(client, 'tweets', db=MONGO_DATABASE)
        query = f"img_tweets_{self.date.strftime(DATESTRFORMAT)}_{self.loc}"
        doc = find_by_id(col, query)
        client = client.close()

        for tw in doc['scope']['tweets']:
            yield CropImage(loc=self.loc, date=self.date, tweet=tw)

    def output(self):
        from models.mongo import connect_db

        name = f"images_{self.date.strftime(DATESTRFORMAT)}_{self.loc}"

        return MongoCellTarget(
            connect_db(MONGO_SERVER, MONGO_PORT),
            MONGO_DATABASE,
            'images',
            name,
            'scope'
        )

    def run(self):

        images = []

        for req in self.requires():
            data = dict(req.tweet.get_wrapped())
            data.update({
                'img_path': req.output().path,
                'crop_path': req.requires().output().path
            })

            images.append(data)

        images = {'images': images, 'loc': self.loc, 'date': self.date}
        self.output().write(images)


class OutputImageTasks(luigi.WrapperTask):
    
    date = luigi.DateMinuteParameter(default=datetime.now())

    def requires(self):
        from models.mongo import connect_db, get_collection, find_by_id

        for loc in locations:
            client = connect_db()
            col = get_collection(client, 'tweets', MONGO_DATABASE)
            client = client.close()
            yield ParseImageTweets(loc=loc, date=self.date)


        # import ipdb; ipdb.set_trace()


class ImageOverlay(luigi.Task):

    date = luigi.DateMinuteParameter()
    loc = luigi.Parameter()
    args_dict = {'image': '', 'background': '', 'output': ''}

    def requires(self):
        return [SaveImages(date=self.date, loc=self.loc)]

    def output(self):
        fname = 'shirt_{}'.format(self.args_dict['image'].split('/')[-1])
        fout = SHIRTS_DIR / fname

        return luigi.LocalTarget(fout)

    def run(self):
        from utils.image_overlay import run as image_overlay

        args_dict = {
            'image': self.requires()[0].output().path,
            'background': str(SHIRT_BG.absolute()),
            'output': self.output().path
        }
        self.args_dict = args_dict

        img = image_overlay(args_dict)

        fname = self.output().path
        os.makedirs(os.path.dirname(fname), exist_ok=True)
        f = open(fname, 'wb')
        cv2.imwrite(f.name, img)
        f.close()
        vt_logging.info('T-Shirt generated.')


class GenerateData(luigi.Task):

    date = luigi.DateMinuteParameter()
    loc = luigi.Parameter()

    def requires(self):
        return [ImageOverlay(date=self.date, loc=self.loc)]

    def run(self):
        image_fp = self.requires()[0].output().path
        title = image_fp.split('/')[-1].split('_')[1]
        
        og_d = TrimTrendsData(date=self.date, loc=self.loc).output().path
        df = pd.read_csv(og_d)
        df = df[df['name'] == title]

        tweet_volume = df['tweet_volume'][0]
        tweet_url = df['url'][0]

        opath = og_d.split('/')[-1].replace('csv', 'json')
        out = SHOPIFY_JSON / opath
        fout = str(out.absolute()).replace('trimmed_', '')

        meta_dict = {
            'og': og_d,
            'tweet_volume': str(tweet_volume),
            'tweet_url': tweet_url,
            'img': image_fp,
            'title': title,
            'load': fout
        }

        f = open(self.output().path, 'w')
        json.dump(meta_dict, f, indent=4)
        f.close()
        vt_logging.info('JSON data generated.')


    def output(self):
        og_d = TrimTrendsData(date=self.date, loc=self.loc).output().path
        opath = og_d.split('/')[-1].replace('csv', 'json')
        out = SHOPIFY_JSON / opath
        fout = str(out.absolute()).replace('trimmed_', '')
        os.makedirs(os.path.dirname(fout), exist_ok=True)

        return luigi.LocalTarget(fout)


class PostShopify(luigi.Task):

    date = luigi.DateMinuteParameter()
    loc = luigi.Parameter()

    def requires(self):
        return[GenerateData(date=self.date, loc=self.loc)]

    def output(self):
        fout = '{}.json'.format(
            Path(self.requires()[0].output().path).stem
        )
        fout = RESPONSE_JSON / fout
        os.makedirs(os.path.dirname(fout), exist_ok=True)
        return luigi.LocalTarget(str(fout.absolute()))

    def run(self):
        from utils.post_shopify import create_product, post_image

        dfp = self.requires()[0].output().path
        with open(dfp) as f:
            data = json.load(f)

        input_dict = {
            'title': data['title'],
            'body_html': 'Volume: {}'.format(data['tweet_volume']),
        }

        response = create_product(input_dict)

        img_dict = {
            'img': data['img']
        }

        img_response = post_image(img_dict, response)

        r_dict = response.json()
        f = open(self.output().path, 'w')
        json.dump(r_dict, f, indent=4)
        f.close()


# class RunPipeline(luigi.WrapperTask):

#     date = luigi.DateMinuteParameter(default=datetime.now())

#     def requires(self):
    
#         yield OutputTwitterTasks(self.date)
#         yield OutputImageTasks(self.date)

#         return tasks

#     # def run(self):
#     #     log = self.output().open('w')
#     #     log.write('Ending viral tees log: {}'.format(self.date))
#     #     log.close()

#     # def output(self):
#     #     fname = 'final_vt_{}.log'.format(self.date)
#     #     fout = LOG_DIR / fname

#     #     return luigi.LocalTarget(fname)


if __name__ == '__main__':
    # import ipdb; ipdb.set_trace()
    # date = luigi.DateMinuteParameter(default=datetime.now())
    date = datetime.now()

    luigi.build([OutputTwitterTasks(date=date)], workers=1)
    luigi.build([OutputImageTasks(date=date)], workers=1)
    # import ipdb; ipdb.set_trace()
    luigi.run()
