import time
from playwright.sync_api import Page, TimeoutError

def handle_popups(page: Page):
    def try_click(selector):
        selectors = [
            f"#{selector}",                                    # ID
            f".{selector}",                                    # Class
            f"[data-sheinprivacysign5464114245='{selector}']", # Data attribute
            f"text={selector}",                               # Text content
            f"[aria-label='{selector}']",                     # Aria label
            f"div:has-text('{selector}')",                    # Contains text
            selector                                          # Raw selector
        ]
        
        for s in selectors:
            try:
                element = page.wait_for_selector(s, timeout=100)
                if element and element.is_visible():
                    element.click()
                    return True
            except TimeoutError:
                continue
            except Exception:
                continue
        return False

    popups = [
        'sign',              # data attribute value
        'Lehnen Sie alles ab', # text content
        'schließen',        # aria-label
        'quickg-outside',  # class
    ]
    
    for popup in popups:
        print(f"Checking for popup {popup}")
        if try_click(popup):
            print(f"Clicked on {popup}")
        else:
            print(f"Popup {popup} not found")