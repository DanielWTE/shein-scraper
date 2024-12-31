from playwright.sync_api import Page, TimeoutError
import click
import time
from functools import wraps

class CaptchaDetected(Exception):
    """Custom exception for captcha detection"""
    pass

def monitor_for_captcha(page: Page) -> bool:
    """
    Monitor for the presence of Geetest captcha elements.
    Returns True if captcha is detected, False otherwise.
    """
    try:
        captcha_selectors = [
            ".geetest_panel_box",
            ".captcha_click_wrapper",
            "[captcha-click-image]",
            ".captcha_btn_click_wrapper"
        ]
        
        for selector in captcha_selectors:
            try:
                element = page.locator(selector).first
                if element and element.is_visible(timeout=1000):
                    return True
            except Exception:
                continue
                
        return False
    except Exception:
        return False

def handle_captcha_interaction(page: Page):
    """
    Handle detected captcha by pausing execution and waiting for resolution.
    Returns True if captcha was resolved, False otherwise.
    """
    try:
        click.secho("\n⚠️ Captcha detected! Waiting for resolution...", fg="yellow", bold=True)
        
        max_wait_time = 300
        start_time = time.time()
        
        # Implement captcha resolution
        
        while time.time() - start_time < max_wait_time:
            if not monitor_for_captcha(page):
                click.secho("✓ Captcha resolved successfully!", fg="green")
                time.sleep(2)
                return True
            time.sleep(1)
            
        click.secho("❌ Captcha resolution timeout!", fg="red")
        return False
        
    except Exception as e:
        click.secho(f"Error handling captcha: {str(e)}", fg="red")
        return False

def with_captcha_check(func):
    """
    Decorator to add captcha monitoring to scraping functions
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        page = next((arg for arg in args if isinstance(arg, Page)), None)
        if page is None:
            page = kwargs.get('page')
            
        if not page:
            return func(*args, **kwargs)
            
        try:
            if monitor_for_captcha(page):
                if not handle_captcha_interaction(page):
                    raise CaptchaDetected("Failed to resolve captcha")
                    
            result = func(*args, **kwargs)
            
            if monitor_for_captcha(page):
                if not handle_captcha_interaction(page):
                    raise CaptchaDetected("Failed to resolve captcha")
                    
            return result
            
        except CaptchaDetected as e:
            click.secho(f"\nCaptcha error: {str(e)}", fg="red")
            raise
            
        except Exception as e:
            click.secho(f"\nUnexpected error: {str(e)}", fg="red")
            raise
            
    return wrapper