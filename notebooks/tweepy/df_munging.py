import pandas as pd

df = pd.read_csv('cached_tweets.csv')
pd.set_option('display.max_colwidth', -1)
print(df.head(1))