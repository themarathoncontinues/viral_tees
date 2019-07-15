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

FACEBOOK_TOKEN="{facebook-api}"
FACEBOOK_APP_ID="{facebook-api}"
FACEBOOK_APP_SECRET="{facebook-api}"
FACEBOOK_AD_ACCT_ID="{facebook-api}"
FACEBOOK_BUSINESS_ID="{facebook-api}"
FACEBOOK_PAGE_ID="{facebook-api}"
FACEBOOK_PIXEL_ID="{facebook-api}"

MONGO_SERVER="{server}""
MONGO_PORT="{port}"
MONGO_DATABASE="{database}"
```

4) Open 4 terminals:
- `luigid`
- `mongod --port=$MONGO_PORT`
- `python run_luigi.py --all`
- `python app.py`

## Tasks

1) `DeepClean`

Removes `data` and `static` folders and all files within.
`python run_luigi.py --flow clean`

2) `StartLogging`

Start logging mechanism of pipeline

3) `QueryTwitterTrends`

For each city metro location in `run_luigi.py`, write to json with trend data.

4) `StoreTrendsData`

For each json saved by `QueryTwitterTrends` write data to mongo

5) `StoreTrimTrendsData`

Query mongo for all trends in current run, and generate a unique list of trends for all metro regions

6) `StoreImageTweets`

Query Twitter via tweepy and save only tweets with images to mongo

7) `SaveImage`

Saves images from filtered trends data.

8) `CropImage`

Cropping images based based on a cv2 KeyPoints heuristic

9) `ParseImageTweets`

Parse out images in order to host on backend via Flask

10) `ImageOverlay`

Overlay cropped images onto background shirt image along with text outlining the trend and date

11) `GenerateData`

Using data stored in mongo, develop a set of data in order to post shirts to Shopify

12) `PostShopify`

From the data generated in `GenerateData` and the image shirt produced in `ImageOverlay` post a product to Shopify

13) `OutputTwitterTasks`

Dependency Graph
![Screen Shot](https://imgur.com/Ps8DuNJ.png)

14) `OutputImageTasks`

Dependency Graph
![Screen Shot](https://imgur.com/J9cwsnk.png)


### References

1) [Luigi Basic Working Example](https://marcobonzanini.com/2015/10/24/building-data-pipelines-with-python-and-luigi/)

2) [Luigi Multiple Inputs and Multiple Outputs - Ex. 1](https://bionics.it/posts/luigi-tutorial)

3) [Luigi Multiple Inputs and Multiple Outputs - Ex. 2](http://rjbaxley.com/posts/2016/03/13/parallel_jobs_in_luigi.html)

4) [Gmail API](https://developers.google.com/gmail/api/guides/sending)
