from pymongo import MongoClient
from datetime import datetime
import json
import time
import math
import requests
import os
import time
import concurrent.futures

from functions.getProxy import *
from functions.getUserAgent import *

#proxy = getProxy()

mongo_host = os.environ.get('MONGO_HOST', 'localhost')
client = MongoClient(f'mongodb://{mongo_host}:27017/')
db = client['shein']
products_collection = db['products']

max_concurrent_downloads = 1
image_dir = "images/products/"
if not os.path.exists(image_dir):
    os.makedirs(image_dir)

def download_image(url, download_path):
    print(f"Starting download for {url}")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(download_path, 'wb') as fd:
            for chunk in response.iter_content(chunk_size=8192):
                fd.write(chunk)
        print(f"Finished download for {url}")
        return url
    except (requests.RequestException, IOError) as e:
        print(f"Error downloading {url}: {e}")
        return None

already_downloaded = []
futures = []

products = products_collection.find({}).sort('timestamp', 1)

with concurrent.futures.ThreadPoolExecutor(max_workers=max_concurrent_downloads) as executor:
    for product in products:
        if product['images'] != []:
            for images in product['images']:
                image_url = images[1]
                if image_url not in already_downloaded:
                    print(f"Preparing to download {image_url}")
                    try:
                        response = requests.get(image_url)
                        response.raise_for_status()
                        print(f"Access to {image_url} is not blocked")
                    except (requests.RequestException, IOError) as e:
                        print(f"Access to {image_url} is blocked: {e}")
                        continue

                    download_path = os.path.join(image_dir, image_url.split("/")[-1])
                    futures.append(executor.submit(download_image, image_url, download_path))
                    already_downloaded.append(image_url)
                    time.sleep(0.1)

    for future in concurrent.futures.as_completed(futures):
        url = future.result()
        if url is not None:
            print(f"Downloaded {url}")
        else:
            print("Error in download")

client.close()