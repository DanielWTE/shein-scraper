from playwright.sync_api import sync_playwright
from random import choice, randint
from .user_agents import USER_AGENTS
import random
import time

def get_hardware_concurrency():
    """Get a realistic number of CPU cores."""
    return choice([2, 4, 6, 8, 12, 16])

def get_device_memory():
    """Get a realistic amount of device memory in GB."""
    return choice([4, 8, 16, 32])

def get_platform():
    """Get consistent platform info based on user agent."""
    platforms = {
        'Windows': {
            'platform': 'Win32',
            'oscpu': 'Windows NT 10.0',
            'vendor': 'Google Inc.',
            'renderer': 'ANGLE (Intel, Intel(R) UHD Graphics Direct3D11 vs_5_0 ps_5_0, D3D11)',
            'languages': ['de-DE', 'de', 'en-US', 'en']
        },
        'Macintosh': {
            'platform': 'MacIntel',
            'oscpu': 'Intel Mac OS X 10_15_7',
            'vendor': 'Apple Computer, Inc.',
            'renderer': 'Apple GPU',
            'languages': ['de-DE', 'de', 'en-US', 'en']
        }
    }
    return platforms['Windows'] if 'Windows' in choice(USER_AGENTS) else platforms['Macintosh']

def get_browser_context():
    """Get a configured browser context with realistic fingerprinting."""
    
    platform_info = get_platform()
    
    launch_options = {
        'headless': True,
        'args': [
            '--disable-application-cache',
            '--disable-gpu',
            '--disable-dev-shm-usage',
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-extensions',
            '--disable-sync',
            '--metrics-recording-only',
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows',
            '--disable-popup-blocking',
            '--disable-notifications',
            '--disable-translate',
            '--disable-web-security',
            f'--lang={platform_info["languages"][0]}',
            '--disable-blink-features=AutomationControlled',
            f'--hardware-concurrency={get_hardware_concurrency()}',
            f'--device-memory={get_device_memory()}'
        ]
    }
    
    p = sync_playwright().start()
    browser = p.chromium.launch(**launch_options)
    
    viewport_sizes = [
        {'width': 1920, 'height': 1080},
        {'width': 1280, 'height': 800},
        {'width': 1440, 'height': 900},
        {'width': 1366, 'height': 768},
        {'width': 1536, 'height': 864},
        {'width': 1600, 'height': 900},
        {'width': 1680, 'height': 1050},
        {'width': 1920, 'height': 1200},
    ]
    
    chosen_viewport = choice(viewport_sizes)
    screen = {
        'width': chosen_viewport['width'],
        'height': chosen_viewport['height'],
        'device_scale_factor': choice([1, 1.25, 1.5, 2])
    }
    
    timezones = {
        'de-DE': ['Europe/Berlin', 'Europe/Vienna', 'Europe/Zurich'],
        'en-GB': ['Europe/London', 'Europe/Dublin'],
    }
    
    chosen_locale = platform_info['languages'][0]
    chosen_timezone = choice(timezones.get(chosen_locale, ['Europe/Berlin']))
    
    context = browser.new_context(
        user_agent=choice(USER_AGENTS),
        viewport=chosen_viewport,
        screen=screen,
        locale=chosen_locale,
        timezone_id=chosen_timezone,
        geolocation={'latitude': 48.1351 + random.uniform(-2, 2),
                    'longitude': 11.5820 + random.uniform(-2, 2)},
        color_scheme='light',
        permissions=['geolocation', 'notifications'],
        device_scale_factor=screen['device_scale_factor'],
        is_mobile=False,
        has_touch=False,
        java_script_enabled=True,
        bypass_csp=True,
        ignore_https_errors=True,
    )
    
    context.add_init_script("""
        Object.defineProperty(navigator, 'platform', { get: () => '""" + platform_info['platform'] + """' });
        Object.defineProperty(navigator, 'vendor', { get: () => '""" + platform_info['vendor'] + """' });
        Object.defineProperty(navigator.connection, 'rtt', { get: () => """ + str(randint(50, 250)) + """ });
        Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => """ + str(get_hardware_concurrency()) + """ });
        Object.defineProperty(navigator, 'deviceMemory', { get: () => """ + str(get_device_memory()) + """ });
        Object.defineProperty(navigator, 'languages', { get: () => """ + str(platform_info['languages']) + """ });
        Object.defineProperty(window.screen, 'colorDepth', { get: () => 24 });
        Object.defineProperty(window.screen, 'pixelDepth', { get: () => 24 });
        Object.defineProperty(window, 'chrome', { get: () => true });
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        
        // WebGL fingerprinting
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {
            if (parameter === 37445) {
                return '""" + platform_info['renderer'] + """';
            }
            return getParameter.apply(this, arguments);
        };
    """)
    
    context.add_cookies([
        {
            'name': 'user_session', 
            'value': f'session_{randint(1000000, 9999999)}',
            'domain': '.shein.com',
            'path': '/'
        },
        {
            'name': 'first_visit',
            'value': str(int(time.time() - randint(86400, 864000))),
            'domain': '.shein.com',
            'path': '/'
        }
    ])
    
    return p, browser, context
