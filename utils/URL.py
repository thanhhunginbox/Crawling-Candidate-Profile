from urllib.parse import urlparse
import re

def remove_subdomain(url):
    modified_url = re.sub(r"https://[a-z]+\.linkedin", "https://linkedin", url)
    return modified_url

def preprocess_linkedin_url(url):
    new_url = remove_subdomain(url)
    return new_url


def preprocess_devto_url(url):
    parser = urlparse(url)
    if parser.path.count("/") > 1:
        parts = parser.path.split("/")
        return parser.scheme + "://" + parser.netloc + "/" + parts[1]
    return url


def preprocess_url(url, site):
    if site == "linkedin":
        return preprocess_linkedin_url(url)
    if site == "dev.to":
        return preprocess_devto_url(url)
    return url


print(preprocess_linkedin_url("https://in.linkedin.com/in/ht-lm-and-python-devi-01668a293"))