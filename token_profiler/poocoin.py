import time
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os


def query_poocoin(address):
    chrome_options = ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")

    url = 'https://poocoin.app/tokens/' + address

    chrome_driver = "token_profiler/chromedriver_win.exe"

    driver = webdriver.Chrome(options=chrome_options,
                              executable_path=chrome_driver)
    driver.get(url)
    # Await page load by querying a specific element
    max_delay = 10
    try:
        myElem = WebDriverWait(driver, max_delay).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'px-3')))
        print("Page is ready!")
    except TimeoutException:
        print("Loading took too much time!")

    v1_lp_holders = driver.find_element_by_xpath(
        "//*[@id='root']/div/div[1]/div[2]/div/div[1]/div[2]/small/a[2]").get_attribute('href')

    v2_lp_holders = driver.find_element_by_xpath(
        "//*[@id='root']/div/div[1]/div[2]/div/div[1]/div[2]/small/a[4]"
    ).get_attribute('href')

    tx_table = driver.find_element_by_xpath(
        "//*[@id='root']/div/div[1]/div[2]/div/div[2]/div[2]/div/div[3]/div[1]/div/div[2]")

    sell_txs = tx_table.text.count("Sell")

    driver.close()

    return {
        "sell": bool(sell_txs),
        "v1_lp_address": v1_lp_holders,
        "v2_lp_address": v2_lp_holders
    }
