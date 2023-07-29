from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from lxml import etree
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
from pymongo import MongoClient
from datetime import datetime
import json
import time
import os

from functions.getProxy import *
from functions.getUserAgent import *

#proxy = getProxy()

debug = False
RETRIES = 3
mongo_host = os.environ.get('MONGO_HOST', 'localhost')
client = MongoClient(f'mongodb://{mongo_host}:27017/')
db = client['shein']
url_collection = db['product_urls']
product_collection = db['products']
product_reviews_collection = db['product_reviews']

# Setup Index
try:
    product_collection.create_index('title', text_index=True)
    product_collection.create_index('url', unique=True)
    product_collection.create_index('product_id', unique=True)
except Exception as e:
    print('Index already exists')

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
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
options.binary_location = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
chrome_drvier_binary = '/opt/homebrew/bin/chromedriver'
driver = webdriver.Chrome(service=Service(chrome_drvier_binary), options=options)

pending_urls = url_collection.find({"status": "pending"}).sort("timestamp", 1)

for url in pending_urls:
    url = url['url']
    print('Processing ' + url)

    retries = 0
    while retries < RETRIES:
        try:
            url_collection.update_one({'url': url}, {'$set': {'status': 'processing'}})
            driver.get(url)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[2]/div/div/div[1]/div/div/div[2]/div/i')))
            break
        except Exception as e:
            print('Error: ' + str(e))
            retries += 1
            print(f'Retrying ({retries} of {RETRIES})')

    if retries == RETRIES:
        print('Giving up on ' + url)
        url_collection.update_one({'url': url}, {'$set': {'status': 'failed'}})
        continue
    
    try:
        try: # Close the popup
            button_popup = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div/div[1]/div/div/div[2]/div/i').click()
            driver.implicitly_wait(10)
            ActionChains(driver).move_to_element(button_popup).click(button_popup).perform()
        except Exception as e:
            pass
        try: # Accept cookies
            button_cookies = driver.find_element(By.ID, 'onetrust-accept-btn-handler').click()
            driver.implicitly_wait(10)
            ActionChains(driver).move_to_element(button_cookies).click(button_cookies).perform()
        except Exception as e:
            pass

        single_product_data = []
        product_id = driver.find_element(By.CLASS_NAME, 'product-intro__head-sku').text.replace('SKU: ', '')
        title = driver.find_element(By.CLASS_NAME, 'product-intro__head-name').text

        product_data = { 'product_id': product_id, 'title': title, 'url': url, 'last_update': datetime.now(), 'timestamp': datetime.now() }
        #single_product_data.append(product_data)
        product_collection.insert_one(product_data)

        try:
            image_count = driver.find_element(By.CLASS_NAME, 'j-expose__review-image-tab-target').text
            image_count = re.sub("\D", "", image_count)
            image_count = int(image_count)
        except Exception as e:
            image_count = 0

        print(f'Found {image_count} reviews with images')
        if image_count > 0:
            review_data = []
            driver.find_element(By.CLASS_NAME, 'j-expose__review-image-tab-target').click() # Reviews with Pictures
            image_pages = int(image_count / 3) + 1 # 3 images per page
            for i in range(1, image_pages + 1): # Loop through all image pages
                print(f'Processing image page {i} of {image_pages}')  # Progress update

                WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'common-reviews__list-item')))

                page_reviews = driver.find_elements(By.CLASS_NAME, 'common-reviews__list-item')

                review_data = []
                for review in page_reviews:
                    time.sleep(5)
                    review_info = {}

                    try:
                        review_info['review_id'] = review.get_attribute('data-comment-id')
                    except Exception as e:
                        review_info['review_id'] = '0'

                    try:
                        images = review.find_elements(By.CLASS_NAME, 'j-review-img')
                        image_array = []

                        for image in images:
                            try:
                                image_url = image.get_attribute('src')
                                final_url = image_url.replace('_thumbnail_x460', '')
                                image_array.append('https:' + final_url)
                            except Exception as e:
                                pass

                        review_info['images'] = image_array
                    except Exception as e:
                        review_info['images'] = []

                    review_info['product_id'] = product_id
                    review_info['timestamp'] = datetime.now()

                    review_data.append(review_info)

                product_reviews_collection.insert_many(review_data)

                if i < image_pages:
                    next_page_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'sui-pagination__next')))
                    next_page_button.click()

                time.sleep(2)


    except Exception as e:
        print('Error: ' + str(e))
        url_collection.update_one({'url': url}, {'$set': {'status': 'failed'}})
        continue
    
    


driver.quit()
client.close()