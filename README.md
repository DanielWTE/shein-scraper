# Shein Scraper Tool

This project is a modular web scraping tool designed to collect product information from Shein, including product URLs, detailed product information, and reviews. It's built with Python and uses Playwright for web automation, with a focus on avoiding detection through browser fingerprinting.

## Features

* Interactive CLI menu interface
* Modular architecture for different scraping tasks
* Advanced browser fingerprinting protection
* Automatic popup and captcha handling
* Configurable scraping parameters
* JSON-based data storage

## Project Structure

The project is organized into several modules:

* **main.py**: The main entry point with CLI menu interface
* **scraper/**: Core scraping functionality
  * **product_urls.py**: Collects product URLs from category pages
  * **product_details.py**: Extracts detailed product information
  * **reviews.py**: Gathers product reviews
* **utils/**: Helper utilities
  * **browser_config.py**: Browser configuration and anti-detection measures
  * **popup_handler.py**: Handles website popups and dialogs
  * **captcha_handler.py**: Manages captcha challenges
  * **user_agents.py**: Collection of user agent strings
  * **validator.py**: URL validation utilities

## Prerequisites

Before running the scraper, ensure you have:

* Python 3.8 or higher installed
* Chrome browser installed
* Required Python packages (install using requirements.txt)

## Installation

### Local Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd shein-scraper
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

### Docker Installation

The project includes Docker support for easy deployment:

1. Make sure you have Docker and Docker Compose installed
2. Build and start the containers:
```bash
docker-compose up --build
```

This will:
* Set up the Python environment
* Mount the local directory to /app in the container
* Create a volume for MongoDB data persistence

## Usage

### Local Usage

1. Start the tool:
```bash
python main.py menu
```

### Docker Usage

When using Docker, you can run the scraper using:
```bash
docker-compose up
```

The scraper service will automatically start with the interactive menu. All output files will be available in your local `output/` directory due to volume mounting.

2. Use the interactive menu to:
   * Collect product URLs from category pages
   * Extract detailed product information
   * Gather product reviews

### Product URL Collector

Collects product URLs from a specified category page:
1. Enter the category URL when prompted
2. Specify the number of pages to scrape
3. URLs will be saved to `output/product_urls_[timestamp].json`

### Product Details Extractor

Extracts detailed product information:
1. Choose between single URL or batch mode
2. For batch mode, it will use the most recent URL collection file
3. Data will be saved to `output/product_details_[timestamp].json`

### Review Collector

⚠️ Currently not implemented.

## Output Format

All data is stored in JSON format in the `output/` directory:

### Product URLs
```json
{
    "category_url": "https://shein.com/category",
    "total_pages_scraped": 5,
    "product_count": 120,
    "urls": [...]
}
```

### Product Details
```json
{
    "total_products": 50,
    "scrape_timestamp": 1709142400,
    "products": [
        {
            "url": "https://shein.com/product",
            "sku": "sw2401234567890",
            "title": "Product Name",
            "images": [...],
            "scraped_at": 1709142400
        }
    ]
}
```

## Anti-Detection Features

The tool implements several measures to avoid detection:
* Randomized user agents
* Realistic browser fingerprinting
* Geolocation spoofing
* Cookie management
* Request header customization
* Dynamic viewport sizes
* Automated popup handling

## Known Limitations

* Review collection functionality is not yet implemented
* No proxy support yet - might get captchas when scraping large amounts of data
* Captcha handling is basic and may require manual intervention
* Some anti-bot detection systems might still detect the scraper
