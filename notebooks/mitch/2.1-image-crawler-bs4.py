import requests
import shutil
import os
from bs4 import BeautifulSoup

def save_images(dest, img_urls):
    if not os.path.exists(dest):
        os.makedirs(dest)
    for url in img_urls:
        img_data = requests.get(url).content
        filename = url.split('/')[-1]
        with open('{}/{}'.format(dest, filename), 'wb') as handler:
            handler.write(img_data)

def get_images_links(tweet):

    d = requests.get(tweet).text
    soup = BeautifulSoup(d, 'html.parser')

    img_tags = soup.find_all('img')

    imgs_urls = []
    for img in img_tags:
        try:
            if img['src'].startswith("http"):
                imgs_urls.append(img['src'])
        except KeyError:
            pass

    return imgs_urls


def refine_image_list(img_urls):

    filenames = [url.split('/')[-1] for url in img_urls]
    clean_files = [file for file in filenames if 'bigger' not in file
                                    and 'normal' not in file
                                    and '_' not in file
                                    and len(file) > 10]
    ctnr = []
    for url in img_urls:
        for fn in clean_files:
            if fn in url:
                ctnr.append(url)

    return ctnr # THERE HAS TO BE A ONE LINE SOLUTION HERE

urls = get_images_links('https://twitter.com/pp8010/status/1116907934544535552/') # NOT WORKING FOR T.CO links.
urls = refine_image_list(urls)

destination = 'images/open_cv_1'
save_images(destination, urls)

