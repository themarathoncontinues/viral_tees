import luigi
import pandas as pd
import pickle

from datetime import datetime
from pathlib import Path

from constants import TRENDS_DIR, TRIMMED_DIR


class QueryTwitterTrend(luigi.Task):

    date = luigi.DateMinuteParameter(default=datetime.now())
    country_code = luigi.Parameter()

    def output(self, **kwargs):
        kwargs.setdefault('loc', self.country_code)
        fname = 'trends_{}_{}.csv'.format(self.date.strftime('%m%d_%Y_%H%M'), kwargs['loc'])
        fout = TRENDS_DIR / fname

        return luigi.LocalTarget(fout)

    def run(self):
        from retrieve_trends import run as retrieve_trends

        args_dict = {
            'location': [self.country_code]
        }

        df_container = retrieve_trends(args_dict)
        f = self.output(loc=self.country_code).open('w')

        df_container[self.country_code].to_csv(f, sep=',', encoding='utf-8', index=False)
        f.close()


class TrendsTaskWrapper(luigi.WrapperTask):

    is_complete = False

    def requires(self):
        locations = [
                'usa-nyc',
                'usa-lax',
                'usa-chi',
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

        for loc in locations:
            yield QueryTwitterTrend(country_code=loc)

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
        fout = TRIMMED_DIR / '{}_{}.csv'.format('trimmed', fp.stem)

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

# class EmailTwitterTrends(luigi.ExternalTask):

#     def requires(self):
#         return TrendsTaskWrapper()

#     def output(self):
#         date = datetime.now()
#         str_date = date.strftime('%m%d_%Y_%H%M')

#         return luigi.LocalTarget("data/trends/trends_{}.pickle".format(str_date))

#     def run(self):
#         from send_email import run as execute, send_message
        
#         args_dict = {
#             {'authentication': ['token.pickle'], 'receivers': ['mitchbregs@gmail.com'], 'attachments': self.input()}
#         }

#         auth, sender, msg = execute(args_dict)

#         send_message(auth, sender, msg)

#         f = self.output().open('w')
#         pickle.dump((auth, sender, msg), f)
#         f.close()


if __name__ == '__main__':
    luigi.run()
