from playwright.sync_api import Page, TimeoutError
import os
from datetime import datetime
    
def setup_page_handlers(page: Page):
    try:
        os.makedirs("logs", exist_ok=True)
        log_file = "logs/risk_requests.log"
        
        def log_to_file(message):
            try:
                with open(log_file, "a") as f:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    f.write(f"[{timestamp}] {message}\n")
            except Exception as e:
                print(f"Error writing to log file: {e}")
        
        def handle_response(response):
            if "risk" in response.url:
                try:
                    log_message = f"<< {response.status} {response.url} Headers: {response.headers}"
                    
                    if response.ok:
                        try:
                            body = response.text()
                            log_message += f" Payload: {body}"
                        except:
                            log_message += " Payload: <unavailable>"
                    
                    log_to_file(log_message)
                except Exception as e:
                    log_to_file(f"Error logging response: {e}")
        
        page.on("request", lambda request: log_to_file(f">> {request.method} {request.url} Headers: {request.headers} Post Data: {request.post_data}") if "risk" in request.url else None)
        page.on("response", handle_response)
        
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
    except Exception as e:
        print(f"Logging error", e)