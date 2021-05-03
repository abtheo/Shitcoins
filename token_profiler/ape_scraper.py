import time
from time import sleep
from selenium import webdriver
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
    def __init__(self):
        self.chrome_options = ChromeOptions()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--window-size=1920x1080")

        # Use the chrome driver in the same directory as this file, regardless
        # of what the current working directory is.
        filepath = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        self.chrome_driver = filepath + "/chromedriver_win.exe"

        self.driver = webdriver.Chrome(options=self.chrome_options,
                                executable_path=self.chrome_driver)

        #Go to web page
        self.driver.get("https://poocoin.app/ape")
        
        max_delay = 10

        #Select V2 tokens
        token_type = WebDriverWait(self.driver, max_delay).until(
                EC.presence_of_element_located((By.XPATH, "//*[@id='root']/div/div/div[2]/label/select")))
        token_type.send_keys(Keys.DOWN)
        self.driver.find_element_by_xpath('//*[@id="root"]').click()
        # token_type.send_keys(Keys.RETURN)
        try:
            myElem = WebDriverWait(self.driver, max_delay).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'table-responsive')))
        except TimeoutException:
            print("Loading took too much time!")
        print("Waiting for Poocoin Ape table to catch up...")
        sleep(15)

    """Dispose of the driver window correctly when code exits"""
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        self.driver.close()            

    def scrape_ape(self):
        # Parse raw HTML with BeautifulSoup
        soup = BeautifulSoup(self.driver.page_source, features="html.parser")
        # Scrape HTML table
        table_data = soup.find(
            "table", {"class": "table table-bordered table-sm text-small text-center"})
        df = pd.read_html(str(table_data))[0]
        df.dropna(axis=1, how='all', inplace=True)
        df["Age"] = df["Creation Time"].apply(lambda x: x[8:16])
        df["Creation Time"] = df["Creation Time"].apply(lambda x: x[:8])

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
        sleep(10)