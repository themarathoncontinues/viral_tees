import luigi
import pickle
from datetime import datetime


class QueryTwitterTrend(luigi.ExternalTask):

    date = luigi.DateMinuteParameter(default=datetime.now())
    country_code = luigi.Parameter(default='usa')

    def requires(self):
        return []

    def output(self, **kwargs):
        kwargs.setdefault('loc', 'dummy')

        return luigi.LocalTarget(
            "data/trends/trends_{}_{}.csv".format(self.date.strftime('%m%d_%Y_%H%M'), kwargs['loc']))

    def run(self):
        from retrieve_trends import run as retrieve_trends
        import pandas as pd

        args_dict = {
            'location': [self.country_code]
        }

        df_container = retrieve_trends(args_dict)
        f = self.output(loc=self.country_code).open('w')
        df_container[self.country_code].to_csv(f, sep=',', encoding='utf-8')
        f.close()


class TrendsTaskWrapper(luigi.WrapperTask):

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
            yield QueryTwitterTrend(country_code=loc)

    def run(self):
        self.complete()

class EmailTwitterTrends(luigi.ExternalTask):

    def requires(self):
        return TrendsTaskWrapper()

    def output(self):
        date = datetime.now()
        str_date = date.strftime('%m%d_%Y_%H%M')

        return luigi.LocalTarget("data/trends/trends_{}.pickle".format(str_date))

    def run(self):
        from send_email import run as execute, send_message
        
        args_dict = {
            {'authentication': ['token.pickle'], 'receivers': ['mitchbregs@gmail.com'], 'attachments': self.input()}
        }

        auth, sender, msg = execute(args_dict)

        send_message(auth, sender, msg)

        f = self.output().open('w')
        pickle.dump((auth, sender, msg), f)
        f.close()


if __name__ == '__main__':
    luigi.run()
