import math
import ipaddress
from urllib.parse import urlparse

def is_ip_address(url):
    domain = urlparse(url).netloc
    if not domain: domain = urlparse('http://'+url).netloc
    domain = domain.split(':')[0]
    try:
        ipaddress.ip_address(domain)
        return 1
    except ValueError:
        return 0

def calculate_entropy(text):
    if not text: return 0
    prob = [float(text.count(c)) / len(text) for c in dict.fromkeys(list(text))]
    return -sum(p * math.log(p) / math.log(2.0) for p in prob)

def extract_features(url):
    url_lower = str(url).lower()
    parsed = urlparse('http://' + url_lower if not url_lower.startswith('http') else url_lower)
    suspicious_words = ['login', 'verify', 'update', 'secure', 'bank', 'account', 'auth', 'confirm', 'service']
    suspicious_tlds = ['.xyz', '.top', '.tk', '.ml', '.ga', '.cf', '.gq', '.cc']
    return {
        'length_url': len(url_lower),
        'length_hostname': len(parsed.netloc),
        'length_path': len(parsed.path),
        'count_dot': url_lower.count('.'),
        'count_hyphen': url_lower.count('-'),
        'count_at': url_lower.count('@'),
        'count_query': url_lower.count('?'),
        'count_equal': url_lower.count('='),
        'count_underscore': url_lower.count('_'),
        'count_percent': url_lower.count('%'),
        'count_ampersand': url_lower.count('&'),
        'count_digits': sum(c.isdigit() for c in url_lower),
        'has_ip': is_ip_address(url_lower),
        'has_suspicious_word': sum(1 for w in suspicious_words if w in url_lower),
        'has_suspicious_tld': sum(1 for tld in suspicious_tlds if url_lower.endswith(tld) or tld + '/' in url_lower),
        'entropy': calculate_entropy(url_lower)
    }
