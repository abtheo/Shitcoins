from time import sleep
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os
import re
from bs4 import BeautifulSoup
import pandas as pd


# Initialise Chrome WebDriver
chrome_options = ChromeOptions()
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
chrome_driver = "./chromedriver_win.exe"

driver = webdriver.Chrome(options=chrome_options,
                          executable_path=chrome_driver)

# Launch driver at given token URL
url = 'https://bscscan.com/token/' + \
    '0xb27adaffb9fea1801459a1a81b17218288c097cc'
driver.get(url)

# Await page load by querying a specific element
max_delay = 10
try:
    myElem = WebDriverWait(driver, max_delay).until(
        EC.presence_of_element_located((By.ID, 'totaltxns')))
    print("Page is ready!")
except TimeoutException:
    print("Loading took too much time!")

# Extract number of token holders
transactions = driver.find_element_by_id("totaltxns").text
num_transactions = int(re.sub("[^0-9]", "", transactions))
print(f"Number of transactions: {num_transactions}")

# Extract number of token holders
holders = driver.find_element_by_class_name("mr-3").text
num_holders = int(re.sub("[^0-9]", "", holders))
print(f"Number of token holders: {num_holders}")

# Focus TX table
WebDriverWait(driver, 3).until(EC.frame_to_be_available_and_switch_to_it(
    (By.XPATH, "//*[@id='tokentxnsiframe']")))

# Select Last Page of TXs
driver.find_element_by_xpath(
    "//*[@id='maindiv']/div[1]/nav/ul/li[5]/a/span[1]").click()


# Parse raw HTML with BeautifulSoup
soup = BeautifulSoup(driver.page_source, features="html.parser")


# Scrape HTML table
Transfers_info_table_1 = soup.find(
    "table", {"class": "table table-md-text-normal table-hover mb-4"})
df = pd.read_html(str(Transfers_info_table_1))[0]
df.dropna(axis=1, how='all', inplace=True)
print(df)

# # data = []
# table = soup.find('table', attrs={'class': 'table'})
# print(table)
# table_body = table.find('tbody')

# rows = table_body.find_all('tr')
# for row in rows:
#     cols = row.find_all('td')
#     cols = [ele.text.strip() for ele in cols]
#     data.append([ele for ele in cols if ele])

# print(data)

# Download table data


sleep(5)
driver.close()
