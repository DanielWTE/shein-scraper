import click
from utils.browser_config import get_browser_context

def collect_reviews():
    click.clear()
    click.secho("Starting review collection process...", fg="green")
    
    playwright, browser, context = get_browser_context()
    try:
        page = context.new_page()
        # implementation
        
    finally:
        context.close()
        browser.close()
        playwright.stop()
    
    click.pause()