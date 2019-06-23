import cv2
import json
import logging as vt_logging
import luigi
import os
import pandas as pd
import requests
import pickle

from datetime import datetime
from luigi.contrib.external_program import ExternalProgramTask
from pathlib import Path
from subprocess import Popen, PIPE

from utils.constants import \
    LOG_DIR, \
    DATA_DIR, \
    TRENDS_DIR, \
    TRIMMED_DIR, \
    IMAGES_DIR, \
    SHIRTS_DIR, \
    SHIRT_BG, \
    SHOPIFY_JSON

# LOG_FORMAT='%(asctime)s,%(msecs)d|%(name)s|%(levelname)s -',
LOG_FILE='logs/{}'.format(datetime.now().strftime("vt_%Y-%m-%d_%H:%M:%S.log"))
vt_logging.basicConfig(
    level=vt_logging.INFO,
    filename=LOG_FILE
)

####### UTILITY TASKS

class DeepClean(ExternalProgramTask):

    def program_args(self):
        vt_logging.warning('Cleaned data drive.')
        return ['./execs/clean_data.sh']

    def output(self):
        return luigi.LocalTarget('output')


####### PIPELINE

class StartLogging(luigi.Task):

    date = luigi.DateMinuteParameter()

    def run(self):
        log = self.output().open('w')
        log.write('Starting viral tees log: {}'.format(self.date))
        log.close()
        vt_logging.info('Starting internal logger.')


    def output(self):
        fname = 'vt_{}.log'.format(self.date).replace(' ', '_')
        fout = LOG_DIR / fname
        os.makedirs(os.path.dirname(fout), exist_ok=True)
        return luigi.LocalTarget(fout)


class QueryTwitter(luigi.Task):

    date = luigi.DateMinuteParameter()
    loc = luigi.Parameter()

    def requires(self):
        return [StartLogging(date=self.date)]

    def output(self):
        fname = 'trends_{}_{}.csv'.format(self.date.strftime('%m%d_%Y_%H%M'), self.loc)
        fout = TRENDS_DIR / fname

        return luigi.LocalTarget(fout)

    def run(self):
        from utils.retrieve_trends import run as retrieve_trends

        args_dict = {
            'location': [self.loc]
        }

        df_container = retrieve_trends(args_dict)
        f = self.output().open('w')
        df_container[self.loc].to_csv(f, sep=',', encoding='utf-8', index=False)
        f.close()
        vt_logging.info('Querying Twitter trends.')



class TrimTrendsData(luigi.Task):

    date = luigi.DateMinuteParameter()
    loc = luigi.Parameter()

    @staticmethod
    def trim_data(csv):
        df = pd.read_csv(csv, sep=',', engine='python')
        df.sort_values(['tweet_volume'], ascending=False)
        return df.head(n=5)

    def requires(self):
        return [QueryTwitter(date=self.date, loc=self.loc)]

    def output(self):
        fname = self.requires()[0].output().path.split('/')[-1]
        fname = '{}_{}'.format('trimmed', fname)
        fout = TRIMMED_DIR / fname

        return luigi.LocalTarget(fout)

    def run(self):
        fp = self.requires()[0].output().path
        trimmed_df = self.trim_data(fp)

        f = self.output().open('w')
        trimmed_df.to_csv(f, sep=',', encoding='utf-8', index=False)
        f.close()
        vt_logging.info('Munging Twitter trends.')



class SaveImages(luigi.Task):

    date = luigi.DateMinuteParameter()
    loc = luigi.Parameter()
    img_dict = ['', '', '']

    def requires(self):
        return [TrimTrendsData(date=self.date, loc=self.loc)]

    def output(self):
        # fname = self.requires()[0].output().path.split('/')[-1].replace('.csv', '.jpg')
        fname = '{}_{}.jpg'.format(self.img_dict[0], self.img_dict[1])
        fout = IMAGES_DIR / fname

        return luigi.LocalTarget(fout)

    def run(self):
        from utils.get_images import run as get_images

        args_dict = {
            'input': self.requires()[0].output().path,
            'output': self.output().path
        }

        self.img_dict = get_images(args_dict)
        response = requests.get(self.img_dict[2]).content

        fname = self.output().path
        os.makedirs(os.path.dirname(fname), exist_ok=True)
        f = open(fname, 'wb')
        f.write(response)
        f.close()
        vt_logging.info('Saving Twitter trends images.')


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
        title = self.requires()[0].output().path.split('/')[2].split('_')[1]

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
        pass

    def run(self):
        from utils.post_shopify import create_product

        pass

class RunPipeline(luigi.WrapperTask):

    date = datetime.now()
    date = luigi.DateMinuteParameter(default=date)

    def requires(self):

        base_tasks = [StartLogging(date=self.date)]

        ####### CONFIG

        locations = [
                'usa-nyc',
                'usa-lax',
                # 'usa-chi',
                # 'usa-dal',
                # 'usa-hou',
                # 'usa-wdc',
                # 'usa-mia',
                # 'usa-phi',
                # 'usa-atl',
                # 'usa-bos',
                # 'usa-phx',
                # 'usa-sfo',
                # 'usa-det',
                # 'usa-sea',
        ]

        twitter_tasks = [QueryTwitter(date=self.date, loc=loc) for loc in locations]
        munging_tasks = [TrimTrendsData(date=self.date, loc=loc) for loc in locations]
        image_tasks = [SaveImages(date=self.date, loc=loc) for loc in locations]
        image_overlay = [ImageOverlay(date=self.date, loc=loc) for loc in locations]
        generate_data = [GenerateData(date=self.date, loc=loc) for loc in locations]
        shopify_tasks = [PostShopify(date=self.date, loc=loc) for loc in locations]

        tasks = base_tasks + \
            twitter_tasks + \
            munging_tasks + \
            image_tasks + \
            image_overlay + \
            generate_data + \
            shopify_tasks

        return tasks

    def run(self):
        log = self.output().open('w')
        log.write('Ending viral tees log: {}'.format(self.date))
        log.close()

    def output(self):
        fname = 'final_vt_{}.log'.format(self.date)
        fout = LOG_DIR / fname

        return luigi.LocalTarget(fname)


if __name__ == '__main__':
    luigi.run()
