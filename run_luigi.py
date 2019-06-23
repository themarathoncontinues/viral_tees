import luigi
import pandas as pd
import pickle

from datetime import datetime
from luigi.contrib.external_program import ExternalProgramTask
from pathlib import Path
from subprocess import Popen, PIPE

from constants import DATA_DIR, TRENDS_DIR, TRIMMED_DIR

####### UTILITY TASKS

class CleanData(ExternalProgramTask):

    def program_args(self):
        return ['./clean_data.sh']

    def output(self):
        return luigi.LocalTarget('output')


class QueryTwitterTrend(luigi.Task):

    date = luigi.DateMinuteParameter(default=datetime.now())
    location = luigi.Parameter()

    def output(self):
        fname = 'trends_{}_{}.csv'.format(self.date.strftime('%m%d_%Y_%H%M'), self.location)
        fout = TRENDS_DIR / fname

        return luigi.LocalTarget(fout)

    def run(self):
        from retrieve_trends import run as retrieve_trends

        args_dict = {
            'location': [self.location]
        }

        df_container = retrieve_trends(args_dict)
        f = self.output().open('w')

        df_container[self.location].to_csv(f, sep=',', encoding='utf-8', index=False)
        f.close()


class TrendsTaskWrapper(luigi.WrapperTask):

    is_complete = False

    def requires(self):
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

        for loc in locations:
            yield QueryTwitterTrend(location=loc)

        self.is_complete = True

    def complete(self):
        if self.is_complete:
            return True
        else:
            return False


class TrimTrendsData(luigi.Task):

    fp = luigi.Parameter()

    @staticmethod
    def trim_data(csv):
        df = pd.read_csv(csv, sep=',', engine='python')
        df.sort_values(['tweet_volume'], ascending=False) 
        return df.head(n=5)

    def requires(self):
        return TrendsTaskWrapper()

    def output(self):
        fname = '{}_{}.csv'.format('trimmed', Path(self.fp).stem)
        fout = TRIMMED_DIR / fname

        return luigi.LocalTarget(fout)

    def run(self):
        fp = Path(self.fp)
        trimmed_df = self.trim_data(fp)

        f = self.output().open('w')
        trimmed_df.to_csv(f, sep=',', encoding='utf-8', index=False)
        f.close()


class TrimTrendsTaskWrapper(luigi.WrapperTask):

    is_complete = False

    def requires(self):
        return TrendsTaskWrapper()

    def run(self):
        trends_data = self.requires()
        trends_path = [Path(fp.path) for fp in trends_data.input()]

        for fp in trends_path:
            yield TrimTrendsData(fp=fp)

        self.is_complete = True

    def complete(self):
        if self.is_complete:
            return True
        else:
            return False


if __name__ == '__main__':
    luigi.run()
