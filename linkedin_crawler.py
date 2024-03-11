from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from config import urls_dataset_save_path
from time import sleep
from datetime import datetime
import random
from urls_crawler import scroll_down
from dotenv import find_dotenv, load_dotenv
_ = load_dotenv(find_dotenv())
import sys
import traceback


email = os.getenv('LINKEDIN_EMAIL')
password = os.getenv('LINKEDIN_PASSWORD')


def profile_crawler(url:str, driver):

    url = url.replace('vn.linkedin', 'linkedin')

    driver.get(url)
    sleep(2)

    user_name_xpath = "/html/body/div[5]/div[3]/div/div/div[2]/div/div/main/section[1]/div[2]/div[2]/div[1]/div[1]/span[1]"
    user_name = driver.find_element(By.XPATH, user_name_xpath).text

    headline_xpath = "/html/body/div[5]/div[3]/div/div/div[2]/div/div/main/section[1]/div[2]/div[2]/div[1]/div[2]"
    headline = driver.find_element(By.XPATH, headline_xpath).text

    location_xpath = "/html/body/div[5]/div[3]/div/div/div[2]/div/div/main/section[1]/div[2]/div[2]/div[2]/span[1]"
    location = driver.find_element(By.XPATH, location_xpath).text

    # main_xpath = "/html/body/div[5]/div[3]/div/div/div[2]/div/div/main"
    # main = driver.find_element(By.XPATH, main_xpath)

    contact_info_xpath = "/html/body/div[5]/div[3]/div/div/div[2]/div/div/main/section[1]/div[2]/div[2]/div[2]/span[2]/a"
    contact_info =  driver.find_element(By.XPATH, contact_info_xpath)
    contact_info.click()
    sleep(5)

    info_section_xpath = "/html/body/div[3]/div/div/div[2]/section/div"
    info_section = driver.find_element(By.XPATH, info_section_xpath)

    info = info_section.text.split("\n")
    keys = info[::2]
    values = info[1::2]

    info_data = {}
    for k, v in zip(keys, values):
        info_data[k] = v


    close_button_xpath = "/html/body/div[3]/div/div/button"
    close_button = driver.find_element(By.XPATH, close_button_xpath)
    close_button.click()
    sleep(3)

    about_xpath = "/html/body/div[5]/div[3]/div/div/div[2]/div/div/main/section[2]"
    try:
        about = driver.find_element(By.XPATH, about_xpath).text
    except:
        about = None

    if url.endswith("/") == False:
        print('add /')
        url=url+"/"
    driver.get(url + "details/skills")
    sleep(5)
    scroll_down(driver, 5)

    skills = []
    try:
        ul_xpath = "/html/body/div[5]/div[3]/div/div/div[2]/div/div/main/section/div[2]/div[2]/div/div/div[1]/ul"
        ul = driver.find_element(By.XPATH, ul_xpath)
        a_tags = ul.find_elements(By.XPATH, "//a[@data-field='skill_page_skill_topic']")
        for a in a_tags:
            t = a.text.split("\n")[0]
            skills.append(t)
    except:
        pass

    skills = list(set(skills))
    
    data = {
        "user_name": user_name,
        "work": headline,
        "headline": about,
        "location": location,
        "contact_info": info_data,
        "skills" : skills
    }
    return data


if __name__ == "__main__":

    dataset = pq.ParquetDataset(urls_dataset_save_path, filters=[('site','=', 'linkedin')])
    df = dataset.read().to_pandas()

    driver = webdriver.Chrome()
    driver.get('https://www.linkedin.com/')
    sleep(5)
    email_box_xpath = "//input[@id='session_key']"
    email_box = driver.find_element(By.XPATH, email_box_xpath)
    email_box.send_keys(email)

    password_box_xpath = "//input[@id='session_password']"
    password_box = driver.find_element(By.XPATH, password_box_xpath)
    password_box.send_keys(password)
    password_box.send_keys(Keys.ENTER)
    sleep(5)

    driver.maximize_window()

    urls = df['url'].to_list()[0:10]

    data = []
    for u in urls:
        print(u)
        try:
            d = profile_crawler(u, driver)
        except:
            result_df = pd.DataFrame(data)
            result_df.to_parquet('data/profiles/linkedin', partition_cols=['date_added'])
            print(traceback.format_exc())
            sys.exit()

        today = datetime.today().date()
        today_string = today.strftime('%Y-%m-%d')
        d['date_added'] = today_string
        data.append(d)
        print(d)
        sleep(random.randint(6,10))


    result_df = pd.DataFrame(data)
    result_df.to_parquet('data/profiles/linkedin', partition_cols=['date_added'])
    

    # url = "https://in.linkedin.com/in/ht-lm-and-python-devi-01668a293"
    # print(profile_crawler(url, driver))