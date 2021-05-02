import time
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


class Profiler:
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

    """Dispose of the driver window correctly when code exits"""
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        self.driver.close()

    def query_poocoin(self,address):
        #Direct driver to Poocoin URL
        url = 'https://poocoin.app/tokens/' + address
        self.driver.get(url)
        # Await page load by querying a specific element
        max_delay = 10
        try:
            myElem = WebDriverWait(self.driver, max_delay).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'px-3')))
        except TimeoutException:
            print("Loading took too much time!")
        sleep(2)

        #Get links to BSCScan for Liquidity Providers
        v1_lp_address = self.driver.find_element_by_xpath(
            "//*[@id='root']/div/div[1]/div[2]/div/div[1]/div[2]/small/a[2]"
        ).get_attribute('href')

        v2_lp_address = self.driver.find_element_by_xpath(
            "//*[@id='root']/div/div[1]/div[2]/div/div[1]/div[2]/small/a[4]"
        ).get_attribute('href')

        #Disgustingly parse out the BNB holdings in V1 and V2 LPs
        bnb_lp_values = self.driver.find_element_by_xpath("//*[@id='root']/div/div[1]/div[2]/div/div[1]/div[2]/small").text
        values = bnb_lp_values.split('BNB')
        v1_bnb = float(re.sub("[^0-9.]", "", values[0]))
        v2_bnb = float(re.sub("[^0-9.]", "", values[1].split(":")[1]))

        #Determine if any Sell transactions have taken place
        tx_table = self.driver.find_element_by_xpath(
            "//*[@id='root']/div/div[1]/div[2]/div/div[2]/div[2]/div/div[3]/div[1]/div/div[2]")
        sell_txs = tx_table.text.count("Sell")

        return {
            "sell_exists": bool(sell_txs),
            "v1_lp_address": v1_lp_address,
            "v2_lp_address": v2_lp_address,
            "v1_bnb_holdings": v1_bnb,
            "v2_bnb_holdings": v2_bnb
        }

    def query_bscscan_token(self, address):
         # Direct driver to given token URL
        url = 'https://bscscan.com/token/' + address
        self.driver.get(url)
        # Await page load by querying a specific element
        max_delay = 10
        try:
            myElem = WebDriverWait(self.driver, max_delay).until(
                EC.presence_of_element_located((By.ID, 'totaltxns')))
        except TimeoutException:
            print("FAIL - Loading took too much time!")

        sleep(0.5)
        # Extract total number of transactions
        transactions = self.driver.find_element_by_id("totaltxns").text
        num_transactions = int(re.sub("[^0-9]", "", transactions))

        # Extract number of token holders
        holders = self.driver.find_element_by_class_name("mr-3").text
        num_holders = int(re.sub("[^0-9]", "", holders))

        # Focus TX table
        WebDriverWait(self.driver, 15).until(EC.frame_to_be_available_and_switch_to_it(
            (By.XPATH, "//*[@id='tokentxnsiframe']")))

        age_col = self.driver.find_element_by_xpath("//*[@id='lnkTokenTxnsAgeDateTime']").text
        if age_col == "Age":
            # Switch DateTime format
            age_elem = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='lnkTokenTxnsAgeDateTime']"))).click()

        # Select Last Page of TXs
        self.driver.find_element_by_xpath(
            "//*[@id='maindiv']/div[1]/nav/ul/li[5]/a/span[1]").click()

        # Parse raw HTML with BeautifulSoup
        soup = BeautifulSoup(self.driver.page_source, features="html.parser")

        # Scrape HTML table
        table_data = soup.find(
            "table", {"class": "table table-md-text-normal table-hover mb-4"})
        df = pd.read_html(str(table_data))[0]
        df.dropna(axis=1, how='all', inplace=True)

        #Get Age of token (first tx datetime)
        # print(df)
        df["Date Time (UTC)"] = pd.to_datetime(df["Date Time (UTC)"])
        earliest_tx = df["Date Time (UTC)"].min()

        #TODO: Hunt for Whales

        return {
            "num_transactions": num_transactions,
            "num_holders" : num_holders,
            "age" : earliest_tx
        }

    def query_bscscan_liquidity_providers(self, url):
         # Direct driver to given LP URL
        self.driver.get(url)
        # Await page load by querying a specific element
        max_delay = 10
        try:
            myElem = WebDriverWait(self.driver, max_delay).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'mr-3')))
        except TimeoutException:
            print("FAIL - Loading took too much time!")

        sleep(0.5)

        # Extract number of token holders
        holders = self.driver.find_element_by_class_name("mr-3").text
        num_lp_holders = int(re.sub("[^0-9]", "", holders))

        # Focus holders table
        WebDriverWait(self.driver, 5).until(EC.frame_to_be_available_and_switch_to_it(
            (By.XPATH, "//*[@id='tokeholdersiframe']")))
        sleep(1)

        icons = self.driver.find_elements_by_class_name("fa-file-alt")

        #Holy shit this is gross
        #Find contract icon by <i> -> <span> -> <td> -> <tr> -> <td>rowKey</td>
        icons = [i.find_element_by_xpath('..').find_element_by_xpath('..').find_element_by_xpath('..')
                .get_attribute('innerHTML')[:10] for i in icons]
        #Then parse out the <td></td> HTML tags to get the row number
        contract_rows = [int(re.sub("[^0-9]", "", i))-1 for i in icons]

        # Parse raw HTML with BeautifulSoup
        soup = BeautifulSoup(self.driver.page_source, features="html.parser")

        # Scrape HTML table
        table_data = soup.find(
            "table", {"class": "table table-md-text-normal table-hover"})
        df = pd.read_html(str(table_data))[0]
        df.dropna(axis=1, how='all', inplace=True)

        # Boolean for IsContractAddress, indicated by the icon on BSCscan
        df["is_contract_address"] = False
        df.loc[contract_rows, "is_contract_address"] = True

        #Stick on the number of holders lol
        df["num_lp_holders"] = num_lp_holders

        return df

    def profile_token(self, address):
        #Start by querying Poocoin to get BSCScan LP links
        poocoin_stats = self.query_poocoin(address)

        #Query token on BSCScan
        bscscan_stats = self.query_bscscan_token(address)

        # [Rank, Address, Quantity, Percentage, is_contract_address]
        v1_lp_holders = self.query_bscscan_liquidity_providers(poocoin_stats["v1_lp_address"])
        v2_lp_holders = self.query_bscscan_liquidity_providers(poocoin_stats["v2_lp_address"])

        # Check if liquidity is sufficient + locked
        dead_address = "0x000000000000000000000000000000000000dead"

        # Return full dictionary
        profile = poocoin_stats
        profile.update(v1_lp_holders)
        profile.update(v2_lp_holders)
        profile['stats'] = bscscan_stats
        return profile

if __name__ == "__main__":
    with Profiler() as profiler:
        address = "0x5bf5a3c97dd86064a6b97432b04ddb5ffcf98331"
        print(profiler.profile_token(address))
