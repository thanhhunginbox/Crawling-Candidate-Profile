from time import sleep
import random
from selenium.webdriver.common.by import By


def scroll_down(driver, n=10):
    """
    Scroll to the end of the page n times
    """
    count = 0
    while count < n:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(random.randint(6, 10))
        count +=1

def scroll_down_and_click(driver, click_element_xpath, n=0):
    """
    Scroll to the end of the page and click see more result n times
    """
    count = 0
    while count <= n:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        try:
            # see_more_xpath = "/html/body/div[5]/div/div[12]/div/div[4]/div/div[3]/div[4]/a[1]/h3/div"
            see_more_xpath = click_element_xpath
            see_more = driver.find_element(By.XPATH, see_more_xpath)
            see_more.click()
            sleep(random.randint(6, 10))
        except:
            break
        if n > 0:
            count += 1