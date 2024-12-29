# Shein Scraper Tool

A modular web scraping tool designed to collect product information from Shein, including product URLs, detailed product information, and reviews. Built with Python and Playwright, featuring advanced anti-detection measures and easy deployment options.

## Features

- Interactive CLI menu interface
- Modular scraping architecture
- Advanced anti-detection features:
  - Dynamic browser fingerprinting
  - Automated popup handling
  - Cookie management
  - Geolocation spoofing
  - Request header customization
- Configurable scraping parameters
- Docker support for easy deployment
- JSON-based data storage

## Project Structure

```
shein-scraper/
├── scraper/
│   ├── product_urls.py     # Category page scraping
│   ├── product_details.py  # Product information scraping
│   └── reviews.py         # Review collection (WIP)
├── utils/
│   ├── browser_config.py   # Anti-detection configuration
│   ├── popup_handler.py    # Popup management
│   ├── captcha_handler.py  # Captcha handling
│   ├── user_agents.py      # User agent rotation
│   └── validator.py        # URL validation
├── docker-compose.yml      # Docker configuration
├── Dockerfile             # Container definition
├── requirements.txt       # Python dependencies
├── main.py               # CLI entry point
└── README.md             # Documentation
```

## Quick Start

### Using Docker (Recommended)

1. Prerequisites:
   - Install [Docker](https://docs.docker.com/get-docker/)

2. Clone the repository:
   ```bash
   git clone https://github.com/DanielWTE/shein-scraper.git
   cd shein-scraper
   ```

3. Create a local output directory:
   ```bash
   mkdir output
   ```

4. Build the Docker image:
   ```bash
   docker build -t shein-scraper .
   ```

5. Run the scraper in interactive mode with data persistence:
   ```bash
   docker run -it --init -v $(pwd)/output:/app/output shein-scraper
   ```

Note: The -v flag maps your local output directory to the container's output directory:
- Without volume mapping, data will be lost when the container stops
- With volume mapping, all scraped data is saved to your local ./output folder

### Local Installation

1. Prerequisites:
   - Python 3.12 or higher
   - pip (Python package manager)
   - Chrome browser

2. Clone and setup:
   ```bash
   git clone https://github.com/DanielWTE/shein-scraper.git
   cd shein-scraper
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   playwright install chromium
   ```

3. Run the scraper:
   ```bash
   python main.py menu
   ```

## Usage Guide

The tool offers three main functions through an interactive CLI menu:

### 1. Product URL Collector
- Extracts product URLs from category pages
- Input: Category URL (e.g., https://shein.com/women-dresses-c-1727.html)
- Output: JSON file with collected URLs in `output/product_urls_[timestamp].json`

### 2. Product Details Extractor
- Gathers detailed product information
- Two modes:
  - Single URL mode: Process one product
  - Batch mode: Process multiple products from a previous URL collection
- Output: JSON file with product details in `output/product_details_[timestamp].json`

### 3. Review Collector
- Currently under development

## Data Format

### Product URLs JSON Structure
```json
{
    "category_url": "https://shein.com/category",
    "total_pages_scraped": 5,
    "product_count": 120,
    "urls": [
        "https://shein.com/product1",
        "https://shein.com/product2"
    ]
}
```

### Product Details JSON Structure
```json
{
    "total_products": 50,
    "scrape_timestamp": 1709142400,
    "products": [
        {
            "url": "https://shein.com/product",
            "sku": "sw2401234567890",
            "title": "Product Name",
            "images": [
                "https://shein.com/image1.jpg",
                "https://shein.com/image2.jpg"
            ],
            "scraped_at": 1709142400
        }
    ]
}
```

## Limitations & Known Issues

- Review collection functionality is under development
- No built-in proxy support
- Basic captcha handling that may require manual intervention
- Some anti-bot detection systems might still detect the scraper
