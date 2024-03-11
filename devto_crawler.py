from selenium import webdriver
from bs4 import BeautifulSoup
import requests
from config import urls_dataset_save_path
import pandas as pd
import pyarrow.parquet as pq
from time import sleep
import random
from datetime import datetime

def profile_crawler(url):
    response = requests.get(url)
    html = response.content
    soup = BeautifulSoup(html, 'html.parser')

    header = soup.find('header', {"class": "profile-header"})

    header_detials = header.find('div', {"class": "profile-header__details"})
    user_name = header_detials.find('h1').text.strip()
    headline = header_detials.find('p').text.strip()

    meta = {}
    meta['details'] = {}
    meta["urls"] = []
    header_meta = header.find('div', {"class": "profile-header__meta"})
    for e in header_meta.findChildren(recursive=False):
        if e.name == "span":
            key = e.find('title').text.strip()
            try:
                value = e.find('span').text.strip()
            except:
                value = ''
            meta['details'][key] = value
        elif e.name == "a":
            url = e.get("href")
            meta['urls'].append(url)
    
    try:
        header_bottom = header.find('div', {"class": "profile-header__bottom"})  
        for i in header_bottom.findChildren(recursive=False):
            text = i.text.strip()
            data = text.split("\n")
            key = data[0]
            value = data[-1]
            meta['details'][key] = value
    except:
        pass


    qualification = {}
    user_info = soup.find('div', {"class": "js-user-info"})
    for i in user_info.findChildren(recursive=False)[1:-1]:
        text = i.text.strip()
        data = text.split("\n")
        key = data[0]
        value = data[-1]
        qualification[key] = value

    data = {
        "user_name": user_name,
        "headline": headline,
        "meta_details": meta,
        "qualifications": qualification
    }

    return data


if __name__ == "__main__":
    dataset = pq.ParquetDataset(urls_dataset_save_path, filters=[('site','=','dev.to')])
    df = dataset.read().to_pandas()


    data = []
    for u in df['url'].to_list():
        print(u)
        d = profile_crawler(u)
        today = datetime.today().date()
        today_string = today.strftime('%Y-%m-%d')
        d['date_added'] = today_string
        print(d)
        data.append(d)
        sleep(random.randint(6,10))

    result_df = pd.DataFrame(data)
    result_df.to_parquet('data/profiles/devto', partition_cols=['date_added'])
    