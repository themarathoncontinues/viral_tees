# ViralTees

Viral-Tees is a service that aims to catch the most trending topics and offer limited time access to merchandise showcasing these topics. Using the social media to track trends, we aim to be first to market with viral-tees.

### Authors

* **Mitchell Bregman** - *Initial work* - [Gallup]
* **Leon Kozlowski** - *Initial work* - [Bloomberg]

## Setup

1) `git clone {repo}`

2) `pip install -r requirements.txt`

3) `.env`:

```bash
SHOPIFY_API="{shopify-api}"
TWITTER_API_KEY="{twitter-api}"
TWITTER_API_SECRET="{twitter-api}"
TWITTER_API_TOKEN="{twitter-api}"
TWITTER_API_ACCESS="{twitter-api}"
```

4) Open 2 terminals: 
- `luigid`
- `python run_luigi.py RunPipeline`

## Tasks

1) `CleanData`

Removes `data` folder and all files within. 

2) `StartLogging`

Start logging mechanism of pipeline

3) `QueryTwitter`

For each city metro location, return a CSV dataframe containing trending tweets, with volumes and links.

4) `TrimTrendsData`

Filters Twitter trends to prepare for image saving.

5) `SaveImages`

Saves images from filtered trends data.

6) `RunPipeline`

Runs entire pipeline.

![Screen Shot](https://i.imgur.com/qSORVn4.png "Pipeline")


### References

1) [Luigi Basic Working Example](https://marcobonzanini.com/2015/10/24/building-data-pipelines-with-python-and-luigi/)

2) [Luigi Multiple Inputs and Multiple Outputs - Ex. 1](https://bionics.it/posts/luigi-tutorial)

3) [Luigi Multiple Inputs and Multiple Outputs - Ex. 2](http://rjbaxley.com/posts/2016/03/13/parallel_jobs_in_luigi.html)

4) [Gmail API](https://developers.google.com/gmail/api/guides/sending)
