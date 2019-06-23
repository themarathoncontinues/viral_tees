import luigi
import os
import pandas as pd
import requests
import pickle

from datetime import datetime
from luigi.contrib.external_program import ExternalProgramTask
from pathlib import Path
from subprocess import Popen, PIPE

from utils.constants import LOG_DIR, DATA_DIR, TRENDS_DIR, TRIMMED_DIR, IMAGES_DIR



####### UTILITY TASKS

class CleanData(ExternalProgramTask):

    def program_args(self):
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

    def output(self):
        fname = 'vt_{}.log'.format(self.date)
        fout = LOG_DIR / fname

        return luigi.LocalTarget(fname)


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


class RunPipeline(luigi.WrapperTask):

    date = datetime.now()
    date = luigi.DateMinuteParameter(default=date)

    def requires(self):

        base_tasks = [StartLogging(date=self.date)]

        ####### CONFIG

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
                'usa-phx',
                'usa-sfo',
                'usa-det',
                'usa-sea',
        ]

        twitter_tasks = [QueryTwitter(date=self.date, loc=loc) for loc in locations]
        munging_tasks = [TrimTrendsData(date=self.date, loc=loc) for loc in locations]
        image_tasks = [SaveImages(date=self.date, loc=loc) for loc in locations]

        tasks = base_tasks + image_tasks

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
