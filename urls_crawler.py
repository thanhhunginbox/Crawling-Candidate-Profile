import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from time import sleep
import random
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from datetime import datetime
from utils.selenium_driver import scroll_down, scroll_down_and_click
from utils.URL import preprocess_url


if __name__ == "__main__":
    if len(sys.argv) > 2:
        search_key_word = sys.argv[1]
        site = sys.argv[2]
        save_path = sys.argv[3]
    else:
        print("Missing search key or save path.")
        sys.exit()

    driver = webdriver.Chrome()

    driver.get("https://www.google.com/")
    sleep(random.randint(6, 10))

    search_box_xpath = "/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[2]/textarea"
    search_box = driver.find_element(By.XPATH, search_box_xpath)
    search_box.send_keys(search_key_word)
    search_box.send_keys(Keys.ENTER)
    sleep(random.randint(6, 10))

    scroll_down(driver, n=10)
    see_more_xpath = "/html/body/div[5]/div/div[12]/div/div[4]/div/div[3]/div[4]/a[1]/h3/div"
    scroll_down_and_click(driver, see_more_xpath)

    result_content_xpath = "//div[@id='search']"
    result_search_content = driver.find_element(By.XPATH, result_content_xpath)

    # get html source of the result
    result_content_html = result_search_content.get_attribute('innerHTML')
    soup = BeautifulSoup(result_content_html, 'html.parser')

    a_tags = soup.find_all('a', recursive=True)

    def url_validate(url):
        if "translate.google.com" in url:
            return False
        if url.startswith("/search?"):
            return False
        return True

    profile_urls = [a.get('href') for a in a_tags]
    profile_urls = [u for u in profile_urls if url_validate(u) == True]
    profile_urls = [preprocess_url(u, site) for u in profile_urls]


    df = pd.DataFrame()
    df['url'] = profile_urls
    today = datetime.today().date()
    today_string = today.strftime('%Y-%m-%d')
    df['date_string'] = [today_string]*df.shape[0]
    df['site'] = [site]*df.shape[0]
    table = pa.Table.from_pandas(df)
    pq.write_to_dataset(table, root_path=save_path, partition_cols=['date_string', 'site'])




    