from bs4 import BeautifulSoup
from selenium import webdriver
from config import urls_dataset_save_path
import pyarrow.parquet as pq
import pandas as pd
import random
from time import sleep
from datetime import datetime


def profile_crawler(url, driver):
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    main_bar = soup.find('div', {"id": "mainbar-full"})
    header_details = main_bar.findChildren(recursive=False)[0].find('div', {"class":"flex--item"})
    user_name = header_details.findChildren(recursive=False)[0].text.strip()
    try:
        work = header_details.findChildren('div', recursive=False)[1].text.strip()
    except:
        work = ''
    uls = header_details.findChildren('ul')

    details = {}

    for li in uls:
        a_tags = li.findChildren('a')
        for a in a_tags:
            key = a.text
            value = a.get("href")
            details[key] = value

    tags = []
    main_content = soup.find("div", {"id": "main-content"})
    top_tags = main_content.find("div", {"id":"top-tags"}).findChildren(recursive=False)[1]
    for a in top_tags.findAll('a')[1:]:
        tags.append(a.text)

    about = main_content.find('div', recursive=False).findAll('div', recursive=False)[1].find('div', recursive=False).findAll('p')
    about_text = "\n".join([p.text for p in about])

    data = {
        "user_name": user_name,
        "headline": about_text,
        "work": work,
        "details" : details,
        "tags": tags,
    }

    return data


if __name__ == "__main__":
    dataset = pq.ParquetDataset(urls_dataset_save_path, filters=[('site','=','stackoverflow')])
    df = dataset.read().to_pandas()

    driver = webdriver.Chrome()
    urls = df['url'].to_list()

    data = []
    for u in urls:
        print(u)
        d = profile_crawler(u, driver)
        today = datetime.today().date()
        today_string = today.strftime('%Y-%m-%d')
        d['date_added'] = today_string
        print(d)
        
        data.append(d)
        sleep(random.randint(6,10))

    result_df = pd.DataFrame(data)
    result_df.to_parquet('data/profiles/stackoverflow', partition_cols=['date_added'])

    driver.quit()

    