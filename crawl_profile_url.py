import subprocess
from config import urls_dataset_save_path

site_keywords = [
    'site:linkedin.com/in/',
    'site:stackoverflow.com/users/ AND "@gmail.com" AND "about"',
    'site:dev.to/ AND "Currently learning" AND "Skills/Languages" AND "@gmail.com"',
]

sites = [
    "linkedin",
    "stackoverflow",
    "dev.to"
]

positions_or_skill = [
    # 'data engineer',
    # 'software engineer',
    # 'machien learning engineer',
    "python",
    "java",
    "javascript"
]

keywords_sites = []
for s, k in zip(sites, site_keywords):
    for p in positions_or_skill:
        k = k + f' AND "{p}"'
        keywords_sites.append((k, s))

for i in keywords_sites:
    print(i)

for search_key in keywords_sites:
    subprocess.run(['python', 'urls_crawler.py', search_key[0], search_key[1], urls_dataset_save_path]) 