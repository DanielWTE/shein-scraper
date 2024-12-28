from playwright.sync_api import Page, TimeoutError

def handle_challenge(page: Page):
    try:
        challenge_frame = page.frame_locator('iframe[title="geetest"]')
        if challenge_frame:
            # handle captcha
            raise Exception("Captcha encountered")
    except TimeoutError:
        pass
    
def setup_page_handlers(page: Page):
    page.on("request", lambda request: print(f">> {request.method} {request.url} Headers: {request.headers} Post Data: {request.post_data}") if "risk" in request.url else None)
    page.on("response", lambda response: print(f"<< {response.status} {response.url} Headers: {response.headers} Payload: {response.text()}") if "risk" in response.url else None)
    
    page.set_extra_http_headers({
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "accept-language": "en-US,en;q=0.9",
        "sec-ch-ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        "sec-ch-ua-mobile": "?0",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1"
    })
    
    cookies = [
        {"name": "sessionID_shein", "value": "", "domain": ".shein.com", "path": "/"},
    ]
    page.context.add_cookies(cookies)
