from urllib.parse import urlparse

def parse_domain(url):
    return urlparse(url).netloc
