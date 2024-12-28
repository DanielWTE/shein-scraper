def validate_url(url):
    if not url.startswith('http'):
        return False
    return True