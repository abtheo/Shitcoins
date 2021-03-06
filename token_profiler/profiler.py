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
from datetime import datetime

class Profiler:
    def __init__(self):
        self.chrome_options = ChromeOptions()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--window-size=1920x1080")
        self.chrome_options.add_argument("--log-level=3")

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

    def query_token_sniffer(self, address):
        #TODO: Refactor this to a simple HTTP request
        url = "https://tokensniffer.com/token/" + address
        self.driver.get(url)
        sleep(1)

        if "WARNING" in self.driver.page_source:
            return "SCAM"
        if "This page could not be found" in self.driver.page_source:
            return "404"
        return "OKAY"


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
            return {
                "sell_exists": False,
                "v1_lp_address": "",
                "v2_lp_address": "",
                "v1_bnb_holdings": 0,
                "v2_bnb_holdings": 0,
                "market_cap": "$0"
            }
        sleep(1)

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
        v1_bnb = float(re.sub("[^0-9.]", "", values[0].replace("V1","")))
        v2_bnb = float(re.sub("[^0-9.]", "", values[1].replace("V2","").split(":")[1]))

        market_cap = self.driver.find_element_by_xpath("//*[@id='root']/div/div[1]/div[2]/div/div[1]/div[2]/span[1]").text

        #Determine if any Sell transactions have taken place
        try:
            tx_table = self.driver.find_element_by_xpath(
                "//*[@id='root']/div/div[1]/div[2]/div/div[2]/div[2]/div/div[3]/div[1]/div/div[2]")
            sell_txs = bool(tx_table.text.count("Sell"))
        except:
            sell_txs = False

        return {
            "sell_exists": sell_txs,
            "v1_lp_address": v1_lp_address,
            "v2_lp_address": v2_lp_address,
            "v1_bnb_holdings": v1_bnb,
            "v2_bnb_holdings": v2_bnb,
            "market_cap": market_cap
        }

    def query_bscscan_token(self, address):
         # Direct driver to given token URL
        url = 'https://bscscan.com/token/' + address
        self.driver.get(url)
        # Await page load by querying a specific element
        max_delay = 25
        try:
            myElem = WebDriverWait(self.driver, max_delay).until(
                EC.presence_of_element_located((By.ID, 'totaltxns')))
        except TimeoutException:
            print("FAIL - Loading took too much time!")
            return {
            "num_transactions": 0,
            "num_holders" : 0,
            "age" : datetime.now(),
            "tx_df": pd.DataFrame(),
        }
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

        # Select Last Page of TXs (may not exist if 1 page only)
        try:
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='maindiv']/div[1]/nav/ul/li[5]/a/span[1]"))).click()
        except:
            pass
        # Parse raw HTML with BeautifulSoup
        soup = BeautifulSoup(self.driver.page_source, features="html.parser")

        # Scrape HTML table
        table_data = soup.find(
            "table", {"class": "table table-md-text-normal table-hover mb-4"})
        tx_df = pd.read_html(str(table_data))[0]
        tx_df.dropna(axis=1, how='all', inplace=True)

        #Get Age of token (first tx datetime)
        # print(df)
        tx_df["Date Time (UTC)"] = pd.to_datetime(tx_df["Date Time (UTC)"])
        earliest_tx = tx_df["Date Time (UTC)"].min()

        #TODO: Hunt for Whales
        #Switch to Holders table tab
        # self.driver.get(url+"#balances")

        # WebDriverWait(self.driver, 25).until(EC.frame_to_be_available_and_switch_to_it(
        #     (By.XPATH, "//*[@id='tokeholdersiframe']")))

        # WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH,"//*[@id='ContentPlaceHolder1_tabHolders']"))).click()

        # Focus Holders table
        # WebDriverWait(self.driver, 15).until(EC.frame_to_be_available_and_switch_to_it(
        #     (By.XPATH, "//*[@id='tokeholdersiframe']")))
        # sleep(5)

        # #Holy shit this is gross
        # #Find contract icon by <i> -> <span> -> <td> -> <tr> -> <td>rowKey</td>
        # icons = self.driver.find_elements_by_class_name("fa-file-alt")
        # icons = [i.find_element_by_xpath('..').find_element_by_xpath('..').find_element_by_xpath('..')
        #         .get_attribute('innerHTML')[:10] for i in icons]
        # #Then parse out the <td></td> HTML tags to get the row number
        # contract_rows = [int(re.sub("[^0-9]", "", i))-1 for i in icons]

        # # Parse raw HTML with BeautifulSoup
        # soup = BeautifulSoup(self.driver.page_source, features="html.parser")

        # # Scrape HTML table
        # table_data = soup.find(
        #     "table", {"class": "table table-md-text-normal table-hover"})
        # holders_df = pd.read_html(str(table_data))[0]
        # holders_df.dropna(axis=1, how='all', inplace=True)

        # # Boolean for IsContractAddress, indicated by the icon on BSCscan
        # holders_df["is_contract_address"] = False
        # holders_df.loc[contract_rows, "is_contract_address"] = True
        # "holders_df": holders_df

        return {
            "num_transactions": num_transactions,
            "num_holders" : num_holders,
            "age" : earliest_tx,
            "tx_df": tx_df,
        }

    def query_bscscan_liquidity_providers(self, url):
         # Direct driver to given LP URL
        self.driver.get(url)
        # Await page load by querying a specific element
        max_delay = 25
        try:
            myElem = WebDriverWait(self.driver, max_delay).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'mr-3')))
        except TimeoutException:
            return pd.DataFrame

        sleep(1)

        # Extract number of token holders
        holders = self.driver.find_element_by_class_name("mr-3").text
        num_lp_holders = int(re.sub("[^0-9]", "", holders))

        # Focus holders table
        WebDriverWait(self.driver, 15).until(EC.frame_to_be_available_and_switch_to_it(
            (By.XPATH, "//*[@id='tokeholdersiframe']")))
        sleep(1)

        #Holy shit this is gross
        #Find contract icon by <i> -> <span> -> <td> -> <tr> -> <td>rowKey</td>
        icons = self.driver.find_elements_by_class_name("fa-file-alt")
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
        # TODO: Exit early if no liquidity
        if poocoin_stats["v1_bnb_holdings"] < 1 and poocoin_stats["v2_bnb_holdings"] < 1:
            poocoin_stats["locked_liquidity"] = 0
            poocoin_stats["tx_df"] = pd.DataFrame()
            poocoin_stats["stats"] = { "age": pd.Timestamp.now()}
            poocoin_stats["token_sniffer"] = "404"

            return poocoin_stats

        #Query token on BSCScan
        bscscan_stats = self.query_bscscan_token(address)

        # Query Liquidity Provider holders on BSCScan
        # [Rank, Address, Quantity, Percentage, is_contract_address]
        v1_lp_holders = self.query_bscscan_liquidity_providers(poocoin_stats["v1_lp_address"])
        v2_lp_holders = self.query_bscscan_liquidity_providers(poocoin_stats["v2_lp_address"])

        def check_locked_liquidty(df, liquidity_value):
            if "There are no matching entries" == df["Percentage"].iloc[0]:
                return 0
            #Find real value of liquidty per address (in BNB)
            df["percent_float"] = df["Percentage"].apply(lambda x: float(''.join(i for i in x if i not in '%,'))/100)
            df = df[df["percent_float"] <= 100]
            df["bnb_value"] = df["percent_float"] * liquidity_value

            total_locked = 0
            # Check if liquidity is sufficient + locked
            dead_address = "0x000000000000000000000000000000000000dead"
            if dead_address in df["Address"]:
                total_locked += sum(df[df["Address"]==dead_address]["bnb_value"])

            # contract_addresses = df[df["is_contract_address"]==True]
            # total_locked += sum(contract_addresses["bnb_value"])

            return total_locked

        #Calculate locked liquidity
        total_locked = 0
        if not v1_lp_holders.empty:
            total_locked += check_locked_liquidty(v1_lp_holders, poocoin_stats["v1_bnb_holdings"])
        if not v2_lp_holders.empty:
            total_locked+= check_locked_liquidty(v2_lp_holders, poocoin_stats["v2_bnb_holdings"])

        # Return full dictionary
        profile = poocoin_stats
        profile['v1_lp_holders'] = v1_lp_holders
        profile['v2_lp_holders'] = v2_lp_holders
        profile['stats'] = bscscan_stats
        profile['token_sniffer'] = self.query_token_sniffer(address)
        profile['locked_liquidity'] = total_locked
        return profile

# if __name__ == "__main__":
#     with Profiler() as profiler:
#         address = "0x1a6c2c3c52cd3cc21db2b8f2b331ca9c4780f1ee"
#         profile = profiler.profile_token(address)
#         print(profile)
