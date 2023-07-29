# Shein Scraper
This project is a scraper designed to fetch product URLs and details including reviews and associated images from Shein, a popular online retailer. It's built with Python, leveraging Selenium for web scraping and MongoDB for data storage.

## Project Structure
The project includes the following files:

* **shein_categories.txt**: Contains a list of category URLs.
* **requirements.txt**: The dependencies required for this project.
* **get_products.py**: Script to get product URLs from categories.
* **get_product_details.py**: Script to get product details and reviews with images.

The **get_products.py** and **get_product_details.py** scripts have been set up with sample paths and configurations, which you will need to adjust to suit your local environment.

## Pre-requisites
Before you run the scripts, make sure:

* MongoDB is installed and running on your machine.
* Chrome browser is installed on your machine.
* The required Python packages are installed. You can install these using the **requirements.txt** file with 

```bash
pip install -r requirements.txt
# or
pip3 install -r requirements.txt.
```

**Important:** You must adjust the path of Chrome binary location and the Chrome driver in the **options.binary_location** and **chrome_drvier_binary** variables to reflect the correct paths on your machine.

## How to use
1. Update **shein_categories.txt** with the category URLs from which you want to scrape product URLs. (I've included a few sample URLs to get you started.)

2. Run the **get_products.py** script to fetch the product URLs.
```bash
python get_products.py
# or
python3 get_products.py
```

3. Run the **get_product_details.py** script to fetch the product details and reviews along with image URLs.
```bash
python get_product_details.py
# or
python3 get_product_details.py
```

Please note that in order to run the scripts, you might need to use **python3** instead of **python** depending on your Python installation.

Please also make sure that your MongoDB instance is running on the default port (27017) on localhost, otherwise you need to update the MongoDB connection string in both scripts.

The scripts store the data in MongoDB. The database and collection names are hard-coded in the scripts. If you wish to change them, you will have to do so directly in the scripts.