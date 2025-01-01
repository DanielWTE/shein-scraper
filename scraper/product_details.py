import click
import time
import json
import os
import glob
from typing import List, Dict
from utils.browser_config import get_browser_context
from utils.page_handler import setup_page_handlers
from utils.validator import validate_url
from utils.captcha_monitor import with_captcha_check, monitor_for_captcha, handle_captcha_interaction, CaptchaDetected

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
    base_url = image_url.split('_thumbnail_')[0]
    if base_url.startswith('//'):
        base_url = 'https:' + base_url
    if not any(base_url.endswith(ext) for ext in ('.jpg', '.png')):
        base_url += '.jpg'
    return base_url

@with_captcha_check
def navigate_to_product(page, url: str, delay: int = 2):
    """Navigate to a product page with captcha checking"""
    page.goto(url)
    time.sleep(delay)

@with_captcha_check
def scrape_product_details(page, url: str) -> Dict:
    """Scrape details for a single product."""
    retry_count = 0
    max_retries = 3
    
    while retry_count < max_retries:
        try:
            # Navigate to the product page
            navigate_to_product(page, url)
            
            # Wait for main elements with timeout
            page.wait_for_selector('.product-intro__head-sku-text, .product-intro__head-name', 
                                 timeout=10000, state='visible')

            # Get SKU
            sku_element = page.locator('.product-intro__head-sku-text').first
            sku = sku_element.text_content().strip().replace('SKU:', '').strip() if sku_element else None

            # Get Title
            title_element = page.locator('.product-intro__head-name').first
            title = title_element.text_content().strip() if title_element else None

            # Get Images
            images = []
            try:
                page.wait_for_selector('.crop-image-container', timeout=5000)
                image_elements = page.locator('.crop-image-container').all()
                
                for container in image_elements:
                    if src := container.get_attribute('data-before-crop-src'):
                        full_image_url = process_image_url(src)
                        if full_image_url not in images:
                            images.append(full_image_url)
            except Exception as e:
                click.secho(f"Warning: Error collecting images: {str(e)}", fg="yellow")

            # Verify we got at least some basic data
            if not (sku or title):
                raise Exception("Failed to extract basic product information")

            return {
                'url': url,
                'sku': sku,
                'title': title,
                'images': images,
                'scraped_at': int(time.time())
            }
            
        except CaptchaDetected as e:
            # Don't retry on captcha failures
            raise
            
        except Exception as e:
            retry_count += 1
            if retry_count >= max_retries:
                raise Exception(f"Failed after {max_retries} attempts: {str(e)}")
            click.secho(f"Retry {retry_count}/{max_retries} for {url}: {str(e)}", fg="yellow")
            time.sleep(2 * retry_count)  # Exponential backoff

def extract_product_details():
    click.clear()
    click.secho("Starting product details extraction process...", fg="green")
    
    initial_url = "https://shein.com"
    
    mode = click.prompt(
        "Choose scraping mode:\n1. Single product URL\n2. Batch from latest URLs file\nChoose 1 or 2",
        type=click.Choice(['1', '2']),
        show_choices=False
    )
    
    urls_to_scrape = []
    
    if mode == '1':
        url = click.prompt("Please enter the product URL", type=str)
        if not validate_url(url):
            click.secho("Invalid URL provided!", fg="red")
            click.pause()
            return
        urls_to_scrape = [url]
    else:
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

    playwright, browser, context = get_browser_context()
    products_data = []
    failed_urls = []
    
    try:
        page = context.new_page()
        setup_page_handlers(page)
        
        # Initial navigation
        navigate_to_product(page, initial_url)
        
        with click.progressbar(urls_to_scrape, label='Scraping products') as urls:
            for url in urls:
                try:
                    product_data = scrape_product_details(page, url)
                    if product_data:
                        products_data.append(product_data)
                        time.sleep(2)  # Base delay between requests
                except CaptchaDetected as e:
                    click.secho(f"\nStopping due to unresolved captcha at {url}", fg="red")
                    failed_urls.append({"url": url, "error": "Captcha detection failed"})
                    break
                except Exception as e:
                    click.secho(f"\nError scraping {url}: {str(e)}", fg="red")
                    failed_urls.append({"url": url, "error": str(e)})
                    continue

        # Save results
        if products_data:
            output_data = {
                'total_products': len(products_data),
                'scrape_timestamp': int(time.time()),
                'products': products_data,
                'failed_urls': failed_urls
            }
            
            output_file = f"output/product_details_{int(time.time())}.json"
            os.makedirs('output', exist_ok=True)
            
            with open(output_file, 'w') as f:
                json.dump(output_data, f, indent=2)
                
            click.secho(f"\nSuccessfully scraped {len(products_data)} products", fg="green")
            click.secho(f"Failed to scrape {len(failed_urls)} URLs", fg="yellow" if failed_urls else "green")
            click.secho(f"Results saved to {output_file}", fg="green")
        else:
            click.secho("\nNo products were successfully scraped!", fg="red")
            
    except Exception as e:
        click.secho(f"\nCritical error: {str(e)}", fg="red")
        
    finally:
        context.close()
        browser.close()
        playwright.stop()
    
    click.pause()