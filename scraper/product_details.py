import click
import time
import json
import os
import glob
from typing import List, Dict
from utils.browser_config import get_browser_context
from utils.popup_handler import handle_popups
from utils.validator import validate_url

def get_latest_urls_file() -> str:
    """Get the most recent product_urls JSON file from output directory."""
    files = glob.glob('output/product_urls_*.json')
    if not files:
        return None
    return max(files, key=os.path.getctime)

def load_urls_from_file(file_path: str) -> List[str]:
    """Load product URLs from a JSON file."""
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data.get('urls', [])

def process_image_url(image_url: str) -> str:
    """Convert thumbnail URL to full-size image URL."""
    # Remove thumbnail size specification
    base_url = image_url.split('_thumbnail_')[0]
    # Add jpg extension if missing
    if not base_url.endswith('.jpg'):
        base_url += '.jpg'
    return base_url

def scrape_product_details(page, url: str) -> Dict:
    """Scrape details for a single product."""
    page.goto(url)
    handle_popups(page)
    time.sleep(2)  # Allow page to load fully

    # Get SKU
    sku_element = page.locator('.product-intro__head-sku-text').first
    sku = sku_element.text_content().strip().replace('SKU:', '').strip() if sku_element else None

    # Get Title
    title_element = page.locator('.product-intro__head-name').first
    title = title_element.text_content().strip() if title_element else None

    # Get Images
    image_elements = page.locator('.crop-image-container').all()
    images = []
    for container in image_elements:
        if src := container.get_attribute('data-before-crop-src'):
            full_image_url = process_image_url(src)
            if full_image_url not in images:  # Avoid duplicates
                images.append(full_image_url)

    return {
        'url': url,
        'sku': sku,
        'title': title,
        'images': images,
        'scraped_at': int(time.time())
    }

def extract_product_details():
    click.clear()
    click.secho("Starting product details extraction process...", fg="green")
    
    initial_url = "https://shein.com"
    
    # Ask user for scraping mode
    mode = click.prompt(
        "Choose scraping mode:\n1. Single product URL\n2. Batch from latest URLs file\nChoose 1 or 2",
        type=click.Choice(['1', '2']),
        show_choices=False
    )
    
    urls_to_scrape = []
    
    if mode == '1':
        # Single URL mode
        url = click.prompt("Please enter the product URL", type=str)
        if not validate_url(url):
            click.secho("Invalid URL provided!", fg="red")
            click.pause()
            return
        urls_to_scrape = [url]
    else:
        # Batch mode
        latest_file = get_latest_urls_file()
        if not latest_file:
            click.secho("No previous URL files found!", fg="red")
            click.pause()
            return
            
        urls_to_scrape = load_urls_from_file(latest_file)
        if not urls_to_scrape:
            click.secho("No URLs found in the file!", fg="red")
            click.pause()
            return
            
        max_urls = len(urls_to_scrape)
        num_urls = click.prompt(
            f"Found {max_urls} URLs. How many do you want to scrape?",
            type=int,
            default=max_urls
        )
        urls_to_scrape = urls_to_scrape[:num_urls]

    # Initialize browser
    playwright, browser, context = get_browser_context()
    products_data = []
    
    try:
        page = context.new_page()

        # First visit landing page
        click.secho("Visiting initial page...", fg="blue")
        page.goto(initial_url)
        handle_popups(page)
        time.sleep(2)  # Short delay after handling initial popups
        
        with click.progressbar(urls_to_scrape, label='Scraping products') as urls:
            for url in urls:
                try:
                    product_data = scrape_product_details(page, url)
                    products_data.append(product_data)
                    time.sleep(2)  # Delay between requests
                except Exception as e:
                    click.secho(f"\nError scraping {url}: {str(e)}", fg="red")
                    continue

        # Save results
        output_data = {
            'total_products': len(products_data),
            'scrape_timestamp': int(time.time()),
            'products': products_data
        }
        
        output_file = f"output/product_details_{int(time.time())}.json"
        os.makedirs('output', exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)
            
        click.secho(f"\nSuccessfully scraped {len(products_data)} products", fg="green")
        click.secho(f"Results saved to {output_file}", fg="green")
        
    finally:
        context.close()
        browser.close()
        playwright.stop()
    
    click.pause()
    