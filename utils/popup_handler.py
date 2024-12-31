import time
from playwright.sync_api import Page, TimeoutError

def handle_popups(page: Page):
    def try_click(selector_info):
        selector, timeout = selector_info
        try:
            element = page.wait_for_selector(selector, timeout=timeout)
            if element and element.is_visible():
                element.click()
                return True
        except (TimeoutError, Exception):
            return False
        return False

    popup_selectors = [
        ('[data-sheinprivacysign5464114245="sign"]', 200),
        ('text="Lehnen Sie alles ab"', 200),
        ('[aria-label="schließen"]', 200),
        ('.dialog-header-v2__close-btn', 200),
        ('.coupon-dialog__coupon-content .dialog-header-v2__close-btn', 200),
        ('svg.btn-new', 200),
        ('[data-v-7833d02c].dialog-header-v2__close-btn', 200),
    ]
    
    for selector, timeout in popup_selectors:
        if try_click((selector, timeout)):
            time.sleep(0.5)
            
    try:
        if page.locator('.coupon-dialog__coupon-content').is_visible():
            page.keyboard.press('Escape')
    except:
        pass