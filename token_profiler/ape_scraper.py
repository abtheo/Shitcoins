import time
from time import sleep
from selenium import webdriver
import undetected_chromedriver as uc
from selenium.webdriver import ChromeOptions
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import os
import re
from bs4 import BeautifulSoup
import pandas as pd


class ApeScraper:
    def __init__(self, wait_for_table_load_now=True):
        self.chrome_options = ChromeOptions()
        # self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--enable-javascript")

        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.chrome_options.add_experimental_option('useAutomationExtension', False)
        self.chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        self.chrome_options.add_argument("user-data-dir={}".format(r"C:\Users\GE60 2PE\AppData\Local\Google\Chrome\User Data\Default"))
        # self.chrome_options.add_argument("--window-size=1920x1080")
        self.chrome_options.add_argument("--log-level=3")

        # Use the chrome driver in the same directory as this file, regardless
        # of what the current working directory is.
        filepath = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        self.chrome_driver = filepath + "/chromedriver_win.exe"

        self.driver = uc.Chrome(options=self.chrome_options)#executable_path=self.chrome_driver


        #Go to web page
        self.driver.get("https://poocoin.app/ape")
        
        max_delay = 25

        if wait_for_table_load_now:
            print("Waiting for Poocoin Ape table to catch up...")
            sleep(15)
        # token_type.send_keys(Keys.RETURN)
        try:
            #Select V2 tokens
            token_type = WebDriverWait(self.driver, max_delay).until(
                    EC.presence_of_element_located((By.XPATH, "//*[@id='root']/div/div/div[2]/label/select")))
            token_type.send_keys(Keys.DOWN)
            self.driver.find_element_by_xpath('//*[@id="root"]').click()
            myElem = WebDriverWait(self.driver, max_delay).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'table-responsive')))
        except TimeoutException:
            print("Loading took too much time!")
        

    """Dispose of the driver window correctly when code exits"""
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        self.driver.close()            

    def scrape_ape(self):
        # Parse raw HTML with BeautifulSoup
        soup = BeautifulSoup(self.driver.page_source, features="html.parser")
        urls = self.driver.find_elements_by_xpath('//a[contains(@href,"https://bscscan.com/address")]')
        # Scrape HTML table
        table_data = soup.find(
            "table", {"class": "table table-bordered table-sm text-small text-center"})
        
        df = pd.read_html(str(table_data))[0]
        df.dropna(axis=1, how='all', inplace=True)
        df["Age"] = df["Creation Time"].apply(lambda x: x[8:16])
        df["Creation Time"] = df["Creation Time"].apply(lambda x: x[:8])

        #Something weird happened, error
        if not len(urls) == len(df):
            return pd.DataFrame()

        #Find Contract URLS + addresses
        df["url"] = [elem.get_attribute('href') for elem in urls]
        df["address"] = df["url"].apply(lambda x: x[-47:-5])

        #If a duplicate name is found, drop both.
        #That's someone pumping out shitcoins programmatically, definite rug.
        df.drop_duplicates("Token", keep=False)
        return df

if __name__ == "__main__":
    ape_scraper = ApeScraper()
    while True:
        df = ape_scraper.scrape_ape()
        print(df)
        #Poocoin table goes back about an hour, but we need to query constantly
        sleep(120)
