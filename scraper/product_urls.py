import click
import time
import json
import os
from utils.browser_config import get_browser_context
from utils.page_handler import setup_page_handlers
from utils.captcha_monitor import with_captcha_check, monitor_for_captcha, handle_captcha_interaction, CaptchaDetected
from utils.popup_handler import handle_popups

@with_captcha_check
def navigate_to_page(page, url, delay=3):
    """Navigate to a URL with captcha checking"""
    page.goto(url)
    time.sleep(delay)

@with_captcha_check
def click_next_page(page):
    try:
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(2)
        
        page.wait_for_selector('.sui-pagination__next')
        page.click('.sui-pagination__next')
        time.sleep(3)
        
        current_url = page.url
        return "page=" in current_url
        
    except Exception as e:
        click.secho(f"\nError navigating to next page: {str(e)}", fg="yellow")
        return False

@with_captcha_check
def scrape_category_page(page, current_domain):
    """Scrape a single category page for product URLs"""
    product_urls = []
    
    try:
        container = page.locator('.product-list-v2__container')
        title_elements = container.locator('.goods-title-link').all()
        
        for element in title_elements:
            if href := element.get_attribute('href'):
                href = href.lstrip('/')
                product_urls.append(current_domain + href)
                
        return product_urls
    except Exception as e:
        click.secho(f"\nError scraping page: {str(e)}", fg="yellow")
        return []

def collect_product_urls():
    click.clear()
    click.secho("Starting URL collection process...", fg="green")
    
    initial_url = "https://shein.com"
    category_url = click.prompt("Please enter the category URL", type=str)
    
    os.makedirs('output', exist_ok=True)
    
    playwright, browser, context = get_browser_context()
    try:
        page = context.new_page()
        setup_page_handlers(page)
        
        # Initial navigation
        navigate_to_page(page, initial_url)
        handle_popups(page)
        navigate_to_page(page, category_url)
        page.mouse.wheel(0, 3000)
        time.sleep(1)
        
        current_domain = '/'.join(page.url.split('/')[:3]) + '/'
        
        # Get total pages
        total_pages_element = page.locator('.sui-pagination__total').first
        total_text = total_pages_element.text_content().strip() if total_pages_element else "1"
        total_pages = int(''.join(filter(str.isdigit, total_text)))
        
        max_pages = click.prompt(
            f"Found {total_pages} pages. How many do you want to scrape?",
            type=int, default=1
        )
        total_pages = min(max_pages, total_pages)
        
        all_product_urls = []
        retry_count = 0
        max_retries = 3
        
        with click.progressbar(range(1, total_pages + 1), label='Scraping pages') as page_numbers:
            for page_num in page_numbers:
                print(f"\nScraping page {page_num} of {total_pages}...")
                try:
                    # Scrape URLs from current page
                    page_urls = scrape_category_page(page, current_domain)
                    if page_urls:
                        all_product_urls.extend(page_urls)
                        click.echo(f"\nCollected {len(page_urls)} URLs from page {page_num}")
                        retry_count = 0
                    else:
                        retry_count += 1
                        if retry_count >= max_retries:
                            click.secho("\nToo many failed attempts. Stopping scraper.", fg="red")
                            break
                    
                    # Navigate to next page if not on last page
                    if page_num < total_pages:
                        if not click_next_page(page):
                            click.secho("\nFailed to navigate to next page. Stopping scraper.", fg="red")
                            break
                        
                except CaptchaDetected:
                    # Captcha was detected but not resolved
                    click.secho("\nStopping due to unresolved captcha.", fg="red")
                    break
                    
                except Exception as e:
                    click.secho(f"\nUnexpected error on page {page_num}: {str(e)}", fg="red")
                    retry_count += 1
                    if retry_count >= max_retries:
                        click.secho("\nToo many errors. Stopping scraper.", fg="red")
                        break
        
        # Save results
        if all_product_urls:
            output_data = {
                'category_url': category_url,
                'total_pages_scraped': page_num,
                'product_count': len(all_product_urls),
                'urls': all_product_urls
            }
            
            output_file = f"output/product_urls_{int(time.time())}.json"
            with open(output_file, 'w') as f:
                json.dump(output_data, f, indent=2)
                    
            click.secho(f"\nCollected {len(all_product_urls)} product URLs", fg="green")
            click.secho(f"Results saved to {output_file}", fg="green")
        else:
            click.secho("\nNo URLs were collected!", fg="red")
            
    except Exception as e:
        click.secho(f"\nCritical error: {str(e)}", fg="red")
        
    finally:
        context.close()
        browser.close()
        playwright.stop()
    
    click.pause()