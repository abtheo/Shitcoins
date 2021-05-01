import time
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os

chrome_options = ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")

url = 'https://poocoin.app/tokens/' + \
    '0xb27adaffb9fea1801459a1a81b17218288c097cc'

chrome_driver = "./chromedriver_win.exe"

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

# coinInfo = driver.find_element_by_class_name("px-3").get_attribute('href')
v1_lp_holders = driver.find_element_by_xpath(
    "//*[@id='root']/div/div[1]/div[2]/div/div[1]/div[2]/small/a[2]")

v2_lp_holders = driver.find_element_by_xpath(

)

print(dir(coinInfo))

# marketCap = coinInfo.text.split(":")
# marketCap = marketCap[1]
# print(coinInfo.text)
# print(marketCap)
driver.close()
