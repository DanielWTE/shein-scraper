from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from lxml import etree
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
from pymongo import MongoClient
from datetime import datetime
import json
import os

from functions.getProxy import *
from functions.getUserAgent import *

#proxy = getProxy()
domain = 'shein.com' # For checking if the URL is from the same domain
debug = False # Set to True to limit to 1 page
db_mode = True # True = MongoDB, False = JSON

with open('shein_categories.txt', 'r') as file: # Read URLs from file
    urls = file.readlines()

if db_mode:
    mongo_host = os.environ.get('MONGO_HOST', 'localhost')
    client = MongoClient(f'mongodb://{mongo_host}:27017/')
    db = client['shein']
    collection = db['product_urls']

    # Setup Index
    try:
        collection.create_index('url', unique=True)
    except Exception as e:
        print('Index already exists')

blacklistedWords = [
    'javascript:',
    'mailto:',
    'tel:',
    'facebook.com',
    'twitter.com',
    'instagram.com',
    'youtube.com',
    'pinterest.com',
    'tiktok.com',
    'Copyright',
    'copyright',
    'Privacy',
    'privacy',
    'Terms',
    'terms',
    'Imprint',
    'imprint',
    'bonus',
    'campaign',
    'campaigns',
    'sale',
    'refund',
    'track',
    'How-to',
    'how-to',
    'shein.com/women',
    'shein.com/other',
    'shein.com/Return-Policy',
    'shein.com/men',
    'shein.com/plussize',
    'shein.com/curve-plus-size',
    'promotion',
    'shein.com/home',
    'shein.com/cart',
    'contact',
    'About',
    'SUPPLY-CHAIN-TRANSPARENCY',
    'prime',
    'shein.com/kids',
    'shein.com/beauty',
    'shein.com/flashsale',
    'Shipping-Info',
    'coupon-a',
    '/user/auth/login',
    'daily-new',
    'New-in-Trends',
    'shein.com/style',
    'New-in-Trends',
    'shein.com/member-image-list',
]

# Function to check if any word from a list is included in a string
def included_in_string(string, word_list):
    for word in word_list:
        if word in string:
            return True
    return False

#prox_options = {
#    'proxy': {
#        'http': proxy
#    }
#}

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--user-agent=' + GET_UA())
options.add_argument('--incognito')
options.binary_location = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
chrome_drvier_binary = '/opt/homebrew/bin/chromedriver'
driver = webdriver.Chrome(service=Service(chrome_drvier_binary), options=options)

for url in urls:
    url = url.strip()
    print('Processing ' + url)

    driver.get(url)

    try:
        pagination_text = driver.find_element(By.CLASS_NAME,'sui-pagination__total').text
        pagination_number = re.sub("\D", "", pagination_text)
        max_pages = int(pagination_number)
        if debug:
            max_pages = min(1, max_pages)  # Limit to 1 page in debug mode
        print(f'Found {max_pages} pages')
    except Exception as e:
        print('Error getting pagination: ' + str(e))
        max_pages = 1  # If no pagination, assume 1 page of product
        pass

    # Initialize array for product urls
    product_urls = []

    for i in range(1, max_pages + 1):
        try:
            print(f'Processing page {i} of {max_pages}')  # Progress update
            driver.get(url + '?page=' + str(i))

            product_elements = driver.find_elements(By.CLASS_NAME, 'product-list__item')
            for product in product_elements:
                href = product.find_element(By.TAG_NAME, 'a').get_attribute('href')
                if not href or included_in_string(href, blacklistedWords):
                    continue
                parsed_url = urlparse(href)
                cleaned_url = parsed_url.scheme + "://" + parsed_url.netloc + parsed_url.path
                if domain in parsed_url.netloc and cleaned_url not in product_urls:
                    try:
                        if db_mode:
                            if collection.find_one({'url': cleaned_url}):
                                print('URL already exists in MongoDB')
                                continue
                            print('Adding ' + cleaned_url + ' to MongoDB')
                            collection.insert_one({'url': cleaned_url, 'status': 'pending', 'timestamp': datetime.now()})
                        else:
                            product_urls.append(cleaned_url)
                    except Exception as e:
                        print('Error adding URL to MongoDB: ' + str(e))
                        pass
        except Exception as e:
            print('Error processing page: ' + str(e))
            continue

    if not db_mode:
        print('Writing to JSON file')
        with open('product_urls.json', 'w') as outfile:
            json.dump(product_urls, outfile)

driver.quit()
if db_mode:
    client.close()