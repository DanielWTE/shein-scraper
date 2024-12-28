import click
import time
import json
import os
from utils.browser_config import get_browser_context
from utils.popup_handler import handle_popups
from utils.captcha_handler import setup_page_handlers

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
    
        page.goto(initial_url)
        handle_popups(page)
        
        page.goto(category_url)
        page.mouse.wheel(0, 1500)
        
        current_domain = '/'.join(page.url.split('/')[:3]) + '/'
        
        total_pages_element = page.locator('.sui-pagination__total').first
        total_text = total_pages_element.text_content().strip() if total_pages_element else "1"
        total_pages = int(''.join(filter(str.isdigit, total_text)))
        
        max_pages = click.prompt(f"Found {total_pages} pages. How many do you want to scrape?",
                               type=int, default=1)
        total_pages = min(max_pages, total_pages)
            
        product_urls = []
        
        for page_num in range(1, total_pages + 1):
            time.sleep(5)
            if page_num > 1:
                page.locator('.sui-pagination__next').click()
                page.reload()
            
            container = page.locator('.product-list-v2__container')
            title_elements = container.locator('.goods-title-link').all()
            
            for element in title_elements:
                print('Processing product')
                if href := element.get_attribute('href'):
                    href = href.lstrip('/')
                    product_urls.append(current_domain + href)
            
            click.secho(f"Processed page {page_num}/{total_pages}", fg="blue")
        
        output_data = {
            'category_url': category_url,
            'total_pages_scraped': total_pages,
            'product_count': len(product_urls),
            'urls': product_urls
        }
        
        output_file = f"output/product_urls_{int(time.time())}.json"
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)
                
        click.secho(f"Collected {len(product_urls)} product URLs", fg="green")
        
    finally:
        context.close()
        browser.close()
        playwright.stop()
    
    click.pause()