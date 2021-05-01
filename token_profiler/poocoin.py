import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")

url = 'https://poocoin.app/tokens/' + \
    '0xb27adaffb9fea1801459a1a81b17218288c097cc'

chrome_driver = "./chromedriver.exe"

driver = webdriver.Chrome(chrome_options=chrome_options,
                          executable_path=chrome_driver)
driver.get(url)
time.sleep(5)
coinInfo = driver.find_element_by_class_name("px-3")
marketCap = coinInfo.text.split(":")
marketCap = marketCap[1]
print(coinInfo.text)
print(marketCap)
driver.close()
